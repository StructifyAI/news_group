import json
import asyncio
from openai import AsyncOpenAI
from news_api.retrive_news import NewsQuery, NewsApiWrapper

with open('keys/newsapi.txt', 'r') as file:
    NEWS_API_KEY = file.read().strip()

with open('keys/openai.txt', 'r') as file:
    OPEN_API_KEY = file.read().strip()


class AsyncOpenAiWrapper:
    def __init__(self, api_key):
        self.client = AsyncOpenAI(api_key=api_key)

    async def summarize_article(self, article_text, index):
        if len(article_text) > 100:
            prompt = f"Please extract key news events from this article. Respond in strictly less than 60 words {article_text}"
            completion = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
            )
            article_text[index] = completion.choices[0].message.content.strip().lower()

    async def compare_summaries(self, summary1, summary2):
        prompt = f"Are these two articles summarizing the same event? Answer only yes or no\n1. {summary1}\n2. {summary2}"
        completion = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
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


class NewsSummarizeAndCompare:
    def __init__(self, api_key, data):
        self.api_client = AsyncOpenAiWrapper(api_key)
        self.union_find = UnionFind(len(data))
        self.data = data
        self.text = []
        for article in data:
            if article['description']:
                self.text.append(article['title'] + article['description'])
            else:
                self.text.append(article['title'])

    async def process_item(self, item_index, summaries):
        tasks = [self.compare_articles(item_index, j, summaries) for j in range(item_index + 1, len(summaries))]
        await asyncio.gather(*tasks)

    async def compare_articles(self, id1, id2, summaries):
        if not self.union_find.connected(id1, id2):
            are_similar = await self.api_client.compare_summaries(summaries[id1], summaries[id2])
            if are_similar:
                self.union_find.union(id1, id2)

    async def print_components_and_titles(self):
        components = {}
        for i in range(len(self.data)):
            root = self.union_find.find(i)
            components.setdefault(root, []).append(i)

        file_name = 'news_groupings.json'
        with open(file_name, 'w') as outfile:
            json.dump(components, outfile, indent=4)

        for i, indices in enumerate(components.values()):
            print(f"Component {i}:")
            print(f"{[self.data[index]['title'] for index in indices]}\n")

    async def run(self):
        await asyncio.gather(*(self.api_client.summarize_article(self.text, i) for i, _ in enumerate(self.text)))
        for i in range(len(self.text)):
            await self.process_item(i, self.text)
        await self.print_components_and_titles()


def retrieve_news_articles(keyword, context="", from_date="", to_date="", language='en'):
    query = NewsQuery(keyword=keyword, context=context, from_date=from_date, to_date=to_date, language=language)
    news_api_wrapper = NewsApiWrapper(NEWS_API_KEY)
    response = news_api_wrapper.execute_query(query)

    with open("news_results.json", "w") as outfile:
        outfile.write(json.dumps(response, indent=4))


if __name__ == "__main__":
    retrieve_news_articles(keyword="IPL", context="Cricket", from_date="2024-03-26")
    with open('news_results.json', 'r') as file:
        data = json.load(file)

    program = NewsSummarizeAndCompare(OPEN_API_KEY, data["articles"][0:25])
    asyncio.run(program.run())
