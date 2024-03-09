import pandas as pd
from utils import pickle_helper
from pprint import pprint
from llm_handler.GHandler import GHandler
from settings import GEMINI_API_KEY

class Traveller:
    def __init__(self, 
                 specialist_LLM_model = "GEMINI",
                 db_path = "./database/travel/SWTT_ Master Database.xlsx",
                 state_path = "./database/travel/",
                 embedding_model = "models/embedding-001"
                 ):
        self.db_path = db_path
        self.state_path = state_path
        self.embedding_model = embedding_model


        self.tables = {}
        self.specialist_LLM_model = specialist_LLM_model
        self.model_specialist = self.set_specialist_model(model = self.specialist_LLM_model)

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
        return model_specialist


    def load_data_model(self, 
                        reembed = False,
                        embed_id = 0,
                        data_model_keys = {"TEST - CLIENT":"CLIENT ID",
                                                  "TEST - CLIENT REQUEST":"CLIENT ID",
                                                  "TEST - FLIGHTS":"FLIGHT ID",
                                                  "TEST - ACCOMODATIONS":"HOTEL ID",
                                                  "TEST - SERVICES":"SERVICE ID",
                                                  }
                        ):
        
        print("loading specialist: TRAVELLER ...")
        if reembed:
            # prep the data model
            self.tables = self.prep_data_model(data_model_keys=data_model_keys)
            # print(self.tables)
            # embed the data model
            self.tables = self.embed_data_model(self.tables,reembed=reembed,embed_id = embed_id, embedding_model = self.embedding_model)
        else: 
            try:
                self.tables = pickle_helper.pickle_this(data=None, pickle_name=f"TRAVELLER_STATE_{embed_id}", path=self.state_path)
            except Exception as e:
                raise ValueError(f"TRAVELLER STATE NOT FOUND: {e} - Please embed the data model first")
            print("TRAVELLER loaded")
    # =====================================================================
    # DATA MODEL PREPROCESSING
    # =====================================================================

    def get_table(self, sheet_name: str):
        df = pd.read_excel(self.db_path, sheet_name=sheet_name)
        return df
    
    def get_table_names(self,):
        tabs = pd.ExcelFile(self.db_path).sheet_names 
        tabs = [sheet for sheet in tabs if "TEST" in sheet]
        return tabs
    
    def prep_data_model(self,         
                        data_model_keys = {"TEST - CLIENT":"CLIENT ID",
                                                  "TEST - CLIENT REQUEST":"CLIENT ID",
                                                  "TEST - FLIGHTS":"FLIGHT ID",
                                                  "TEST - ACCOMODATIONS":"ACCOMODATION ID",
                                                  "TEST - SERVICES":"SERVICE ID",
                                                  },
                        verbose = True,
                        ):
        """
        This function will ensure the data model is ready to be embedded
        this includes any data cleaning, data wrangling, etc
        ultimately the data model will be a dictionary of dataframes with the following structure:
        "Title" "text" 

        for now can make it simple, just "CLIENT ID" as the title and everything else as the text with the format:
        "Title" "text" 
        where "text" = str combine all column values in the row in the format: "column_1: value, column_2: value, column_3: value, ..."

        """

        #  DATA LOADING -----------------------------------------------------
        tabs = self.get_table_names()
        print(f"tables: \n{tabs}")
        tables = self.tables
        # load all tables into a dictionary of dataframes
        for tab in tabs:
            tables[tab] = self.get_table(tab)
        print("tables loaded into memory")    

        #  DATA PREPROCESSING ------------------------------------------------
        for tab in self.tables:
            df = self.tables[tab]
            # Chunk all the columns into a single text column
            df["Text"] = df.apply(lambda row: ", ".join([f"{col}: {row[col]}" for col in df.columns]), axis=1)
            # set the title
            df["Title"] = df[data_model_keys[tab]]
            # ensure Title has no NaNs or None
            df["Title"] = df["Title"].dropna()
            # drop everything except for the title and text
            df = df[["Title", "Text"]] # would this reduce ram? or should i just keep the original df? ans: yes it would reduce ram but not by much but it would make the data model more efficient
            # print col names and number of rows
            if verbose:
                print(f"tab: {tab} - {df.columns} - {len(df)}")
            tables[tab] = df

        print("data model ready for embedding")
        return tables

    # =====================================================================
    # EMBEDDINGS
    # =====================================================================

    def embed_data_model(self, tables, reembed=False, embedding_model = None, embed_id = 0):
        if embedding_model is None:
            embedding_model = self.embedding_model

        for embed_step_id,tab in enumerate(tables.keys()):
            print(f"TRAVELLER embedding: {tab}")
            if reembed: 
                try:
                    tables[tab] = self.model_specialist.embed_df(tables[tab],
                                                                title = "Title", 
                                                                text = "Text",
                                                                model=embedding_model)
                except Exception as e:
                    raise ValueError(f"Embed_df FAILED: \n{e}\n - Please investigate and debug the error")
            else:
                tables[tab] = pickle_helper.pickle_this(f"TRAVELLER_STATE_{embed_id}{embed_step_id}", path=self.state_path)
            if embed_step_id == len(tables) - 1:
                embed_step_id=""
            pickle_helper.pickle_this(data=tables, pickle_name=f"TRAVELLER_STATE_{embed_id}{embed_step_id}", path=self.state_path)
            print(f"TRAVELLER embedding: {tab} ({embed_id}{embed_step_id}) - SAVED")
        print(f"TRAVELLER_STATE_{embed_id}{embed_step_id} - SAVED in {self.state_path}")
        return tables


    def search_context_data(self, 
              context_data, 
              content,
              topN = 3,
              task_type = "retrieval_query"):
        """
        This function will search the specialist database for the topN most relevant results given the user prompt X
        and the context data
        """
        # get the topN most relevant results
        topN_results = self.model_specialist.find_best_passage(content = content, 
                                                               dataframe = self.tables[context_data], 
                                                               topN = topN,
                                                               task_type = task_type,
                                                               model = self.embedding_model
                                                               )
        # if topN_results is a pandas series then join it into a string
        if isinstance(topN_results, pd.Series):
            topN_results = '\n'.join(topN_results)
        elif isinstance(topN_results, str):
            topN_results = topN_results
        return topN_results

    
    # =====================================================================
    # TRAVELLER MAIN SKILLS
    # =====================================================================


    # ---------------------------------------------------------------------
    # LEVEL 1 SKILLS
    # ---------------------------------------------------------------------

    def I_recommend_flights(self, 
                          travel_proposal,
                          topN = 3, 
                          task_type = "retrieval_query"):
        """
        This function will recommend the topN most relevant flights given the client request
        """
        context_data = "TEST - FLIGHTS"

        content = f"""
        I have an inventory for a {travel_proposal}. 
        I can recommend you the longest flight based on the location of the activity.
        """

        return self.search_context_data(context_data = context_data, 
                                        content = content,
                                        topN = topN,
                                        task_type = task_type)
    
    def I_recommend_accomodations(self,
                                travel_proposal,
                                topN = 3, 
                                task_type = "retrieval_query"):
        """
        This function will recommend the topN most relevant accomodations given the client request
        """
        context_data = "TEST - ACCOMODATIONS"

        content = f"""
        I have an inventory for a {travel_proposal}. 
        I can recommend you a set of optimal accomodation based on the location of the activity.
        """

        return self.search_context_data(context_data = context_data, 
                                        content = content,
                                        topN = topN,
                                        task_type = task_type)
    
    def I_recommend_services(self,
                           travel_proposal,
                           topN = 3, 
                           task_type = "retrieval_query"):
        """
        This function will recommend the topN most relevant services given the client request
        """

        context_data = "TEST - SERVICES"
        content = f"""I have an inventory for a {travel_proposal}.
        I can recommend you a more luxurious based on the location of the activity."""

        return self.search_context_data(context_data = context_data, 
                                        content = content,
                                        topN = topN,
                                        task_type = task_type)
    

    def I_recommend_client(self, 
                          content,
                          topN = 3, 
                          task_type = "retrieval_query"):
        """
        This function will recommend the topN most relevant clients given the client request
        """

        context_data = "TEST - CLIENT"
        return self.search_context_data(context_data = context_data, 
                                        content = content,
                                        topN = topN,
                                        task_type = task_type)
    
    def I_recommend_client_request(self, 
                                   content,
                                   topN = 3, 
                                   task_type = "retrieval_query"):
        """
        This function will recommend the topN most relevant clients given the client request
        """

        context_data = "TEST - CLIENT REQUEST"
        return self.search_context_data(context_data = context_data, 
                                        content = content,
                                        topN = topN,
                                        task_type = task_type)                                
    



    # ---------------------------------------------------------------------
    # LEVEL 2 SKILLS
    # ---------------------------------------------------------------------
    # these are higher level skills that can do higher dimension tasks
    # e.g. recommend a flight, then recommend an accomodation based on the flight
    # ---------------------------------------------------------------------
    def II_recommend_client(self, 
                            prompt,
                            topN = 3, 
                            task_type = "retrieval_query",
                            chatbot = False, 
                            chatbot_model_name = "gemini-pro",
                            custom_prompt = None):
        """
        This function will recommend the topN most relevant clients given the client request
        """

        client_data = "TEST - CLIENT"
        content_client_data = f"""
        I have a travel proposal/request from a client: {prompt}
        """
        client_recommendation =  self.search_context_data(context_data = client_data, 
                                                          content = content_client_data,
                                                          topN = topN,
                                                          task_type = task_type)
        
        client_request_data = "TEST - CLIENT REQUEST"
        content_client_request_data = f"""
        I have a few clients that I can recommend for a particular client request.
        """
        client_request_recommendation =  self.search_context_data(context_data = client_request_data, 
                                                    content = content_client_request_data,
                                                    topN = topN,
                                                    task_type = task_type)
        
        if chatbot:
            prompt = f"""
            {custom_prompt}
            these are the information: 
            clients:
            {client_recommendation}
            client requests:
            {client_request_recommendation}
            """
            response = self.model_specialist.prompt(model_name = chatbot_model_name,
                                                    prompt = prompt)
            pprint(response.text)
            return {"clients":client_recommendation, "client_requests":client_request_recommendation, "response":response}
    
    def II_recommend_travel_logistics(self,
                         travel_proposal,
                         topN = 3, 
                         task_type = "retrieval_query", 
                         chatbot = False, 
                         chatbot_model_name = "gemini-pro",
                         custom_prompt = None):
        """
        This function will recommend the topN most relevant travel logistics given the client request
        """
        if custom_prompt is None:
            custom_prompt = """
            I have a few flights, accomodations, and services that I can recommend for a particular travel proposal.
            Please summarise them in a travel package format. so for the flights table please get Name, Type, Location and Price and Description information.
            for the accomodations table please get the accomodation details
            for the services table please get the service details, which are all pertinent to building a travel package. 
            If there are no flights, accomodations, or services that are relevant to the travel proposal, then please indicate that there are no flights, accomodations, or services that are relevant to the travel proposal.
            """
        flights = self.I_recommend_flights(travel_proposal, topN = topN, task_type = task_type)
        accomodations = self.I_recommend_accomodations(travel_proposal, topN = topN, task_type = task_type)
        services = self.I_recommend_services(travel_proposal, topN = topN, task_type = task_type)
        if chatbot:
            prompt = f"""
            {custom_prompt}
            these are the information: 
            flights:
            {flights}
            accomodations:
            {accomodations}
            services:
            {services}

            """
            response = self.model_specialist.prompt(model_name = chatbot_model_name,
                                                    prompt = prompt)
            pprint(response.text)
            return {"flights":flights, "accomodations":accomodations, "services":services, "response":response}
        else:
            pprint(f"flights:\n{flights}")
            pprint(f"accomodations:\n{accomodations}")
            pprint(f"services:\n{services}")
            return {"flights":flights, "accomodations":accomodations, "services":services, "response":None}
    
    def II_generate_travel_proposal(self,
                                    input_prompt = "I want to go this place in the photo for 3 days! calm vibe",  #"recommend a full day trip travel itinerary for Kelingking Beach, Nusa Penida, Bali, Indonesia.",
                                    model_name = "gemini-pro",
                                    image_path = None, #"./database/travel/sometiktokss.jpg",
                                    ):
        if image_path is not None:
            prompt_1 = f"""
            You are an expert AI travel agent and is given the following client request:
            {input_prompt}
            And also an image of a travel destination that is relevant to the client request. 
            (it could be an instagram post of a celebrity, a screenshot from a phone of a travel brochure, etc)
            Give me the exact location, name and description of the place in the image? (if it is not AI generated that is) 
            """
            prompt_2 = """Based on the response, recommend a full itinerary based on the customer request and the image content."""
            response = self.model_specialist.prompt_image(model_name = "gemini-pro-vision",
                                                          image_path = image_path,
                                                          prompt_1 = prompt_1,
                                                          prompt_2 = prompt_2)
            pprint(response.text)
            return response 
        else:
            response = self.model_specialist.prompt(model_name = "gemini-pro",
                                                    prompt = input_prompt)
            pprint(response.text)
            return response
               

    # ---------------------------------------------------------------------
    # LEVEL 3 SKILLS
    # ---------------------------------------------------------------------
    # these are higher level skills that can do higher dimension tasks
    # eg; given inventory recommendations, wrap LLM around it to provide a more human friendly response
    

    def III_generate_travel_package(self,
                                    travel_proposal,
                                    model_name = "gemini-pro",
                                    topN = 3, 
                                    task_type = "retrieval_query"):
            """
            This function will recommend the topN most relevant travel logistics given the client request
            """
            inventory_package = self.II_recommend_travel_logistics(travel_proposal, topN = topN, task_type = task_type)
            
            UX_prompt = f"""
                        Generate a travel package for the given trip_recommendation:
                        {travel_proposal}

                        This trip_recommendation comes with the following hotel recommendation:
                        {inventory_package['accomodations']}

                        This trip_recommendation comes with the following flight recommendation:
                        {inventory_package['flights']}

                        This trip_recommendation comes with the following services/activities/tours recommendation:
                        {inventory_package['services']}

                        The package should include the following sections:

                        "Summary"
                        introductory and summary of the trip in one paragraph.
                        The summary should describe in vivid detail, the main attractions, activities, and experiences that the travelers can enjoy in the trip_recommendation. 

                        "Journey Highlights"
                        A list of the main features and most exciting aspects of the package.
                        the highlights must end off with a bold line: "Your journey takes you to: x - y - z"

                        "Itinerary & Map" 
                        This section is an itenerary list that shows the day-by-day plan of the trip, that is also accompanied by a map.

                        The itinerary should include the name, location, and description of each place or activity that the travelers will visit or do each day. 
                        The itinerary should also indicate the approximate duration and transportation mode for each item.

                        A highlights and inclusions section that lists the main features and benefits of the package. 
                        The section should mention what is included in the price, such as flights, accommodation, meals, guides, entrance fees, etc. 
                        The section should also mention any special offers or discounts that are available for the package.
                        A dates and pricing section that shows the available dates and prices for the package. 
                        The section should indicate the departure and return dates, the number of travelers, the total cost, and the payment options for the package. 
                        The section should also provide a link or contact information for booking or inquiring about the package.

                        All information derived here should be based on the recommendations from the previous steps and MUST not be fabricated.

                        """
            response_UX = self.model_specialist.prompt(UX_prompt, model_name = model_name)    
            pprint(response_UX.text)                   
            return response_UX
                         

