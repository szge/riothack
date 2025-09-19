from dotenv import load_dotenv
import os
import requests
import json
import time

load_dotenv()

def main():
	api_key = os.getenv('RIOT_API_KEY')
	if not api_key:
		raise ValueError('RIOT_API_KEY environment variable must be set.')

	with open("experiments/download_matches/szge_match_ids.json", "r", encoding="utf-8") as f:
		match_ids = json.load(f)


	# Load existing progress if available
	dates_path = "experiments/download_matches/szge_match_dates.json"
	if os.path.exists(dates_path):
		with open(dates_path, "r", encoding="utf-8") as f:
			match_dates = json.load(f)
	else:
		match_dates = {}

	delay = 0.1
	for match_id in match_ids:
		if match_id in match_dates:
			continue  # Skip already processed
		while True:
			url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
			response = requests.get(url)
			if response.status_code == 429:
				print(f"Rate limit exceeded for match {match_id}. Backing off for {delay:.2f}s.")
				time.sleep(delay)
				delay = min(delay * 2, 60)  # Exponential backoff, max 60s
				continue
			elif response.status_code != 200:
				print(f"Failed to fetch match {match_id}: {response.status_code} {response.text}")
				break
			data = response.json()
			timestamp = data.get('info', {}).get('gameStartTimestamp')
			match_dates[match_id] = timestamp
			# Write progress after each successful fetch
			with open(dates_path, "w", encoding="utf-8") as f:
				json.dump(match_dates, f, ensure_ascii=False, indent=2)
			delay = 0.1  # Reset delay after success
			time.sleep(delay)
			break

if __name__ == "__main__":
	main()
