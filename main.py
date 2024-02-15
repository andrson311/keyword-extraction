import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from wordwise import Extractor

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

if __name__ == '__main__':
    url = 'https://ak-codes.com/google-knowledge-graph-search/'
    soup = get_soup(url)
    body = soup.find('body')
    text = scrape_content(body)
    extractor = Extractor(spacy_model="en_core_web_lg", n_gram_range=(1, 4))
    keywords = extractor.generate(text, 10)

    print(keywords)

