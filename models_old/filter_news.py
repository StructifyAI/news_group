from transformers import DistilBertTokenizer, DistilBertModel
import torch
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class DistilBertEmbedding():
    def __init__(self, model_name):
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_name)
        self.model = DistilBertModel.from_pretrained(model_name)

    def get_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            hidden_states = outputs.last_hidden_state
        embedding = hidden_states.mean(dim=1)
        return embedding[0]
          
class FilterNews():
    def __init__(self, query, model, results=""):
        self.query = query
        self.results = results
        self.model = model
        if self.results == "":
            self.load_results()
        self.embeddings = []
        self.calculate_embeddings()

    def load_results(self):
        with open('news_results.json', 'r') as file:
            self.results = json.load(file)
    
    def calculate_embeddings(self):
        for article in self.results["articles"]:
            article['embedding'] = self.model.get_embedding(article["description"])

    def filter(self):
        embeddings_list = [article['embedding'].unsqueeze(0) for article in self.results["articles"]]
        embeddings = torch.stack(embeddings_list, dim=0)
        embeddings_2d = embeddings.view(len(self.results["articles"]), -1)
        embeddings_np = embeddings_2d.numpy()

        tsne = TSNE(n_components=2, perplexity = 4, random_state=42, n_iter = 2000)
        tsne_results = tsne.fit_transform(embeddings_np)
        tsne_df = pd.DataFrame(tsne_results, columns=['TSNE_1', 'TSNE_2'])

        plt.figure(figsize=(8, 6))
        plt.scatter(tsne_df['TSNE_1'], tsne_df['TSNE_2'])
        plt.xlabel('TSNE_1')
        plt.ylabel('TSNE_2')
        plt.title('t-SNE visualization of embeddings')
        plt.show()

model = DistilBertEmbedding("distilbert-base-uncased")
filter_news = FilterNews("Apples stocks and shares", model)
filtered_text = filter_news.filter()



