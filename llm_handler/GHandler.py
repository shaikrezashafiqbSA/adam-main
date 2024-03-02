"""
At the command line, only need to run once to install the package via pip:

$ pip install google-generativeai
"""
    

import numpy as np
import pandas as pd


from pathlib import Path
import google.generativeai as genai


class GHandler:
    def __init__(self, API_KEY):
        self.API_KEY = API_KEY
        self.generation_config = {
                                "temperature": 0.9,
                                "top_p": 0.95,
                                "top_k": 40,
                                "max_output_tokens": 1024,
                                }
        self.safety_settings = [
            {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        
    def build_model(self, model_name,):
        genai.configure(api_key = self.API_KEY)

        model = genai.GenerativeModel(model_name=model_name,
                                        generation_config=self.generation_config,
                                        safety_settings=self.safety_settings)
        
        return model
    

    def show_available_models(self,):
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)


    def prompt(self, prompt,model_name="gemini-pro"):
        model = self.build_model(model_name)
        response = model.generate_content(prompt)
        # print(response.text)
        return response
    

    def prompt_image(self, 
                      image_path, 
                      prompt_1,
                      prompt_2 = None,
                      model_name="gemini-pro-vision",
                      generation_config = {
                                            "temperature": 0.9,
                                            "top_p": 0.95,
                                            "top_k": 40,
                                            "max_output_tokens": 1024,
                                            },
                      safety_settings = [
                                        {
                                        "category": "HARM_CATEGORY_HARASSMENT",
                                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                                        },
                                        {
                                        "category": "HARM_CATEGORY_HATE_SPEECH",
                                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                                        },
                                        {
                                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                                        },
                                        {
                                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                                        },
                                        ]

        ):
        genai.configure(api_key = self.API_KEY)
        # Set up the model
        model = genai.GenerativeModel(model_name=model_name,
                                        generation_config=generation_config,
                                        safety_settings=safety_settings)

        # Validate that an image is present
        if not (img := Path(image_path)).exists():
            raise FileNotFoundError(f"Could not find image: {img}")

        image_parts = [
            {
            "mime_type": "image/jpeg",
            "data": Path(image_path).read_bytes()
            },
        ]

        if prompt_2 is None:
            prompt_parts = [
                prompt_1,
                image_parts[0],
            ]
        else:
            prompt_parts = [
                prompt_1,
                image_parts[0],
                prompt_2,
            ]

        response = model.generate_content(prompt_parts)
        return response


    def ingest_google_sheet():
        # READ FROM GOOGLE DRIVE URL
        df = pd.read_csv('https://docs.google.com/spreadsheets/d/1pw96y3hZrI9jjxanfagu1cr9aioxRc2P25h00MzR72M/edit#gid=0')
        # read from .xlsx file from .\database\travel\travel.xlsx
        # get first sheet and 2nd sheet as 2 dataframes
        hotels_df = pd.read_excel(r'./database/travel/travel.xlsx', sheet_name="Hotels")
        day_trips_df = pd.read_excel(r'./database/travel/travel.xlsx', sheet_name="Day Trip")


    def image_travel_analyse(self, 
                             image_path, 
                             prompt = """
                                        You are a helpful and informative concierge bot that consumes images of travel destinations
                                        and outputs the logistics required in enjoying the travel destination.
                                        Essentially: the logistics of the day trips first then work backwards to the hotel and flight.
                                      """,
                             additional_prompt = ""):
        response = self.analyse_image(image_path, prompt + additional_prompt)
        print(response.text)
        return response
    
    def _embed_fn(self,
                  title,
                  text,
                  model='models/embedding-001', ):
        """
        Usage: 
            df['Embeddings'] = df.apply(lambda row: embed_fn(row['Title'], row['Text']), axis=1)
            df
        """
        return genai.embed_content(model=model,
                                    content=text,
                                    task_type="retrieval_document",
                                    title=title)["embedding"]
    
    def embed_df(self,
                 df,
                 title="Title",
                 text="Text",
                 model='models/embedding-001', ):
        assert title in df.columns, f"title: '{title}' column not found in dataframe"
        assert text in df.columns, f"text: '{text}' column not found in dataframe"
        

        df['Embeddings'] = df.apply(lambda row: self._embed_fn(row[title], row[text], model=model), axis=1)

        return df

    # Document SEARCH WITH Q&A

    def retrieval_query(self, query):
        model = 'models/embedding-001'

        request = genai.embed_content(model=model,
                                    content=query,
                                    task_type="retrieval_query")
        
    def find_best_passage(self,
                          query, 
                          dataframe, 
                          task_type="retrieval_query",
                          model='models/embedding-001'):
        """
        Compute the distances between the query and each document in the dataframe
        using the dot product.
        """
        query_embedding = genai.embed_content(model=model,
                                                content=query,
                                                task_type=task_type)
        dot_products = np.dot(np.stack(dataframe['Embeddings']), query_embedding["embedding"])
        idx = np.argmax(dot_products)
        return dataframe.iloc[idx]['Text'] # Return text from index with max value
    
    def build_knowledgebase(self,
                            data,
                            knowledge_domain = "travel", 
                            data_type = "csv"):
        """
        This is a higher level function that when called,
        will allow the user to input any kind of unstructured or structured data 
        (images, pdf, excel sheets, word documents, etc)

        The function will automatically process the data and store it in a structured format
        for further embedding and retrieval queries. 

        The knowledge_domain will specify the kind of data that the user is inputting.
        So if the user is inputting travel data, the knowledge_domain will be "travel"
        if the user is inputting islamic data, the knowledge_domain will be "islam"

        This way the user can input any kind of data and the function will automatically process it
        and store it in a structured format for further retrieval queries.
        """
        
        if data_type != "csv":
            raise ValueError("Data type not supported. Please input a csv file")
        else:
            df = pd.read_csv(data)
            df = self.clean_df(df)
            df = self.embed_df(df)
            return df

    def clean_process_df(self, df):
        df.apply(lambda row: ', '.join([f"{col}: {row[col]}" for col in df.columns]), axis=1)

    
