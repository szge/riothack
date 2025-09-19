from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

def main():
	api_key = os.getenv('RIOT_API_KEY')
	puuid = os.getenv('PUUID')
	if not api_key or not puuid:
		raise ValueError('RIOT_API_KEY and PUUID environment variables must be set.')

	all_matches = []
	for i in range(10):
		start = i * 100
		url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count=100&api_key={api_key}"
		response = requests.get(url)
		if response.status_code != 200:
			print(f"Failed to fetch matches for start={start}: {response.status_code} {response.text}")
			continue
		matches = response.json()
		all_matches.extend(matches)

	with open("experiments/download_matches/szge_match_ids.json", "w", encoding="utf-8") as f:
		json.dump(all_matches, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
	main()
