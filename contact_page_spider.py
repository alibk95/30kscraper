import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
import csv
from collections import deque
from urllib.parse import urlsplit
import re
# init the colorama module
colorama.init()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET

# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()

total_urls_visited = 0


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue
        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            # not a valid URL
            continue
        if href in internal_urls:
            # already in the set
            continue
        if domain_name not in href:
            # external link
            if href not in external_urls:
                print(f"{GRAY}[!] External link: {href}{RESET}")
                external_urls.add(href)
            continue
        print(f"{GREEN}[*] Internal link: {href}{RESET}")
        urls.add(href)

        internal_urls.add(href)

    return urls


def crawl(url, max_urls=30):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1
    links = get_all_website_links(url)
    for link in links:
        if total_urls_visited > max_urls:
            break
        crawl(link, max_urls=max_urls)


def get_email(url):

    # a queue of urls to be crawled
    unprocessed_urls = url
    print(unprocessed_urls)
    # set of already crawled urls for email

    # extract base url to resolve relative links
    parts = urlsplit(url)

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/87.0.4280.66 Safari/537.36'}

    try:
        response = requests.get(url, headers=headers)
    except:
        response = ""
        pass

    # extract all email addresses and add them into the resulting set
    # You may edit the regular expression as per your requirement
    try:
        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
        emails = new_emails
        if emails == set():
            emails = ''
    except:
        emails = ''
    for em in emails:
        fieldnames = ['link', 'email']
        with open(r'30k_output.csv', 'a', newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # checks if the file already exists with headers then it skips writing headers again.
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow({'link': q, 'email': em})
        csvfile.close()

if __name__ == "__main__":

    dictionary = open('task.csv', 'r', encoding="utf-8")
    query_list = dictionary.readlines()

    for q in query_list:
        print(q)
        max_urls = 1
        try:
            crawl(q, max_urls=max_urls)
        except:
            email = ""
        print("[+] Total Internal links:", len(internal_urls))
        print("[+] Total External links:", len(external_urls))
        print("[+] Total URLs:", len(external_urls) + len(internal_urls))

        for t in internal_urls:
            get_email(t)




