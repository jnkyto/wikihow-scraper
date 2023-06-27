# Fetches a random article from Wikihow and dumps into json

import argparse
import json
import os
from datetime import datetime
from time import sleep

from article import get_article

random_url = "https://www.wikihow.com/Special:Randomizer"
specific_url = "https://www.wikihow.com/Refill-a-Fire-Extinguisher"

# set to 1 to test with a specific url declared in specific_url and lower batches to 1
USE_DEBUG = 0
WORKDIR = "work"
URL = specific_url if USE_DEBUG else random_url


def batch_and_dump(batches):
    if not os.path.exists(WORKDIR):
        os.makedirs(WORKDIR)

    json_batch = {}
    done_hashes = []
    for i in range(batches):
        json_batch[f"{i}"], url, url_hash = get_article(URL)

        if url_hash in done_hashes:
            print(f"Hash {url_hash} already scraped! Skipping...")
            continue
        done_hashes.append(url_hash)

        print(f"Art {i + 1}/{batches} done. URL: {url}, Hash: {url_hash}")
        sleep(0.2)  # let's not flood requests

    with open(f"{WORKDIR}/batch_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json", "w") as file:
        json.dump(json_batch, file)


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
    print("All done. Exiting...")
    exit(0)
