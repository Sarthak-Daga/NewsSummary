from flask import Flask, render_template
from newsapi import NewsApiClient
from newspaper import Article
import nltk

# Initialize Flask app
app = Flask(__name__)

# Initialize News API client
newsapi = NewsApiClient(api_key='e35362ca86944f2a8a39e41738b677d9')

# Download nltk resources
nltk.download('punkt')

# Function to fetch and process news articles
def get_news_articles(keyword, page_size=5):
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

# Define a route to display news articles
@app.route('/')
def index():
    keyword = 'Education'  # Change this keyword as needed
    articles = get_news_articles(keyword)
    return render_template('specific.html', articles=articles)

if __name__ == '__main__':
    app.run(debug=True)
