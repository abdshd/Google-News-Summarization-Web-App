import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
import base64
import re
import boto3
nlp = spacy.load('en_core_web_sm')

def lambda_handler(event=None, context=None):

    headers = {'User-Agent': 'Mozilla/5.0'}

    url = 'https://news.google.com/news/rss'
    client = urlopen(url)
    xml_page = client.read()
    client.close()
    soup = BeautifulSoup(xml_page, 'xml')

    contents = soup.find_all("item")

    encoded_links = []
    headlines = []
    dates = []

    for news in contents:
        if "youtube.com" in str(news.source):
            continue
        encoded_links.append(news.link.text)
        headlines.append(news.title.text)
        dates.append(news.pubDate.text)

    encoded_links = encoded_links[:15]
    headlines = headlines[:15]
    dates = dates[:15]

    decoded_links = []

    for link in encoded_links:
        coded = link[44:-5]
        while True:
            try:
                url = base64.b64decode(coded)
                break
            except:
                coded += "a"
        url = str(base64.b64decode(coded))

        strip1 = re.search("(?P<url>https?://[^\s]+)", url).group("url")
        strip2 = stripped = strip1.split('$', 1)[0]
        strip3 = stripped = strip2.split('\\', 1)[0]
        decoded_links.append(strip3)

    summarized_texts = []


    counter = 0
    for link in decoded_links:
        try:
            new_page = requests.get(link, headers=headers)
        except:
            continue
        new_soup  = BeautifulSoup(new_page.text, 'lxml')
        
        text = ""
        paragraphs = new_soup.find_all("p")
        for p in paragraphs:
            text += p.text

        doc = nlp(text)

        corpus = [sent.text.lower() for sent in doc.sents]
        cv = CountVectorizer(stop_words=list(STOP_WORDS))
        cv_fit=cv.fit_transform(corpus)
        word_list = cv.get_feature_names_out()
        count_list = cv_fit.toarray().sum(axis=0)
        word_frequency = dict(zip(word_list, count_list))

        val = sorted(word_frequency.values())
        higher_word_frequencies = [word for word, freq in word_frequency.items() if freq in val[-3:]]
        higher_frequency = val[-1]
        for word in word_frequency.keys():
            word_frequency[word] = (word_frequency[word]/higher_frequency)

        sentence_rank = {}
        for sent in doc.sents:
            for word in sent:
                if word.text.lower() in word_frequency.keys():
                    if sent in sentence_rank.keys():
                        sentence_rank[sent] += word_frequency[word.text.lower()]
                    else:
                        sentence_rank[sent] = word_frequency[word.text.lower()]
        top_sentences = (sorted(sentence_rank.values())[::-1])
        top_sentences = top_sentences[:3]


        summary = []
        for sent, strength in sentence_rank.items():
            if strength in top_sentences:
                summary.append(sent)
            else:
                continue

        nlp_text = [sent.text.strip() for sent in summary]
        final = ''.join(nlp_text)

        if "enable" and ("js" or "javascript") in final.lower():
            del headlines[counter]
            del dates[counter]
            continue

        summarized_texts.append(final)
        counter += 1


    list_of_summaries = [{'headline': title, 'date': date, 'summary': summarized} for title, date, summarized in zip(headlines, dates, summarized_texts)]

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('News_Data')

    for object in list_of_summaries:
        table.put_item(
            Item = object
        )

    return "Success"
