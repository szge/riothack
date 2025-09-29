import os
import asyncio
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum
from datetime import datetime
import uuid

from yt_dlp import YoutubeDL
from dotenv import load_dotenv
from openai import OpenAI
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

load_dotenv()


class ProcessingStage(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    SUMMARIZING = "summarizing"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TranscriptionJob:
    """Represents a single video transcription job"""
    url: str
    job_id: str
    title: Optional[str] = None
    status: ProcessingStage = ProcessingStage.PENDING
    transcription: Optional[str] = None
    summary: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    audio_file_path: Optional[str] = None
    tags: List[str] = field(default_factory=list)


class VideoTranscriber:
    def __init__(
        self,
        max_concurrent_jobs: int = 3,
        max_retries: int = 2,
        cleanup_files: bool = True,
        audio_output_dir: Optional[str] = os.path.join(
            os.getcwd(), "downloaded_audios"),
        opensearch_index: str = "video-transcriptions"
    ):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=self.openai_api_key)

        # OpenSearch configuration
        self.opensearch_endpoint = os.getenv('AWS_OPENSEARCH_ENDPOINT')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.opensearch_index = opensearch_index

        if self.opensearch_endpoint and self.aws_access_key_id and self.aws_secret_access_key:
            # Remove https:// prefix if present
            host = self.opensearch_endpoint.replace('https://', '').replace('http://', '')
            
            # Create AWS4Auth instance
            credentials = boto3.Session().get_credentials()
            awsauth = AWS4Auth(
                self.aws_access_key_id,
                self.aws_secret_access_key,
                self.aws_region,
                'es',
                session_token=credentials.token if credentials else None
            )
            
            self.opensearch_client = OpenSearch(
                hosts=[{'host': host, 'port': 443}],
                http_auth=awsauth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
                pool_maxsize=20
            )
        else:
            self.opensearch_client = None
            print("Warning: OpenSearch credentials not fully configured; upload will skip.")

        self.max_concurrent_jobs = max_concurrent_jobs
        self.max_retries = max_retries
        self.cleanup_files = cleanup_files
        self.audio_output_dir = audio_output_dir
        os.makedirs(self.audio_output_dir, exist_ok=True)
        self._semaphore = asyncio.Semaphore(max_concurrent_jobs)
        self._jobs: Dict[str, TranscriptionJob] = {}

    def _generate_job_id(self) -> str:
        """Generate unique job ID"""
        return str(uuid.uuid4())

    async def transcribe_videos(self, video_urls: List[str], tags: List[str] = None) -> List[TranscriptionJob]:
        """Main entry point for transcribing multiple videos."""
        jobs = []
        tasks = []

        for url in video_urls:
            job = TranscriptionJob(
                url=url,
                job_id=self._generate_job_id(),
                created_at=datetime.now(),
                tags=tags if tags else []
            )
            self._jobs[job.job_id] = job
            jobs.append(job)

            task = asyncio.create_task(
                self._process_video_with_semaphore(job)
            )
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

        return jobs

    async def _process_video_with_semaphore(self, job: TranscriptionJob):
        async with self._semaphore:
            await self._process_video(job)

    async def _process_video(self, job: TranscriptionJob):
        """Process a single video through all stages"""
        try:
            job.status = ProcessingStage.DOWNLOADING
            audio_path, video_info = await self._download_audio(job.url)
            job.audio_file_path = audio_path
            job.title = video_info.get('title', 'Untitled')

            print(f"Audio saved to: {audio_path}")

            # Transcribe
            job.status = ProcessingStage.TRANSCRIBING
            transcription_result = await self._transcribe_audio(audio_path)
            job.transcription = transcription_result

            # Summarize (optional - uncomment if needed)
            # job.status = ProcessingStage.SUMMARIZING
            # job.summary = await self._summarize_text(job.transcription)

            # Upload to OpenSearch
            if self.opensearch_client:
                job.status = ProcessingStage.UPLOADING
                await self._upload_to_opensearch(job)

            job.completed_at = datetime.now()
            job.status = ProcessingStage.COMPLETED

        except Exception as e:
            job.error = str(e)
            job.status = ProcessingStage.FAILED
            print(f"Error processing {job.url}: {e}")
        finally:
            if self.cleanup_files and job.audio_file_path and os.path.exists(job.audio_file_path):
                try:
                    os.remove(job.audio_file_path)
                    print(f"Removed audio file: {job.audio_file_path}")
                except Exception as e:
                    print(f"Error cleaning up file {job.audio_file_path}: {e}")

    async def _download_audio(self, url: str) -> tuple[str, dict]:
        """Download audio from video URL using yt-dlp and save to output dir with optional processing"""
        loop = asyncio.get_event_loop()

        def download():
            with YoutubeDL({
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.audio_output_dir, '%(id)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }) as ydl:
                info = ydl.extract_info(url, download=False)
                video_id = info['id']

                ydl.download([url])

                initial_audio_file = os.path.join(
                    self.audio_output_dir, f"{video_id}.mp3")

                if not os.path.exists(initial_audio_file):
                    raise FileNotFoundError(
                        f"Downloaded audio file not found for video {video_id}")

                processed_audio_file = self._preprocess_audio(
                    initial_audio_file, video_id)

                # Remove the original file and use the processed one
                if processed_audio_file != initial_audio_file:
                    try:
                        os.remove(initial_audio_file)
                    except Exception as e:
                        print(
                            f"Warning: Could not remove original audio file {initial_audio_file}: {e}")

                return processed_audio_file, info

        # Run in executor to avoid blocking
        audio_file, info = await loop.run_in_executor(None, download)
        return audio_file, info

    def _preprocess_audio(
        self,
        input_file: str,
        video_id: str,
        remove_silence: bool = True,
        speed_multiplier: float = 1.5,
        silence_threshold: str = "-50dB"
    ) -> str:
        """Process audio file to remove silence and/or adjust speed using ffmpeg"""
        import subprocess

        output_file = os.path.join(
            self.audio_output_dir, f"{video_id}_processed.mp3")

        filters = []

        if remove_silence:
            # Remove silence at start and end, with configurable threshold
            silence_filter = (
                f"silenceremove=start_periods=1:start_duration=0:start_threshold={silence_threshold}:"
                f"stop_periods=-1:stop_duration=0.02:stop_threshold={silence_threshold},"
                f"apad=pad_dur=0.02"
            )
            filters.append(silence_filter)

        if speed_multiplier != 1.0:
            # Speed up audio - ffmpeg's atempo filter works best with values between 0.5-2.0
            # For values > 2.0, we need to chain multiple atempo filters
            speed = speed_multiplier
            if speed > 2.0:
                # Chain multiple atempo filters for speeds > 2x
                while speed > 2.0:
                    filters.append("atempo=2.0")
                    speed /= 2.0
                if speed > 1.0:
                    filters.append(f"atempo={speed:.2f}")
            elif speed < 0.5:
                # Chain multiple atempo filters for very slow speeds
                while speed < 0.5:
                    filters.append("atempo=0.5")
                    speed *= 2.0
                if speed < 1.0:
                    filters.append(f"atempo={speed:.2f}")
            else:
                filters.append(f"atempo={speed:.2f}")

        filter_string = ",".join(filters) if filters else None

        cmd = [
            'ffmpeg', '-i', input_file,
            '-y',  # Overwrite output file
            '-ac', '1',  # Mono audio for smaller file size
            '-b:a', '64k'  # Lower bitrate for faster processing
        ]

        if filter_string:
            cmd.extend(['-af', filter_string])

        cmd.append(output_file)

        try:
            # print(f"Processing audio with filters: {filter_string}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True)
            # print(f"Audio processing completed: {output_file}")
            return output_file
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg processing failed: {e.stderr}")
            print(f"Falling back to original file: {input_file}")
            return input_file
        except FileNotFoundError:
            print(
                "FFmpeg not found. Please install FFmpeg to use audio processing features.")
            print(f"Falling back to original file: {input_file}")
            return input_file

    async def _transcribe_audio(self, audio_path: str) -> str:
        loop = asyncio.get_event_loop()

        def transcribe():
            with open(audio_path, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",
                    file=audio_file,
                    response_format="json",
                    language="en"
                )
                print(
                    f"Input tokens: {response.usage.input_tokens}, output tokens: {response.usage.output_tokens}")
                return response.text

        result = await loop.run_in_executor(None, transcribe)
        return result

    async def _summarize_text(self, text: str, max_length: int = 500) -> str:
        """
        Summarize transcription using OpenAI GPT

        Args:
            text: The transcription text to summarize
            max_length: Maximum length of summary in tokens

        Returns:
            Summary text
        """
        loop = asyncio.get_event_loop()

        def summarize():
            # Truncate input if too long (to manage token limits)
            max_input_chars = 12000  # Approximate safe limit for context
            truncated_text = text[:max_input_chars] if len(
                text) > max_input_chars else text

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates concise, informative summaries of video transcripts. Focus on the main topics, key points, and important details."
                    },
                    {
                        "role": "user",
                        "content": f"Please provide a comprehensive summary of the following video transcript. Include the main topics discussed, key points, and any important conclusions or takeaways:\n\n{truncated_text}"
                    }
                ],
                max_tokens=max_length
            )
            return response.choices[0].message.content

        # Run in executor to avoid blocking
        summary = await loop.run_in_executor(None, summarize)
        return summary

    async def _upload_to_opensearch(self, job: TranscriptionJob):
        """Upload transcription data to OpenSearch"""
        if not self.opensearch_client:
            return

        loop = asyncio.get_event_loop()

        def upload():
            document = {
                'job_id': job.job_id,
                'url': job.url,
                'title': job.title,
                'transcription': job.transcription,
                'summary': job.summary,
                'tags': job.tags,
                'created_at': job.created_at.isoformat(),
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'processing_time_seconds': (job.completed_at - job.created_at).total_seconds() if job.completed_at else None,
                'status': job.status.value
            }

            response = self.opensearch_client.index(
                index=self.opensearch_index,
                id=job.job_id,
                body=document,
                refresh=True
            )
            
            print(f"Uploaded to OpenSearch: {response['_id']}")

        await loop.run_in_executor(None, upload)

    async def add_tags_to_job(self, job_id: str, tags: List[str]):
        """Add tags to an existing job in OpenSearch"""
        if not self.opensearch_client:
            return

        loop = asyncio.get_event_loop()

        def update_tags():
            self.opensearch_client.update(
                index=self.opensearch_index,
                id=job_id,
                body={
                    "doc": {
                        "tags": tags
                    }
                }
            )

        await loop.run_in_executor(None, update_tags)


