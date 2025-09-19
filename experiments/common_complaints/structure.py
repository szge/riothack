# Script to extract review bodies from metacritic_raw.txt and save as JSON array in reviews.json
import re
import json

def extract_reviews(text):
	# Each review starts after a date and username, then a score, then the body, ending before 'Report' or 'Read More'
	# We'll use a regex to find review bodies
	# Reviews are separated by lines with a date and username, then a score, then the body, ending with 'Report' or 'Read More'
	# We'll match blocks between a score line and 'Report' or 'Read More'
	pattern = re.compile(r"\n\d+\n.*?\n(.*?)(?:\nReport|\nRead More)", re.DOTALL)
	reviews = pattern.findall(text)
	# Clean up whitespace
	reviews = [r.strip() for r in reviews if r.strip()]
	return reviews

def main():
	with open("experiments/common_complaints/metacritic_raw.txt", encoding="utf-8") as f:
		raw = f.read()
	reviews = extract_reviews(raw)
	with open("experiments/common_complaints/reviews.json", "w", encoding="utf-8") as f:
		json.dump(reviews, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
	main()
