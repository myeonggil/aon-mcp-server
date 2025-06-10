from typing import AsyncGenerator, Any

from groq import AsyncGroq
from groq.types.chat import ChatCompletion

from configs import config


class AONModel:
    def __init__(self):
        self.async_groq = AsyncGroq(api_key=config["GROQ_API_KEY"])

    async def get_chat_completion(self, prompt: str, stream: bool) -> AsyncGenerator | ChatCompletion:
        response = await self.async_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Keep all responses under 512 tokens."
                },
                # {
                #     "role": "assistant",
                # },
                {
                    "role": "user",
                    "content": prompt
                },
                # {
                #     "role": "user",
                #     "content": "Please answer smaller than 512 tokens"
                # }
            ],
            stream=stream,
            timeout=5,
            temperature=0.05, # more lower focus on consistency, more higher focus on newer answer
            max_tokens=512, # response maximum token length(different by language) Between 512 and 1024
            top_p=1,    # random response match temperature 
            frequency_penalty=0,    # more lower use unique word
            presence_penalty=0  # more lower use similar and repeat word
        )
        return response
