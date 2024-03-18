import requests
import json

class NewsQuery:
    def __init__(self, keyword, from_date="", to_date="", language='en'):
        self.keyword = keyword
        self.from_date = from_date
        self.to_date = to_date
        self.language = language
        

class NewsApiWrapper:
    def __init__(self, api_key):
        self.base_url = 'https://newsapi.org/v2/everything'
        self.api_key = api_key

    def execute_query(self, query):
        query_url = f"{self.base_url}?q={query.keyword}&from={query.from_date}&to={query.to_date}&sortBy=popularity&language={query.language}&apiKey={self.api_key}"
        response = requests.get(query_url)
        return response.json()

'''NEWS_API_KEY = None
with open('../../keys/newsapi.txt', 'r') as file:
    NEWS_API_KEY = file.read().strip()

query = NewsQuery("OpenAI")
newsApiClientWrapper = NewsApiWrapper(NEWS_API_KEY)
response = newsApiClientWrapper.execute_query(query)

with open("news_results.json", "w") as outfile:
    outfile.write(json.dumps(response, indent=4))'''


