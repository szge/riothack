import os
import asyncio
import tempfile
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum
from datetime import datetime
import uuid
import json

from yt_dlp import YoutubeDL
from dotenv import load_dotenv
from openai import OpenAI
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


class VideoTranscriber:
    def __init__(
        self,
        max_concurrent_jobs: int = 3,
        max_retries: int = 2,
        cleanup_files: bool = True
    ):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=self.openai_api_key)

        self.s3_bucket = os.getenv('AWS_S3_BUCKET')
        self.aws_region = os.getenv('AWS_REGION', 'us-west-2')
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

        if self.s3_bucket and self.aws_access_key_id and self.aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                region_name=self.aws_region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
        else:
            self.s3_client = None
            print(
                "Warning: AWS S3 credentials not fully configured. S3 upload will be skipped.")

        self.max_concurrent_jobs = max_concurrent_jobs
        self.max_retries = max_retries
        self.cleanup_files = cleanup_files
        self.temp_dir = tempfile.gettempdir()
        self._semaphore = asyncio.Semaphore(max_concurrent_jobs)
        self._jobs: Dict[str, TranscriptionJob] = {}

    def _generate_job_id(self) -> str:
        """Generate unique job ID"""
        return str(uuid.uuid4())

    async def transcribe_videos(self, video_urls: List[str]) -> List[TranscriptionJob]:
        """Main entry point for transcribing multiple videos."""
        jobs = []
        tasks = []

        for url in video_urls:
            job = TranscriptionJob(
                url=url,
                job_id=self._generate_job_id(),
                created_at=datetime.now()
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

            # Transcribe
            job.status = ProcessingStage.TRANSCRIBING
            transcription_result = await self._transcribe_audio(audio_path)
            job.transcription = transcription_result
            print(transcription_result)

            # Summarize
            # job.status = ProcessingStage.SUMMARIZING
            # job.summary = await self._summarize_text(job.transcription)

            # Upload to S3
            # if self.s3_client:
            #     job.status = ProcessingStage.UPLOADING
            #     await self._upload_to_s3(job)

            job.completed_at = datetime.now()
            job.status = ProcessingStage.COMPLETED

        except Exception as e:
            job.error = str(e)
            job.status = ProcessingStage.FAILED
            print(f"Error processing {job.url}: {e}")
        finally:
            # Cleanup temporary files
            if self.cleanup_files and job.audio_file_path and os.path.exists(job.audio_file_path):
                try:
                    os.remove(job.audio_file_path)
                except Exception as e:
                    print(f"Error cleaning up file {job.audio_file_path}: {e}")

    async def _download_audio(self, url: str) -> tuple[str, dict]:
        """Download audio from video URL using yt-dlp"""
        loop = asyncio.get_event_loop()

        def download():
            with YoutubeDL({
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.temp_dir, '%(id)s.%(ext)s'),
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

                # Find the output file (should be mp3 after post-processing)
                audio_file = os.path.join(self.temp_dir, f"{video_id}.mp3")

                if not os.path.exists(audio_file):
                    raise FileNotFoundError(
                        f"Downloaded audio file not found for video {video_id}")

                return audio_file, info

        # Run in executor to avoid blocking
        audio_file, info = await loop.run_in_executor(None, download)
        return audio_file, info

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

    async def _upload_to_s3(self, job: TranscriptionJob):
        """Upload transcription data to S3"""
        if not self.s3_client:
            return

        loop = asyncio.get_event_loop()

        def upload():
            # Prepare data for upload
            data = {
                'job_id': job.job_id,
                'url': job.url,
                'title': job.title,
                'transcription': job.transcription,
                'summary': job.summary,
                'created_at': job.created_at.isoformat(),
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'processing_time_seconds': (job.completed_at - job.created_at).total_seconds() if job.completed_at else None
            }

            # Create S3 key using video title and job ID
            safe_title = "".join(c for c in job.title if c.isalnum() or c in (
                ' ', '-', '_')).rstrip()[:50]
            timestamp = job.created_at.strftime('%Y%m%d_%H%M%S')
            s3_key = f"transcriptions/{timestamp}_{safe_title}_{job.job_id[:8]}.json"

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=json.dumps(data, indent=2, ensure_ascii=False),
                ContentType='application/json',
                Metadata={
                    'video_url': job.url[:255],  # S3 metadata has size limits
                    'job_id': job.job_id,
                }
            )

            job.metadata['s3_key'] = s3_key
            job.metadata['s3_bucket'] = self.s3_bucket

        await loop.run_in_executor(None, upload)

    def get_job(self, job_id: str) -> Optional[TranscriptionJob]:
        """Get status of a specific job"""
        return self._jobs.get(job_id)

    def get_all_jobs(self) -> List[TranscriptionJob]:
        """Get all jobs"""
        return list(self._jobs.values())

    def get_jobs_by_status(self, status: ProcessingStage) -> List[TranscriptionJob]:
        """Get all jobs with a specific status"""
        return [job for job in self._jobs.values() if job.status == status]


async def main():
    transcriber = VideoTranscriber(
        max_concurrent_jobs=2,
        cleanup_files=True
    )

    urls = [
        'https://www.youtube.com/watch?v=qf27qzFKv60',
    ]

    print("🚀 Starting video transcription...")
    print(f"📹 Processing {len(urls)} video(s)\n")

    jobs = await transcriber.transcribe_videos(urls)

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
        # if 's3_key' in job.metadata:
        #     print(f"   S3 Location: s3://{job.metadata.get('s3_bucket')}/{job.metadata['s3_key']}")

    for job in failed_jobs:
        print(f"\n❌ Failed: {job.url}")
        print(f"   Error: {job.error}")


if __name__ == "__main__":
    asyncio.run(main())
