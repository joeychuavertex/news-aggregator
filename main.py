import urllib.parse
import uuid
from datetime import datetime
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
import hashlib

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Load credentials from Firebase
key_dict = json.loads(st.secrets["textkey"])
cred = credentials.Certificate(key_dict)

try:
    firebase_admin.initialize_app(cred)
except ValueError as error:
    if 'already exists' in str(error):
        app = firebase_admin.get_app()
    else:
        raise error

db = firestore.client()

# Streamlit App
nltk.download('punkt')

# User inputs
st.title("News")
query = st.text_input("Enter your news query:")

# date = st.date_input("Enter date to query news for (YYYY-MM-DD):")

if query:
    # Query news for selected date using Google News API
    gn = GoogleNews(start='01/01/2023', end='02/11/2023')
    gn.search(query)
    # gn.setTimeRange(date, date)
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

                news_id = str(uuid.uuid5(uuid.NAMESPACE_URL, news_link))

                doc_ref = db.collection("news").document(news_id)

                doc_ref.set({
                    "id": news_id,
                    "title": news.title,
                    "link": news_link,
                    "published_date": news.publish_date,
                    "content": news.text,
                    "media": news.top_image,
                    "summary": news.summary,
                    "query": query,
                })
            except:
                pass

# Render app
news_ref = db.collection("news")
for news_data in news_ref.stream():
    data = news_data.to_dict()
    try:
        if query == data["query"]:
            title = data["title"]
            link = data["link"]
            published_date = data["published_date"]
            content = data["content"]
            media = data["media"]
            summary = data["summary"]

            st.markdown(f'[{title}]({link})')
            if media:
                st.image(media)
            st.markdown(f"**Provided summary:** {summary}")
    except KeyError:
        pass

    else:
        pass
