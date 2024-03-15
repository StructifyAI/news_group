from openai import AsyncOpenAI
import json
import asyncio
import networkx as nx

API_KEY = None

with open('../keys/openai.txt', 'r') as file:
    API_KEY = file.read().strip()

client = AsyncOpenAI(api_key = API_KEY)

with open('../tests/titles.json', 'r') as file:
    data = json.load(file)
    headings = data['article_titles']

print(headings)
G = nx.Graph()
G.add_nodes_from(headings)

async def compare_articles(id1, id2):
    if nx.has_path(G, headings[id1], headings[id2]):
        return
    print("Compared", id1, id2)
    prompt = f"Are these two news headings reporting the same event? Look at the message behind the heading. Answer only yes or no\n1. {headings[id1]}\n2. {headings[id2]}"
    completion = await client.chat.completions.create(
        model="gpt-4-turbo-preview", 
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    response = completion.choices[0].message.content.strip().lower()
    if response == "yes":
        G.add_edge(headings[id1], headings[id2])

async def process_item(item_index):
    tasks = [compare_articles(item_index, j) for j in range(item_index+1, len(headings))]
    await asyncio.gather(*tasks)

async def main():    
    for i in range(len(headings)):
        await process_item(i)
    
    connected_components = list(nx.connected_components(G))
    for i, component in enumerate(connected_components):
        print("Component: {}".format(i))
        print(component)
        print()

if __name__ == "__main__":
    asyncio.run(main())
