import json
import asyncio
from openai import AsyncOpenAI
import time

class AsyncOpenAIClient:
    def __init__(self, api_key):
        self.client = AsyncOpenAI(api_key=api_key)

    async def compare_headings(self, headings):
        prompt = f"I will give you some news titles. Can you please group the articles that report the exact same event together. Format the answer as : Group1 : [article1, article3, ..]\nGroup2 : [article2, artcile5, ..]..\n. Return the groupings without any additional text.\n"
        for heading in headings:
            prompt += (heading + "\n")
        completion = await self.client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "user", "content": prompt},
            ]
        )
        response = completion.choices[0].message.content.strip().lower()
        return response

class NewsComparison:
    def __init__(self, api_key, headings):
        self.api_client = AsyncOpenAIClient(api_key)
        self.headings = headings
        self.response = None

    async def run(self):
        self.response = await self.api_client.compare_headings(self.headings)

    def print_components(self):
        print(self.response)


API_KEY = None
with open('keys/openai.txt', 'r') as file:
    API_KEY = file.read().strip()

headings = []
with open('../tests/titles.json', 'r') as file:
    data = json.load(file)
    headings = data['article_titles']

if __name__ == "__main__":
    start = time.time()
    news_compare_model = NewsComparison(API_KEY, headings)
    asyncio.run(news_compare_model.run())
    news_compare_model.print_components()
    end = time.time()
    print("Time: ", (end-start))