from dotenv import load_dotenv
import os
import json
import asyncio
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import Dict, List
import time

# https://platform.openai.com/docs/guides/structured-outputs

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

MAX_CONCURRENT_REQUESTS = 5

CATEGORIES = {
    "learning_curve_and_complexity": {
        "learning_champions": "Learning abilities and mechanics for 160+ champions",
        "understanding_systems": "Understanding complex game systems (items, runes, macro strategy)",
        "steep_curve": "The steep learning curve that takes months to even grasp basics",
        "bad_tutorial": "No adequate tutorial system to teach essential concepts",
        "mechanics_difficult": "Difficulty with basic mechanics like last-hitting minions",
    },
    "hostile_community_environment": {
        "flamed_for_mistakes": "Players are 'flamed' and insulted for making mistakes",
        "toxic_teammates": "Toxic behavior from teammates who expect perfection immediately",
    },
    "matchmaking_issues": {
        "smurfs": "New players often encounter smurfs (experienced players on new accounts) who dominate matches",
        "unfair_matchmaking": "New players matched against much more experienced opponents",
        "long_queue": "Long queue times that can discourage continued play",
        "long_matches": "Individual matches lasting 30-45+ minutes",
    },
    "time_investment_requirements": {
        "slow_progress": "Difficulty progressing without substantial time investment",
    },
    "technical_and_interface_issues": {
        "bad_ui": "Unintuitive camera controls and UI elements",
        "client_bugs": "Client stability problems and bugs",
    }
}


class LearningCurveAndComplexity(BaseModel):
    learning_champions: bool = False
    understanding_systems: bool = False
    steep_curve: bool = False
    bad_tutorial: bool = False
    mechanics_difficult: bool = False


class HostileCommunityEnvironment(BaseModel):
    flamed_for_mistakes: bool = False
    toxic_teammates: bool = False


class MatchmakingIssues(BaseModel):
    smurfs: bool = False
    unfair_matchmaking: bool = False
    long_queue: bool = False
    long_matches: bool = False


class TimeInvestmentRequirements(BaseModel):
    slow_progress: bool = False


class TechnicalAndInterfaceIssues(BaseModel):
    bad_ui: bool = False
    client_bugs: bool = False


class ReviewCategories(BaseModel):
    learning_curve_and_complexity: LearningCurveAndComplexity
    hostile_community_environment: HostileCommunityEnvironment
    matchmaking_issues: MatchmakingIssues
    time_investment_requirements: TimeInvestmentRequirements
    technical_and_interface_issues: TechnicalAndInterfaceIssues


async def categorize_review(review: str, review_index: int) -> Dict:
    """
    Use OpenAI API to categorize a review into zero or more complaint categories.
    """
    prompt = "You are an expert at analyzing player reviews for video games. Given the following review, categorize it into the appropriate complaint categories. Return a structured JSON response.\n\nCategories:\n\n"

    for major_category, subcategories in CATEGORIES.items():
        prompt += f"{major_category.replace('_', ' ').title()}:\n"
        for key, desc in subcategories.items():
            prompt += f"  - {key}: {desc}\n"
        prompt += "\n"

    prompt += f"Review:\n{review}\n\nAnalyze this review and return a JSON object indicating which categories apply (true/false for each subcategory)."

    try:
        response = await client.beta.chat.completions.parse(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing player reviews for video games. Respond with structured JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format=ReviewCategories
        )

        result = response.choices[0].message.parsed
        categories = result.model_dump() if result else ReviewCategories().model_dump()
        
        print(f"✓ Completed review {review_index + 1}")
        return {
            "review": review,
            "categories": categories,
            "index": review_index
        }

    except Exception as e:
        print(f"✗ Error categorizing review {review_index + 1}: {e}")
        # Return default structure with all False values
        return {
            "review": review,
            "categories": ReviewCategories().model_dump(),
            "index": review_index
        }


async def process_reviews_parallel(reviews: List[str], max_concurrent: int = MAX_CONCURRENT_REQUESTS) -> List[Dict]:
    """
    Process reviews in parallel with configurable concurrency.
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_single_review(review: str, index: int) -> Dict:
        async with semaphore:
            return await categorize_review(review, index)
    
    print(f"Starting parallel processing with {max_concurrent} concurrent requests...")
    start_time = time.time()
    
    # Create tasks for all reviews
    tasks = [
        process_single_review(review, i) 
        for i, review in enumerate(reviews)
    ]
    
    # Process all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    print(f"Parallel processing completed in {end_time - start_time:.2f} seconds")
    
    # Handle any exceptions and sort by original index
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            print(f"Task failed with exception: {result}")
            continue
        processed_results.append(result)
    
    # Sort by original index to maintain order
    processed_results.sort(key=lambda x: x['index'])
    
    return processed_results


def calculate_frequencies(categorized: List[Dict]) -> Dict:
    """Calculate frequency counts for all categories."""
    frequencies = {}

    # Initialize frequency counters
    for major_cat, subcats in CATEGORIES.items():
        frequencies[major_cat] = {}
        for subcat in subcats.keys():
            frequencies[major_cat][subcat] = 0

    # Count occurrences
    for item in categorized:
        categories = item["categories"]
        for major_cat, subcats in categories.items():
            if isinstance(subcats, dict):
                for subcat, value in subcats.items():
                    if value and subcat in frequencies[major_cat]:
                        frequencies[major_cat][subcat] += 1

    # Return nested structure
    return frequencies


async def main(max_concurrent: int = MAX_CONCURRENT_REQUESTS):
    """Main function to process reviews and categorize them."""
    try:
        with open("experiments/common_complaints/reviews.json", encoding="utf-8") as f:
            reviews = json.load(f)

        print(f"Processing {len(reviews)} reviews with {max_concurrent} concurrent requests...")

        # Process reviews in parallel
        categorized = await process_reviews_parallel(reviews, max_concurrent)

        complaint_frequencies = calculate_frequencies(categorized)

        output = {
            "num_reviews": len(reviews),
            "processed_reviews": len(categorized),
            "max_concurrent_requests": max_concurrent,
            "complaint_categories": complaint_frequencies
        }

        # Save output
        os.makedirs("experiments/common_complaints", exist_ok=True)
        with open("experiments/common_complaints/categorized_reviews.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"Categorization complete! Processed {len(categorized)} reviews.")
        print("Results saved to categorized_reviews.json")

    except FileNotFoundError:
        print("Error: reviews.json file not found. Please ensure the file exists at experiments/common_complaints/reviews.json")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in reviews.json")
    except Exception as e:
        print(f"Unexpected error: {e}")


def run_with_concurrency(max_concurrent: int = MAX_CONCURRENT_REQUESTS):
    """Helper function to run the async main with configurable concurrency."""
    asyncio.run(main(max_concurrent))


if __name__ == "__main__":
    import sys
    
    concurrent_requests = MAX_CONCURRENT_REQUESTS
    if len(sys.argv) > 1:
        try:
            concurrent_requests = int(sys.argv[1])
            print(f"Using {concurrent_requests} concurrent requests from command line argument")
        except ValueError:
            print(f"Invalid concurrency value, using default: {MAX_CONCURRENT_REQUESTS}")
    
    run_with_concurrency(concurrent_requests)