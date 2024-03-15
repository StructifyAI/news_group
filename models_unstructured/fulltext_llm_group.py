from openai import AsyncOpenAI
import json
import asyncio
import networkx as nx

API_KEY = None

with open('../keys/openai.txt', 'r') as file:
    API_KEY = file.read().strip()

client = AsyncOpenAI(api_key = API_KEY)

headings = []
with open('../tests/news.json', 'r') as file:
    data = json.load(file)
    for article in data['news']:
        headings.append(article['article']['text'])

G = nx.Graph()
G.add_nodes_from([i for i in range(len(headings))])

for i in range(len(headings)):
    print((i, data['news'][i]['article']['title']))
    print()

async def compare_articles(id1, id2, summaries):
    if nx.has_path(G, id1, id2):
        return

    prompt = f"Are these two articles summarizing the same event? Answer only yes or no\n1. {summaries[id1]}\n2. {summaries[id2]}"
    completion = await client.chat.completions.create(
        model="gpt-4-turbo-preview", 
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    response = completion.choices[0].message.content.strip().lower()
    if response == "yes":
        G.add_edge(id1, id2)

async def summarize_articles(heading):
    prompt = f"Please extract key news events from this article. Respond in stricly less than 60 words {heading}"
    completion = await client.chat.completions.create(
        model="gpt-4-turbo-preview", 
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    return completion.choices[0].message.content.strip().lower()

async def process_item(item_index, summaries):
    tasks = [compare_articles(item_index, j, summaries) for j in range(item_index+1, len(summaries))]
    await asyncio.gather(*tasks)

async def main():    
    summaries = await asyncio.gather(*(summarize_articles(heading) for heading in headings))

    for i in range(len(summaries)):
        await process_item(i, summaries)
    
    connected_components = list(nx.connected_components(G))
    for i, component in enumerate(connected_components):
        print("Component: {}".format(i))
        print(component)
        print()

if __name__ == "__main__":
    asyncio.run(main())