async def main():
    transcriber = VideoTranscriber(
        max_concurrent_jobs=2,
        cleanup_files=False,
        audio_output_dir=os.path.join(os.getcwd(), "downloaded_audios"),
        opensearch_index="video-transcriptions"
    )

    urls = [
        'https://www.youtube.com/watch?v=qf27qzFKv60',
    ]

    # tags = ["tutorial", "python", "programming"]
    tags = None

    print("🚀 Starting video transcription...")
    print(f"📹 Processing {len(urls)} video(s)\n")

    jobs = await transcriber.transcribe_videos(urls, tags=tags)

    print("\n" + "="*60)
    print("📊 TRANSCRIPTION SUMMARY")
    print("="*60)

    successful_jobs = [j for j in jobs if j.status ==
                       ProcessingStage.COMPLETED]
    failed_jobs = [j for j in jobs if j.status == ProcessingStage.FAILED]

    print(f"\n✅ Successful: {len(successful_jobs)}/{len(jobs)}")
    print(f"❌ Failed: {len(failed_jobs)}/{len(jobs)}")

    for job in successful_jobs:
        processing_time = (job.completed_at - job.created_at).total_seconds()
        print(f"\n📹 {job.title}")
        print(f"   Job ID: {job.job_id}")
        print(f"   Processing time: {processing_time:.1f}s")
        print(f"   Indexed in OpenSearch: {transcriber.opensearch_index}")
        if job.tags:
            print(f"   Tags: {', '.join(job.tags)}")

    for job in failed_jobs:
        print(f"\n❌ Failed: {job.url}")
        print(f"   Error: {job.error}")


if __name__ == "__main__":
    asyncio.run(main())