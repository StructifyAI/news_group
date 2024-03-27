import requests


class NewsQuery:
    def __init__(self, keyword, context="", from_date="", to_date="", language='en'):
        self.keyword = keyword+" "+context
        self.from_date = from_date
        self.to_date = to_date
        self.language = language
        

class NewsApiWrapper:
    def __init__(self, api_key):
        self.base_url = 'https://newsapi.org/v2/everything'
        self.api_key = api_key

    def execute_query(self, query):
        query_url = (f"{self.base_url}?q={query.keyword}&from={query.from_date}&to={query.to_date}&sortBy=relevancy"
                     f"&language={query.language}&apiKey={self.api_key}")
        response = requests.get(query_url)
        return response.json()



