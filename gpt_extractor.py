import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

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

if __name__ == '__main__':
    url = 'https://ak-codes.com/google-knowledge-graph-search/'
    soup = get_soup(url)
    body = soup.find('body')
    text = scrape_content(body)

    keywords = extract_keywords(text)

    print(keywords)

