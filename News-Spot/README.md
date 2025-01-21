NewsSpot
NewsSpot is a web application that provides users with the latest news articles and videos from top Indian news channels. It allows users to search for news on specific topics, view related videos ranked by popularity (views), and summarize articles for quick insights.

Features
Search News: Search for the latest news articles and videos by entering a keyword.
Top Articles: Displays the top 5 news articles related to the search query, along with the source and a "Summarize" button.
Article Summarization: Summarize news articles to get concise insights into the content.
Top Videos: Displays the top 5 YouTube videos related to the search query, ranked by views, from prominent Indian news channels.
Responsive Design: Articles and videos are displayed side by side for better usability.
Technologies Used
Backend
Flask: Python web framework for handling API requests and responses.
Newspaper3k: For fetching and parsing article content.
nltk: Natural Language Toolkit for text processing and summarization.
scikit-learn: Used for TF-IDF vectorization in the summarization process.
YouTube Data API v3: Fetches videos and statistics (views, likes) from YouTube.
News API: Fetches news articles from multiple sources.
Frontend
HTML5: Structure of the web application.
CSS3: Styling and layout.
JavaScript: For dynamic content updates and API integration.
Setup Instructions
Prerequisites
Python 3.7 or higher
Flask (pip install flask)
Newspaper3k (pip install newspaper3k)
NLTK (pip install nltk)
scikit-learn (pip install scikit-learn)
API keys for:
YouTube Data API v3
News API
