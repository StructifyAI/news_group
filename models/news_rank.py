import pandas as pd


class NewsSource:
    def __init__(self):
        self.sources_df = {}
        self.rank_map = {}
        self.rank_to_score = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0}

    def load_sources_to_dict(self, path):

        self.sources_df = pd.read_excel(path)
        for source, rank in zip(self.sources_df['Outlet Name'], self.sources_df['Tier']):
            self.rank_map[source] = self.rank_to_score.get(rank.upper(), 0)

        print(self.rank_map)


path_to_file = 'major_outlets.xlsx'
news_sources = NewsSource()
news_sources.load_sources_to_dict(path_to_file)
