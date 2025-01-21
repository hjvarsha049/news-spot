from flask import Flask, request, jsonify, render_template
import requests
from newspaper import Article
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

nltk.download('punkt')

app = Flask(__name__)

NEWS_API_KEY = "fd116d1e95394cd5b1460c9a51e63e5e"
YOUTUBE_API_KEY = "AIzaSyC8vm-q8-I4wp0YO0N6HxgmEmK0iCskLkA"

# Channel IDs for Indian news channels
CHANNEL_IDS = [
    "UCZFMm1mMw0F81Z37aaEzTUA",  # NDTV
    "UCt4t-jeY85JegMlZ-E5UWtA",  # Aaj Tak
    "UCYPvAwZP8pZhSMW8qs7cVCw",  # India Today
    "UCmAv0T1BgvQjRBWmVNDnDoQ",  # ABP News
    "UCZprYEkC8XtPfGf6T2E3o5Q"   # Zee News
]

class TextSummarizer:
    def __init__(self):
        self._tfidf = TfidfVectorizer(tokenizer=self.tokenize_and_stem, stop_words='english')

    def tokenize_and_stem(self, text):
        stemmer = PorterStemmer()
        tokens = word_tokenize(text)
        return [stemmer.stem(token) for token in tokens]

    def train_model(self, documents):
        self._tfidf.fit(documents)

    def summarize(self, article_text, num_sentences=5):
        sentences = nltk.sent_tokenize(article_text)
        response = self._tfidf.transform([article_text])
        feature_names = self._tfidf.get_feature_names_out()

        word_prob = {feature_names[col]: response[0, col] for col in response.nonzero()[1]}
        scores = [
            sum(word_prob.get(word, 0) for word in self.tokenize_and_stem(sentence)) / len(sentence.split())
            for sentence in sentences
        ]

        ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
        return [sentence for _, sentence in ranked_sentences[:num_sentences]]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/articles', methods=['GET'])
def get_articles():
    query = request.args.get('query', '')
    news_api_url = f"https://newsapi.org/v2/everything?q={query}&domains=ndtv.com,thehindu.com,indiatoday.in&sortBy=popularity&apiKey={NEWS_API_KEY}"
    response = requests.get(news_api_url)
    data = response.json()

    articles = [
        {
            "title": article.get("title"),
            "description": article.get("description"),
            "url": article.get("url"),
            "source": article.get("source", {}).get("name", "Unknown Source")
        }
        for article in data.get("articles", [])[:5]
    ]
    return jsonify(articles)


@app.route('/api/videos', methods=['GET'])
def get_videos():
    query = request.args.get('query', '')
    videos = []

    for channel_id in CHANNEL_IDS:
        youtube_search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&channelId={channel_id}&type=video&maxResults=10&key={YOUTUBE_API_KEY}"
        search_response = requests.get(youtube_search_url)
        if search_response.status_code != 200:
            continue

        search_data = search_response.json()
        video_ids = [item["id"]["videoId"] for item in search_data.get("items", []) if "videoId" in item["id"]]

        if not video_ids:
            continue

        video_stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={','.join(video_ids)}&key={YOUTUBE_API_KEY}"
        stats_response = requests.get(video_stats_url)
        if stats_response.status_code != 200:
            continue

        stats_data = stats_response.json()
        videos.extend([
            {
                "title": video["snippet"]["title"],
                "description": video["snippet"]["description"][:100] + "..." if len(video["snippet"]["description"]) > 100 else video["snippet"]["description"],
                "url": f"https://www.youtube.com/watch?v={video['id']}",
                "views": int(video["statistics"].get("viewCount", "0")),
                "likes": int(video["statistics"].get("likeCount", "0"))
            }
            for video in stats_data.get("items", [])
        ])

    # Sort videos by views in descending order and select the top 5
    top_videos = sorted(videos, key=lambda x: x["views"], reverse=True)[:5]
    return jsonify(top_videos)


@app.route('/api/summarize', methods=['POST'])
def summarize_article():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        article = Article(url)
        article.download()
        article.parse()
        article_text = article.text

        summarizer = TextSummarizer()
        summarizer.train_model([article_text])
        summary = summarizer.summarize(article_text, num_sentences=5)

        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
