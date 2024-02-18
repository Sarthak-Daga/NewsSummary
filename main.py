from flask import Flask, jsonify, render_template
import requests
from flask_pymongo import PyMongo
from newsapi import NewsApiClient
from newspaper import Article
import nltk
from gtts import gTTS
import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/NewSummary"
mongo = PyMongo(app)
newsapi = NewsApiClient(api_key='2a56eed0128b47739a6c63888499a76b')
NEWS_API_KEY = "2a56eed0128b47739a6c63888499a76b"
nltk.download('punkt')


def get_news_articles(keyword, page_size=3):
    articles_data = []
    # Fetch news articles
    page = 1
    while len(articles_data) < page_size:
        news_articles = newsapi.get_everything(q=keyword, language='en', page=page, page_size=page_size)

        # Process each article
        for article in news_articles['articles']:
            try:
                article_data = {}
                article_data['title'] = article['title']
                article_data['author'] = article['author']
                article_data['url'] = article['url']

                # Extract article summary
                toi_article = Article(article['url'], language="en")
                toi_article.download()
                toi_article.parse()
                toi_article.nlp()
                article_data['summary'] = toi_article.summary

                # Extract article image URL if available
                article_data['image'] = article['urlToImage'] if 'urlToImage' in article else None

                # Only include articles with a valid summary
                if article_data['summary']:
                    articles_data.append(article_data)
                    if len(articles_data) == page_size:
                        break
            except Exception as e:
                print(f"Error processing article: {e}")
        page += 1
    
    return articles_data

# MongoDB setup
client = MongoClient('localhost', 27017)  # Assuming MongoDB is running locally on default port
db = client['NewSummary']
collection = db['LoginData']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signuppage')
def signup_page():
    return render_template('signuppage.html')

@app.route('/loginpage')
def login_page():
    return render_template('loginpage.html')

@app.route('/HomePage')
def HomePage():
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}&pageSize=10"
    response = requests.get(url)
    news_data = response.json()

    if news_data['status'] == 'ok':
        articles = [article for article in news_data['articles'] if article.get('title')]
        return render_template('main.html', articles=articles)
    else:
        return "Error fetching news"

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Check if the passwords match
        if password != confirm_password:
            error_message = "Passwords do not match. Please try again."
            return render_template('signuppage.html', error_message=error_message)
        
        # Check if the username already exists
        if collection.find_one({'username': username}):
            warning_message = f"Username '{username}' already exists. Please choose a different username."
            return render_template('signuppage.html', warning_message=warning_message)
        
        # Inserting data into MongoDB
        user_data = {
            'username': username,
            'password': password
        }
        collection.insert_one(user_data)
        
        # Redirect to the page of interest after successful signup
        return redirect('/HomePage')


    

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username exists in the database
        user = collection.find_one({'username': username})
        if user:
            # If the username exists, check if the password matches
            if user['password'] == password:
                # Password matches, redirect to success page
                return redirect('/HomePage')
        
        # If username or password is incorrect, redirect back to login page with error message
        error_message = "Invalid username or password. Please try again."
        return render_template('loginpage.html', error_message=error_message)

@app.route('/Technology')
def tech():
    articles = get_news_articles("Technology")
    # Render the HTML page for the specified category
    return render_template('Technology.html',articles=articles)

@app.route('/f')
def finance():
    articles = get_news_articles("finance")
    # Render the HTML page for the specified category
    return render_template('finance.html',articles=articles)

@app.route('/Bussiness')
def busi():
    articles = get_news_articles("Bussiness")
    # Render the HTML page for the specified category
    return render_template('Bussiness.html',articles=articles)

@app.route('/sports')
def spot():
    articles = get_news_articles("sports")
    # Render the HTML page for the specified category
    return render_template('sports.html',articles=articles)


if __name__ == '__main__':
    app.run(debug=True)
