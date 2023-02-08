from google.cloud import firestore
import streamlit as st
import openai
from google.oauth2 import service_account
from newspaper import Article
import nltk
import pandas as pd
from GoogleNews import GoogleNews
import spacy

# Authenticate to Firestore with the JSON account key.
# db = firestore.Client.from_service_account_json("news-aggregator-firestore-key.json")

# Create a reference to the news collection and google-scraper document from firebase
# doc_ref = db.collection("news").document("google-scraper")
# doc = doc_ref.get()

# Reference to all news
# posts_ref = db.collection("news")

# Reference to collection
# for doc in posts_ref.stream():
#     st.write("The id is: ", doc.id)
#     st.write("The contents are: ", doc.to_dict())

# Review data
# st.write(doc.id)
# st.write(doc.to_dict())

import json
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="news-aggregator")

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
                news_publish_date = news.publish_date
                news_text = news.text
                news_summary = news.summary
                news_image = news.top_image

                # Streamlit View of News
                st.markdown(f'[{news_title}]({news_link})')
                if news_image:
                    st.image(news_image)
                st.markdown(f"**Provided summary:** {news_summary}")

                # Store the news details in Firestore based on unique URL
                doc_ref = db.collection("news").document(news_link)
                doc_ref.set({
                    "title": news_title,
                    "url": news_link,
                    "date": news_publish_date,
                    "text": news_text
                }, merge=True)

            except:
                article_text = "Unable to extract article text."
        else:
            article_text = "Unable to extract article text."
