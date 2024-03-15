import json
import asyncio
from openai import AsyncOpenAI
import networkx as nx
import time

class AsyncOpenAIClient:
    def __init__(self, api_key):
        self.client = AsyncOpenAI(api_key=api_key)

    async def compare_headings(self, heading1, heading2):
        prompt = f"Are these two news headings reporting the same event? Look at the message behind the heading. Answer only yes or no\n1. {heading1}\n2. {heading2}"
        completion = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview", 
            messages=[
                {"role": "user", "content": prompt},
            ]
        )
        response = completion.choices[0].message.content.strip().lower()
        return response == "yes"

class NewsGraphManager:
    def __init__(self, headings):
        self.G = nx.Graph()
        self.G.add_nodes_from(headings)
    
    def add_comparison(self, heading1, heading2, are_similar):
        if are_similar and not nx.has_path(self.G, heading1, heading2):
            self.G.add_edge(heading1, heading2)
    
    def print_components(self):
        connected_components = list(nx.connected_components(self.G))
        for i, component in enumerate(connected_components):
            print(f"Component {i}:")
            print(f"{component} \n")

class NewsComparison:
    def __init__(self, api_key, headings):
        self.api_client = AsyncOpenAIClient(api_key)
        self.graph_manager = NewsGraphManager(headings)
        self.headings = headings

    async def compare_articles(self, id1, id2):
        if not nx.has_path(self.graph_manager.G, self.headings[id1], self.headings[id2]):
            are_similar = await self.api_client.compare_headings(self.headings[id1], self.headings[id2])
            self.graph_manager.add_comparison(self.headings[id1], self.headings[id2], are_similar)
    
    async def process_item(self, item_index, headings):
        tasks = [self.compare_articles(item_index, j) for j in range(item_index + 1, len(headings))]
        await asyncio.gather(*tasks)

    async def run(self, headings):
        for i in range(len(headings)):
            await self.process_item(i, headings)
        self.graph_manager.print_components()

API_KEY = None
with open('../keys/openai.txt', 'r') as file:
    API_KEY = file.read().strip()

headings = []
with open('../tests/titles.json', 'r') as file:
    data = json.load(file)
    headings = data['article_titles']

if __name__ == "__main__":
    start = time.time()
    program = NewsComparison(API_KEY, headings)
    asyncio.run(program.run(headings))
    end = time.time()
    print("Time: ", (end-start))