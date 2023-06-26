import regex as re
from bs4 import BeautifulSoup
import requests
from hashlib import md5

# purges everything inside <span>-tags. on wikihow these are usually tooltips
def despanify(soup):
    spans = soup.find_all("span")
    for span in spans:
        span.decompose()
    return soup


def get_article(art_url):
    art_regex = re.compile("mf-section-\d{1,}")
    subtext_regex = re.compile("(?<=\<p\>)(.*)(?=\<\/p\>)")
    headline_regex = re.compile("title_\w{2}")
    step_regex = re.compile("step-id-\d{2,}")

    r = requests.get(art_url)
    soup = BeautifulSoup(r.content, "html.parser")

    div_article = soup.find("div", class_="mw-parser-output")
    headline = soup.find("h1", class_=headline_regex).findChild("a").contents[0]
    url_hash = md5(str(r.url).encode())
    subtext = despanify(div_article.find("div", class_="mf-section-0").findChild("p")).text
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
        entry = entry.find("div", class_="step")
        entry = despanify(entry).text.replace("\n", "")
        # print(f"Step {step_ctr}:\n{entry}\n")
        json_data[f"step_{step_ctr}"] = entry
        step_ctr += 1

    return json_data, r.url, url_hash.hexdigest()
