import json
import asyncio
from openai import AsyncOpenAI
import time


class AsyncOpenAIClient:
    def __init__(self, api_key):
        self.client = AsyncOpenAI(api_key=api_key)

    async def compare_headings(self, heading1, heading2):
        prompt = (f"Are these two news headings reporting the same event? Look at the message behind the heading. "
                  f"Answer only yes or no\n1. {heading1}\n2. {heading2}")
        completion = await self.client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "user", "content": prompt},
            ]
        )
        response = completion.choices[0].message.content.strip().lower()
        return response == "yes"


class UnionFind:
    def __init__(self, size):
        self.parent = [i for i in range(size)]
        self.rank = [0] * size

    def find(self, item):
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, item1, item2):
        root1 = self.find(item1)
        root2 = self.find(item2)
        if root1 != root2:
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            else:
                self.parent[root1] = root2
                if self.rank[root1] == self.rank[root2]:
                    self.rank[root2] += 1

    def connected(self, item1, item2):
        return self.find(item1) == self.find(item2)


class NewsComparison:
    def __init__(self, api_key, headings):
        self.api_client = AsyncOpenAIClient(api_key)
        self.union_find = UnionFind(len(headings))
        self.headings = headings

    async def compare_articles(self, id1, id2):
        if not self.union_find.connected(id1, id2):
            are_similar = await self.api_client.compare_headings(self.headings[id1], self.headings[id2])
            if are_similar:
                self.union_find.union(id1, id2)
    
    async def process_item(self, item_index):
        tasks = [self.compare_articles(item_index, j) for j in range(item_index + 1, len(self.headings))]
        await asyncio.gather(*tasks)

    async def run(self):
        for i in range(len(self.headings)):
            await self.process_item(i)
        self.print_components()

    def print_components(self):
        components = {}
        for i in range(len(self.headings)):
            root = self.union_find.find(i)
            if root not in components:
                components[root] = []
            components[root].append(i)

        for indices in components.values():
            print("Component:")
            print(f"{[self.headings[index] for index in indices]}\n")


with open('keys/openai.txt', 'r') as file:
    OPEN_API_KEY = file.read().strip()

with open('../tests/titles.json', 'r') as file:
    data = json.load(file)
    headings = data['article_titles']

if __name__ == "__main__":
    start = time.time()
    program = NewsComparison(OPEN_API_KEY, headings)
    asyncio.run(program.run())
    end = time.time()
    print("Time: ", (end-start))