import textwrap
import pandas as pd
from pprint import pprint 
from settings import GEMINI_API_KEY
from llm_handler.GHandler import GHandler

from specialists.traveller import Traveller 


class Librarian:
    def __init__(self, 
                 librarian_LLM_model = "GEMINI", 
                ):
        
        """
        RAG Application LIBRARIAN 
        1) Given a user prompt X, you will primarily use the given CONTEXT data to provide the user with the topN results.
        2) Augment your answers with the CONTEXT data first and then use your own intrinsic knowledge.
        3) So produce an answer in the following format: 
            "Based on the CONTEXT data, I found the following information on X:
            ... 
            Based on my intrinsic knowledge, I also found the following information on X:
            ... "
        4) The CONTEXT data can be a .csv file, a .txt file, a .xlsx file, a link, an image, etc
        5) The user prompt X can be a question, a statement, a command, etc
        6) The topN results can be the topN most relevant results from the CONTEXT data, or the topN most relevant results from the LLM
        12) Finally wrap up the topN results in a nice format and present to the user

        AI DATA MODEL: 
        1) Simpleton (LLM context only)             -    LLM(prompt, context_data = NONE)           -> text
        2) Contextualist (limited by token limit)   -    LLM(prompt, context_data = context_data_i) -> text  
        3) Librarian:                               -    LLM(prompt, context_data = Recommendation_Engine(context_data, scope)) -> text
        
        where Recommendation_Engine(prompt_context)_scope generates all possible sets of context data WITHIN scope. 
        - This function will return the topN most relevant (scope) context data to the prompt_context 

        CHAIN/CONVERSATIONAL MODEL:
        1-chain (Aloof librarian):
        - set librarian context -> Librarian(prompt, context_data = Recommendation_Engine(context_data, scope))  -> Librarian_reply
        2-chain (Curious librarian - with self-awareness):
            - set librarian context -> Librarian(prompt, context_data = Recommendation_Engine(context_data, scope))  -> Librarian_reply 
            Then take 
            - Librarian(prompt + Librarian_reply, context_data = Recommendation_Engine(context_data, scope)) -> Librarian_reply_with_selfAwareness

        1_2 chain (cross-disciplinary librarian):
            - set librarian context -> Librarian(prompt, context_data = Recommendation_Engine(context_datas, scope_3))  -> Librarian_reply
        where context_datas = Recommendation_Engine(context_data_1, scope_1) + Recommendation_Engine(context_data_2, scope_2)

        OR ANY OTHER PERMUTATIONS to form a comprehensive DATA-centric conversation model
        
        """
            
        self.librarian_LLM_model = librarian_LLM_model
        self.model_librarian = self.set_librarian_model(LLM = self.librarian_LLM_model)

    def set_librarian_model(self, LLM = "GEMINI"):
        """
        This function will initialise the model_librarian with the correct model
        """
        
        if LLM == "GEMINI":
            self.model_librarian = GHandler(GEMINI_API_KEY,                  
                                            generation_config = {"temperature": 0.9,
                                                                "top_p": 0.95,
                                                                "top_k": 40,
                                                                "max_output_tokens": 1024,
                                                                },
                                            block_threshold="BLOCK_NONE",
                                            )
        else:
            raise ValueError("LLM not recognised - Not integrated")
        
        return self.model_librarian
                                   

    def select_specialist(self, specialist: str, specialist_LLM_model = "GEMINI"):
        """
        This will be main entry point for data ingestion for X_context_source
        so this could be a link, or an image, or a .xlsx or .csv file or a .txt file
        """ 
        if specialist == "traveller":
            # This will be the Subject matter expert
            self.Traveller = Traveller(specialist_LLM_model = specialist_LLM_model)
        else:
            raise ValueError(f"specialist {specialist} not recognised - Not integrated")
        
    def make_prompt(self,query, relevant_passage):
        librarian_contextualisation_prompt = """
        You are a librarian, and you are tasked to provide information on a given topic X,
        given a set of CONTEXT data
        So given a user prompt X, you will primarily use the given CONTEXT data (which is a topN result) to provide the user with insightful response.
        Augment your answers with the CONTEXT data first and then use your own intrinsic knowledge. 
        So produce an answer in the following format: 
        "Based on the CONTEXT data, I found the following information on X:
        ... 
        Based on my intrinsic knowledge, I also found the following information on X:
        ... """
        
        
        escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
        # prompt = textwrap.dedent("""You are a helpful and informative bot that answers questions using text from the reference passage included below. \
        # Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
        # However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
        # strike a friendly and converstional tone. \
        # If the passage is irrelevant to the answer, you may ignore it.
        # QUESTION: '{query}'
        # PASSAGE: '{relevant_passage}'

        #     ANSWER:
        # """).format(query=query, relevant_passage=escaped)

        prompt = textwrap.dedent("""You are a librarian, who has access to various sources of embedded information and recommendations from specialists.\
        You are tasked to provide information on a given QUESTION, given a set of relevant PASSAGE data which is a topN result from a specialist.\
        You will primarily use the given PASSAGE data (which is a topN result) to provide the user with insightful response.\
        Augment your answers with the PASSAGE data first and then use your own intrinsic knowledge (if dont have, then ignore) \
        Be sure to respond in a complete sentence, being comprehensive, including all relevant background information.\
        QUESTION: '{query}'
        PASSAGE: '{relevant_passage}'

            ANSWER:
        """).format(query=query, relevant_passage=escaped)

        return prompt

    def ask(self, prompt, vibe: str, context_data = "TEST - CLIENT",topN= 1, model_tier = "gemini-pro"):
        """
        This function will be the main entry point for the librarian to provide the user with the topN results.
        Augment your answers with the CONTEXT data first and then use your own intrinsic knowledge. 
        So produce an answer in the following format: 
        "Based on the CONTEXT data, I found the following information on X:
        ... 
        Based on my intrinsic knowledge, I also found the following information on X:
        ... "
        """
        specialist_recommendations_series = self.specialist.search_context_data(context_data = context_data, vibe=vibe, topN=topN,)
        specialist_recommendations = '\n'.join(specialist_recommendations_series)

        prompt = self.make_prompt(prompt, specialist_recommendations)

        response = self.model_librarian.prompt(prompt, model_name = model_tier)
        pprint(response.text)
        return {"prompt":prompt, "response":response, "specialist_recommendations":specialist_recommendations}


    # def convo_add(self, X, Y):
    #     prompt = f"Give me information on {X}, given {Y}"
    #     response = self.model_librarian.prompt(prompt)
    #     return response

    # def deep_search(self):
    #     return f"Hey AI, give me information on {self.X}, given {self.context_population} and give me the top {self.topN} results"
    

