# Fetches a random article from Wikihow and dumps into json

import argparse
import json
import os
from datetime import datetime
from time import sleep

from article import get_article

random_url = "https://www.wikihow.com/Special:Randomizer"
specific_url = "https://www.wikihow.com/Refill-a-Fire-Extinguisher"

# set to 1 to test with a specific url declared in specific_url
USE_DEBUG = 0
BATCH_SIZE = 100
WORKDIR = "work"
URL = specific_url if USE_DEBUG else random_url


def batch_and_dump(batches):
    if not os.path.exists(WORKDIR):
        os.makedirs(WORKDIR)

    timestamp: str = datetime.now().strftime('%Y%m%d-%H%M')
    json_batch = {}
    done_hashes = []
    for j in range(1, batches + 1):
        print(f"Starting batch {j} of {batches}...")
        i = 0
        while i < BATCH_SIZE:
            sleep(0.5)  # let's not flood requests
            article_data = {}

            # handle 0.001% of articles that somehow manage to error out
            try:
                article_data, url, url_hash = get_article(URL)
            except:
                print(f"An error occurred while getting the article. Skipping...")
                continue

            if url_hash in done_hashes:
                print(f"Hash {url_hash} already scraped during this run! Skipping...")
                continue

            done_hashes.append(url_hash)
            json_batch[f"{i}"] = article_data

            print(f"Art {i + 1}/{BATCH_SIZE} done. URL: {url}, Hash: {url_hash}")
            i += 1

        with open(f"{WORKDIR}/{timestamp}_batch_{j}.json", "w") as file:
            json.dump(json_batch, file)

        print(f"Batch {j} done and written to file.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b", "--batches",
        type=int,
        help="number of articles to be scraped")
    args = parser.parse_args()

    if type(args.batches) != int:
        print("Please specify the amount of articles by passing --batches <number> as argument.")
        print("Quitting on error.")
        exit(1)
    print("Wikihow scraper starting...")
    batch_and_dump(args.batches)
    # get_article(URL)
    print("All done. Exiting... (writing the .json-file might take a while)")
    exit(0)
