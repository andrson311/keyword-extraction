import os
import requests
import argparse
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from googleapiclient.discovery import build
from pprint import pprint

load_dotenv()

def get_soup(url):
    response = requests.get(url)
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except:
        return
    
def scrape_content(body):
    p_tags = body.find_all('p')
    text = []
    for p in p_tags:
        for link in p.find_all('a'):
            link.extract()
        for img in p.find_all('img'):
            img.extract()
        text.append(p.get_text(strip=False))
    
    return ' '.join(text)


def extract_keywords(text):

    response_schemas = [
        ResponseSchema(name='keywords', description='List of extracted keywords from a string')
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

    format_instructions = output_parser.get_format_instructions()
    prompt = PromptTemplate(
        template='extract relevant keywords from the following text that would rank on Google: \n{text}\n{format_instructions}',
        input_variables=['text'],
        partial_variables={'format_instructions': format_instructions}
    )

    model = ChatOpenAI(temperature=0)
    chain = prompt | model | output_parser
    keywords = chain.invoke({'text': text})

    return keywords['keywords']

def get_search_results(query):
    service = build(
        'customsearch',
        'v1',
        developerKey=os.getenv('CUSTOM_SEARCH_API_KEY')
    )

    res = service.cse().list(
        q=query,
        cx=os.getenv('CUSTOM_SEARCH_ENGINE_ID')
    ).execute()

    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Returns list of search results links'
    )

    parser.add_argument(
        '-u',
        '--url',
        type=str,
        required=True,
        help='URL address from where to scrape information'
    )

    args = parser.parse_args()
    url = args.url

    soup = get_soup(url)
    body = soup.find('body')
    text = scrape_content(body)
    keywords = extract_keywords(text)
    print(keywords)

    res = get_search_results(keywords[0])
    links = [l['link'] for l in res['items']]
    pprint(links)

