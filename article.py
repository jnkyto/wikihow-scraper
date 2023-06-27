import os
from hashlib import md5

import bs4.element
import regex as re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


# purges everything inside <span>-tags. on Wikihow these are usually tooltips
def despanify(soup):
    spans = soup.find_all("span")
    for span in spans:
        span.decompose()
    return soup


def get_article(art_url):
    # regexes for finding the html-tags we want
    art_regex = re.compile("mf-section-\d{1,}")
    subtext_regex = re.compile("(?<=\<p\>)(.*)(?=\<\/p\>)")
    headline_regex = re.compile("title_\w{2}")
    stepgroup_regex = re.compile("steps_\d{1,2}")
    step_regex = re.compile("step-id-\d{2,}")

    # send customized headers to Wikihow to indicate our scraping
    r = requests.get(art_url, headers={
        "User-Agent": os.getenv("UA"),
        "From": os.getenv("EMAIL")
    })
    soup = BeautifulSoup(r.content, "html.parser")

    div_article = soup.find("div", class_="mw-parser-output")  # this finds the content of the article
    headline = soup.find("h1", class_=headline_regex).findChild("a").contents[0]
    url_hash = md5(str(r.url).encode())  # we hash the url to keep track of what we've done
    subtext = despanify(div_article.find("div", class_="mf-section-0").findChild("p")).text

    # check if "Things You Should Know"-field exists
    tysk = div_article.find("div", class_="section_text", id="thingsyoushouldknow")
    if type(tysk) is bs4.element.Tag:
        tysk = despanify(tysk).text.replace("\n", "")

    # find stepgroups, which correspond to parts in Wikihow
    stepgroups = div_article.find_all("div", id=stepgroup_regex, class_="section_text")

    json_data = {
        "hash": url_hash.hexdigest(),
        "url": r.url,
        "headline": headline,
        "subtext": subtext,
        "tysk": tysk if type(tysk) == str else "none"
    }

    # print(f"Headline:\n{headline} // URL Hash: {url_hash.hexdigest()}\n\nSubtext:\n{subtext}")

    for i, stepgroup in enumerate(stepgroups, start=1):
        steps = stepgroup.find_all("li", id=step_regex)
        json_data[f"group_{i}"] = []
        for j, step in enumerate(steps, start=1):
            step = step.find("div", class_="step")
            step = despanify(step).text.replace("\n", "")
            step_data = {f"step_{j}": step}
            json_data[f"group_{i}"].append(step_data)
        # print(f"Group {i}: {json_data[f'group_{i}']}")

    return json_data, r.url, url_hash.hexdigest()
