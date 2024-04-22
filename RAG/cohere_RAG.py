
import numpy as np

from settings import COHERE_API_KEY
import cohere
from gdrive.gdrive_handler import GspreadHandler



class RAG:
    def __init__(self):
        self.co = cohere.Client(COHERE_API_KEY)
        self.model="embed-english-v3.0"
    
    def get_df(self, sheet_name, worksheet_name):
        gspread_handler = GspreadHandler(credentials_filepath='./gdrive/phrasal-ability-419201-d527372ace3b.json')
        df = gspread_handler.get_sheet_as_df(sheet_name=sheet_name, worksheet_name=worksheet_name)
        df["meta_data"] = df["meta"] + " | " + df["data"]
        return df


    def embed_df(self, df):
        chunks = list(df["meta_data"])

        model="embed-english-v3.0"
        response = self.co.embed(
            texts= chunks,
            model=model,
            input_type="search_document",
            embedding_types=['float']
        )
        embeddings = response.embeddings.float
        print(f"We just computed {len(embeddings)} embeddings.")

        return embeddings
    
    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def query_embedding(self, query):
        # Because the text being embedded is the search query, we set the input type as search_query
        response = self.co.embed(
            texts=[query],
            model=self.model,
            input_type="search_query",
            embedding_types=['float']
        )
        query_embedding = response.embeddings.float[0]
        print("query_embedding: ", query_embedding)
        return query_embedding

    def retrieve(self, query_embedding, embeddings, chunks, top_N = 5):
        # Calculate similarity between the user question & each chunk
        similarities = [self.cosine_similarity(query_embedding, chunk) for chunk in embeddings]
        print("similarity scores: ", similarities)

        # Get indices of the top 10 most similar chunks
        sorted_indices = np.argsort(similarities)[::-1]

        # Keep only the top 10 indices
        top_indices = sorted_indices[:top_N]

        # Retrieve the top 10 most similar chunks
        top_chunks_after_retrieval = [chunks[i] for i in top_indices]
        print(f"Here are the top {top_N} inventories after retrieval: ")
        for t in top_chunks_after_retrieval:
            print("== " + t)

        return top_chunks_after_retrieval
    

    def augmented_generation(self,query, top_chunks_after_retrieval):
        # preamble containing instructions about the task and the desired style for the output.
        preamble = """
        ## Task & Context
        You help people answer their questions and other requests interactively. You will be asked a very wide array of requests on all kinds of topics. You will be equipped with a wide range of search engines or similar tools to help you, which you use to research your answer. You should focus on serving the user's needs as best you can, which will be wide-ranging.

        ## Style Guide
        Unless the user asks for a different style of answer, you should answer in full sentences, using proper grammar and spelling.
        """

        # retrieved documents
        documents = [
            {"title": "activity 1", "snippet": top_chunks_after_retrieval[0]},
            {"title": "activity 2", "snippet": top_chunks_after_retrieval[1]},
            {"title": "activity 3", "snippet": top_chunks_after_retrieval[2]},
        ]

        # get model response
        response = self.co.chat(
        message=query,
        documents=documents,
        preamble=preamble,
        model="command-r",
        temperature=0.3
        )

        print("Search Database result:")
        print(response.text)

        return response.text
    

    def rag_pipeline(self, query, sheet_name, worksheet_name):
        df = self.get_df(sheet_name, worksheet_name)
        embeddings = self.embed_df(df)
        query_embedding = self.query_embedding(query)
        top_chunks_after_retrieval = self.retrieve(query_embedding, embeddings, list(df["meta_data"]))
        response = self.augmented_generation(query, top_chunks_after_retrieval)
        return response