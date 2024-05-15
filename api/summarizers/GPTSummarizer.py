import os

from dotenv import load_dotenv
from openai import OpenAI

class GPTSummarizer:
    def __init__(self) -> None:
        load_dotenv()
        secret_key = os.getenv('OPENAI_SECRET_KEY')
        self.client = OpenAI(api_key=secret_key)
        
    def summarize(self, text):
        system_msg = 'You are a text summarizer'
        user_msg = 'Summarize the following text: "' + text + '". Return only the summarized text. The summarized text cannot be greater than 48 words. '
        
        response = self.client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content':system_msg},
                {'role': 'user', 'content':user_msg}
            ],
            stop=None
        )
        summary = response.choices[0].message.content
        return summary