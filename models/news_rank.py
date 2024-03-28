from collections import defaultdict
import pandas as pd
import json
from news_api.retrive_news import NewsQuery
from datetime import datetime, timezone
import numpy as np


class NewsRank:
    def __init__(self):
        self.sources_df = {}
        self.rank_map = {}
        self.rank_to_score = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0}
        self.articles = {}

    def load_sources_to_dict(self, path):

        self.sources_df = pd.read_excel(path)
        for source, rank in zip(self.sources_df['Outlet Name'], self.sources_df['Tier']):
            self.rank_map[source] = self.rank_to_score.get(rank.upper(), 0)

        print(self.rank_map)

    def load_news_results(self):
        with open('news_results.json', 'r') as file:
            articles = json.load(file)
        self.articles = articles["articles"]

    def score_by_source_tier(self, article_index, src_list):
        article_source = self.articles[article_index]['source']['name']
        src_list.append(article_source)
        return self.rank_map[article_source] if article_source in self.rank_map else 0

    def score_by_date(self, article_index, query):
        return 0

    def score_by_length(self, article_index):
        article_length = len(self.articles[article_index]['content'])
        return 1 if article_length > 200 else 0

    def score_by_keywords(self, article_index, keywords=None):
        article_content = self.articles[article_index]['content']
        return sum([1 for keyword in keywords if keyword in article_content])

    def rank_articles(self, components, query, w_source, w_date, w_length, w_keyword):
        scores = defaultdict(int)
        rep_title = {}
        source_list = defaultdict(list)
        for group_name in components:
            for article_index in components[group_name]:
                source_score = self.score_by_source_tier(article_index, source_list[group_name])
                date_score = self.score_by_date(article_index, query)
                length_score = self.score_by_length(article_index)
                keyword_score = self.score_by_keywords(article_index, keywords=[])

                total_score = (w_source*source_score + w_date*date_score + w_length*length_score
                               + w_keyword*keyword_score)
                rep_title[group_name] = article_index if total_score >= scores[group_name] else rep_title[group_name]
                scores[group_name] = max(scores[group_name], total_score)

        sorted_keys = sorted(scores, key=scores.get, reverse=True)
        for key in sorted_keys:
            print(self.articles[rep_title[key]]['title'])
            print(source_list[key],"\n")


path_to_file = 'news_api/major_outlets.xlsx'
news_sources = NewsRank()
news_sources.load_sources_to_dict(path_to_file)
news_sources.load_news_results()
qry = NewsQuery(keyword="IPL", context="Cricket", from_date="2024-03-26")
with open('news_groupings.json', 'r') as file:
    data = json.load(file)
news_sources.rank_articles(data, qry, 1, 1, 1, 1)
