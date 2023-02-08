from json import JSONDecodeError

from google.cloud import firestore
import streamlit as st
import openai
from newspaper import Article
import nltk
import pandas as pd
from GoogleNews import GoogleNews
import spacy
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Load credentials from Firebase
key_dict = json.loads(st.secrets["textkey"])
cred = credentials.Certificate(key_dict)

try:
    firebase_admin.initialize_app(cred, name='news-aggregator')
except ValueError as error:
    if 'already exists' in str(error):
        app = firebase_admin.get_app('news-aggregator')
    else:
        raise error

db = firestore.client()


# Create a reference to the news collection and google-scraper document from firebase
doc_ref = db.collection("news").document("google-scraper")
doc = doc_ref.get()

# Streamlit App
nltk.download('punkt')

# User inputs
st.title("News")
query = st.text_input("Enter your news query:")
date = st.date_input("Enter date to query news for (YYYY-MM-DD):")

if date and query:
    # Query news for selected date using Google News API
    gn = GoogleNews()
    gn.search(query)
    gn.setTimeRange(date, date)
    news_results = gn.result(sort=True)

    # Extract details of each news article
    for news in news_results:
        news_link = news["link"]
        if news_link:
            try:
                # Article details
                news = Article(news_link)
                news.download()
                news.parse()
                news.nlp()
                news_title = news.title
                # news_publish_date = news.publish_date
                news_text = news.text
                news_summary = news.summary
                news_image = news.top_image

                # Store the news details in Firestore based on unique URL
                doc_ref = db.collection("news").document(news_link)
                doc_ref.set({
                    "title": news_title,
                    "link": news_link,
                    # "published_date": news_publish_date,
                    "content": news_text,
                    "media": news_image,
                    "summary": news_summary,
                }, merge=True)

            except:
                article_text = "Unable to extract article text."
        else:
            article_text = "Unable to extract article text."

# Render app
news_ref = db.collection("news")
for news_data in news_ref.stream():
    data = news_data.to_dict()
    title = data["title"]
    link = data["link"]
    # published_date = data["published_date"]
    content = data["content"]
    media = data["media"]
    summary = data["summary"]

    st.markdown(f'[{title}]({link})')
    if media:
        st.image(media)
    st.markdown(f"**Provided summary:** {summary}")
