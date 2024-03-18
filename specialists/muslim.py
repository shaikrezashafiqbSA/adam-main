import pandas as pd
from utils import pickle_helper

from llm_handler.GHandler import GHandler
from settings import GEMINI_API_KEY

class Muslim:
    def __init__(self, specialist_LLM_model = "GEMINI"):
        self.db_path = "./database/muslim/Sunan al Tirmidhi.csv"
        self.state_path = "./database/muslim/"
        self.tables = {}
        self.specialist_LLM_model = specialist_LLM_model
        self.specialist_LLM = self.set_specialist_model(model = self.specialist_LLM_model)
        self.embedding_model = "models/embedding-001"

    def set_specialist_model(self, model = "GEMINI"):
        if model == "GEMINI":
            model_specialist = GHandler(GEMINI_API_KEY,                  
                            generation_config = {"temperature": 0.9,
                                                "top_p": 0.95,
                                                "top_k": 40,
                                                "max_output_tokens": 1024,
                                                },
                            block_threshold="BLOCK_NONE",
                            )
        else:
            raise ValueError("LLM not recognised - Not integrated")
        self.model_specialist = model_specialist


    def load_data_model(self, reembed = False, sheet_image_columns = None):
        print("loading specialist: MUSLIM ...")
        if reembed:
            # prep the data model
            self.prep_data_model()

            # embed the data model
            self.embed_data_model(embedding_model = self.embedding_model)
        else: 
            try:
                print("MUSLIM data model embedded - SAVING MUSLIM STATE") 
                pickle_helper.pickle_this(data=None, pickle_name="MUSLIM_STATE_0", path=self.state_path)
                print("MUSLIM STATE LOADED")
            except Exception as e:
                raise ValueError(f"MUSLIM STATE NOT FOUND: {e} - Please embed the data model first")
    


    def prep_data_model(self,):
        """
        This function will ensure the data model is ready to be embedded
        this includes any data cleaning, data wrangling, etc
        ultimately the data model will be a dictionary of dataframes with the following structure:
        "Title" "text" 

        for now can make it simple, just "CLIENT ID" as the title and everything else as the text with the format:
        "Title" "text" 
        where "text" = str combine all column values in the row in the format: "column_1: value, column_2: value, column_3: value, ..."

        """
        # load all tables into a dictionary of dataframes
        self.tables = self.get_table(sheet_name="Sunan al Tirmidhi")  
         
        for tab in self.tables:
            df = self.tables[tab]
            df = df.fillna("")
            # df["Text"] = df.apply(lambda row: ", ".join([f"{col}: {row[col]}" for col in df.columns]), axis=1)
            df["Text"] = df.apply(lambda row: ", ".join([f"{row[col]}" for col in df.columns]), axis=1)
            self.tables[tab] = df

        print("data model ready for contextualising")

    def get_table(self, sheet_name: str = None):
        tables = {}
        if ".csv" in self.db_path:
            df = pd.read_csv(self.db_path)
            tables[sheet_name] = df
        elif ".xlsx" in self.db_path:
            tabs = self.get_table_names()
            df = pd.read_excel(self.db_path, sheet_name=sheet_name)
            for tab in tabs:
                tables[tab] = self.get_table(tab)
        return tables
    
    def get_table_names(self,):
        if ".xlsx" in self.db_path:
            tabs = pd.ExcelFile(self.db_path).sheet_names
            tabs = [sheet for sheet in tabs if "TEST" in sheet]
            return tabs
        

    
    def embed_data_model(self, embedding_model = None):
        if embedding_model is None:
            embedding_model = self.embedding_model
        # TO be generalised but for now just do loop
        sheet = "Sunan al Tirmidhi"
        # CLIENT table
        print(f"MUSLIM embedding: {sheet}")
        # make an ID column with index
        self.tables[sheet]["ID"] = self.tables[sheet].index
        self.tables[sheet] = self.model_specialist.embed_df(self.tables[sheet],
                                                        title = "ID", 
                                                        text = "Text",
                                                        model=embedding_model)

        # print(f"MUSLIM embedding: {client_request}")
        # self.tables[client_request] = self.model_specialist.embed_df(self.tables[client_request],
        #                                                 title = "CLIENT ID", 
        #                                                 text = "Text",
        #                                                 model=embedding_model)
        
        # print(f"MUSLIM embedding: {flights}")
        # self.tables[flights] = self.model_specialist.embed_df(self.tables[flights],
        #                                                 title = "FLIGHT ID", 
        #                                                 text = "Text",
        #                                                 model=embedding_model)
        
        # print(f"MUSLIM embedding: {accomodations}")
        # self.tables[accomodations] = self.model_specialist.embed_df(self.tables[accomodations],
        #                                                 title = "ACCOMODATION ID", 
        #                                                 text = "Text",
        #                                                 model=embedding_model)
        
        # print(f"MUSLIM embedding: {activities}")
        # self.tables[activities] = self.model_specialist.embed_df(self.tables[activities],
        #                                                 title = "SERVICE ID", 
        #                                                 text = "Text",
        #                                                 model=embedding_model)
        
        print("MUSLIM data model embedded - SAVING MUSLIM STATE") 
        pickle_helper.pickle_this(data=self.tables, pickle_name="MUSLIM_STATE_0", path= self.state_path)
        print("MUSLIM STATE SAVED")

    def search_context_data(self, 
              context_data, 
              query,
              topN = 3,
              task_type = "retrieval_query"):
        """
        This function will search the specialist database for the topN most relevant results given the user prompt X
        and the context data
        """
        # get the topN most relevant results
        topN_results = self.specialist_LLM.find_best_passage(query = query, 
                                                             dataframe = context_data, 
                                                             topN = topN,
                                                             task_type = task_type,
                                                             model = self.embedding_model)
        return topN_results

    
