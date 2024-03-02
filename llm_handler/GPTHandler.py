import time

import openai
from settings import OPENAI_API_KEY
from utils.json_search import json_search
from ABCs.llm_abc import AbstractLLMHandler
from logger.logger import logger
class GPTHandler(AbstractLLMHandler):
    def __init__(self, 
                 settings: dict = {"model":"gpt-3.5-turbo",
                                   "temperature":0}, 
                 credentials: list = [OPENAI_API_KEY]):
        self.credentials = credentials
        self.settings = settings
        self.connect_to_LLM()

    def connect_to_LLM(self):
        openai.api_key = self.credentials[0]

    def generate_image(self,
                       prompt: str,
                       size="1024x1024",):
        
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size=size
        )
        image_url = response['data'][0]['url']
        return image_url


    def send_prompt(self,
                    prompt: dict):
        #  TODO: Messages accept more lists input, so to generalise this further later
        if type(prompt) == str:
            messages = [{"role": "user", "content": prompt}]
        else:
            messages= prompt
            # functions = prompt["functions"]
        t0 = time.time()
        try:
            response = openai.ChatCompletion.create(model= self.settings["model"],
                                                    temperature= self.settings["temperature"],
                                                    messages= messages, 
                                                    )
            content = response.choices[0]["message"]["content"]
            LLM_status = "SUCCESS"
            t1 = round(time.time() - t0, 3)
            return {"content": content, "json_content": json_search(content),"response":response, "time_taken":t1, "LLM_status": LLM_status}
    
        except Exception as e:
            print(e)
            response = f" Error: " + str(e)
            LLM_status = "ERROR"
            raise Exception(e)
        