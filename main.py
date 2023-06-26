# Fetches a random article from Wikihow and dumps into json

import json
import os
from datetime import datetime
from hashlib import md5
from time import sleep

import regex as re
import requests
from bs4 import BeautifulSoup

# set to 1 to test with a specific url declared in specific_url and lower batches to 1
USE_DEBUG = 0
WORKDIR = "work"
BATCHES = 1 if USE_DEBUG else 20    # change number of batches here

random_url = "https://www.wikihow.com/Special:Randomizer"
specific_url = "https://www.wikihow.com/Raise-Mealworms"


def get_article():
    art_regex = re.compile("mf-section-\d{1,}")
    headline_regex = re.compile("title_\w{2}")
    subtext_regex = re.compile("(?<=\<p\>)(.*)(?=\<\/p\>)")
    step_regex = re.compile("step-id-\d{2,}")

    art_url = specific_url if USE_DEBUG else random_url
    r = requests.get(art_url)
    soup = BeautifulSoup(r.content, "html.parser")

    div_article = soup.find("div", class_="mw-parser-output")
    headline = soup.find("h1", class_=headline_regex).findChild("a").contents[0]
    url_hash = md5(str(r.url).encode())
    subtext = div_article.find("div", class_="mf-section-0").findChild("p").text
    steps = div_article.find_all("li", id=step_regex)

    # print(f"Headline:\n{headline} // URL Hash: {url_hash.hexdigest()}\n\nSubtext:\n{subtext}\n")

    json_data = {
        "hash": url_hash.hexdigest(),
        "url": r.url,
        "headline": headline,
        "subtext": subtext
    }

    step_ctr = 1
    for entry in steps[0:]:
        entry = entry.find("div", class_="step").text.replace("X\nResearch source", "").replace("\n", "")
        # print(f"Step {step_ctr}:\n{entry}\n")
        json_data[f"step_{step_ctr}"] = entry
        step_ctr += 1

    return json_data, r.url, url_hash.hexdigest()


if __name__ == "__main__":
    print("Wikihow scraper starting...")
    if not os.path.exists(WORKDIR):
        os.makedirs(WORKDIR)

    json_batch = {}
    done_hashes = []
    for i in range(BATCHES):
        json_batch[f"{i}"], url, url_hash = get_article()

        if url_hash in done_hashes:
            print(f"Hash {url_hash} already scraped! Skipping...")
            continue
        done_hashes.append(url_hash)

        print(f"Art {i+1}/{BATCHES} done. URL: {url}, Hash: {url_hash}")
        sleep(0.2) # let's not flood requests

    with open(f"{WORKDIR}/batch_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json", "w") as file:
        json.dump(json_batch, file)