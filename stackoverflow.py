import itertools
import json
import requests
from bs4 import BeautifulSoup
import time
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def href(soup):
    """Get all href links from one page."""
    return [tag.get('href') for tag in soup.find_all(lambda tag: tag.name == 'a' and tag.get('class') == ['s-link'])]

def clean_empty_hrefs(hrefs):
    """Remove all empty lists and merge elements into one list."""
    return list(itertools.chain.from_iterable(filter(None, hrefs)))

def add_prefix(hrefs_list):
    """Rearrange links to include 'https://stackoverflow.com' prefix if missing."""
    prefix = 'https://stackoverflow.com'
    return [prefix + h for h in hrefs_list if 'https' not in h]

def single_page_scraper(url, session):
    """Fetch and parse a single page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    response = session.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def single_page_question_answer(url, session):
    """Extract question and top 5 answers in one request."""
    soup = single_page_scraper(url, session)

    # Extract question content
    question_section = soup.find("div", class_="s-prose js-post-body", itemprop="text")
    question = "\n".join([p.get_text() for p in question_section.find_all(['p', 'pre'])]) if question_section else None

    # Extract answers
    answers = [
        "\n".join([p.get_text() for p in answer.find("div", class_="s-prose").find_all(['p', 'pre'])])
        for answer in soup.find_all("div", class_="answer")
    ]

    # Get the top 5 answers
    return question, answers[:5]

def questions_answers(start_page, end_page, output_file="output.json"):
    """Scrape questions and their top 5 answers from StackOverflow."""
    session = requests.Session()
    # can increase how many question are retrieved with each request but be wary of timeout
    base_url = 'https://stackoverflow.com/questions/tagged/terraform-provider-azure?tab=votes&page={}&pagesize=30&filters=answered'
    soups = [
        single_page_scraper(base_url.format(page), session)
        for page in range(start_page, end_page + 1)
    ]

    hrefs = [href(s) for s in soups if s]
    hrefs_list = clean_empty_hrefs(hrefs)
    new_hrefs_list = add_prefix(hrefs_list)

    output_data = []

    for url in new_hrefs_list:
        logging.info(f"Scraping URL: {url}") #added log
        try:
            question, answers = single_page_question_answer(url, session)
            if question and answers:
                output_data.append({
                    "question": question,
                    "answers": [{"text": answer} for answer in answers]
                })
                logging.info(f"Successfully scraped: {url}") #added log
            else:
                logging.warning(f"No data found at: {url}") #added log
        except Exception as e:
            logging.error(f"Skipping URL {url} due to error: {e}")
        time.sleep(random.uniform(1, 3)) # Add random delay between 1 and 3 seconds
    time.sleep(random.uniform(2,5)) # add delay between pages.

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    # change end_page to amount of pages u want scraped, one page is 15 questions
    questions_answers(start_page=1, end_page=30)
