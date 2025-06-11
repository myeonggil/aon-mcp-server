from pymongo import AsyncMongoClient
from configs import config

# 비동기 클라이언트 설정
MONGO_URI = config['MONGO_URI']
USERNAME = config['USERNAME']
PASSWORD = config['PASSWORD']
MONGO_URI = MONGO_URI.replace(
    '<username>', USERNAME
).replace(
    '<password>', PASSWORD
)


class MongoDBCluster:
    def __init__(self):
        self.client = AsyncMongoClient(MONGO_URI)
        self.db = self.client['chatbot']
        self.collection = self.db['chat_history']

    async def close(self):
        await self.client.close()

    async def get_context_string_from_docs(self, embedded_query: list[float]) -> str:
        context_docs = await self.search_vector(embedded_query=embedded_query)
        context_string = " ".join([doc["text"] for doc in context_docs])
        return context_string

    async def search_vector(self, embedded_query: list[float]):
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "queryVector": embedded_query,
                    "path": "embedding",
                    "exact": True,
                    "limit": 5
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "text": 1
                }
            }
        ]
        array_of_results = []
        async for doc in await self.collection.aggregate(pipeline=pipeline):
            array_of_results.append(doc)
        return array_of_results
