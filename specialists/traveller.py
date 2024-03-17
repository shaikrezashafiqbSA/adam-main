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
                                            "TEST - ACCOMODATIONS":"ACCOMODATION ID",
                                            "TEST - ACTIVITIES":"ACTIVITY ID",
                                            "TEST - SERVICES":"SERVICE ID",
                                            },
                        reembed_table = {"TEST - CLIENT":False,
                                        "TEST - CLIENT REQUEST":False,
                                        "TEST - FLIGHTS":True,
                                        "TEST - ACCOMODATIONS":False,
                                        "TEST - ACTIVITIES":False,
                                        "TEST - SERVICES":False,
                                        }
                        ):
        
        print("loading specialist: TRAVELLER ...")
        if reembed:
            # prep the data model
            self.tables = self.prep_data_model(data_model_keys=data_model_keys)
            # print(self.tables)
            # embed the data model
            self.tables = self.embed_data_model(self.tables,reembed_table=reembed_table,embed_id = embed_id, embedding_model = self.embedding_model)
        else: 
            for tab in data_model_keys.keys():
                try:
                    self.tables[tab] = pickle_helper.pickle_this(data=None, pickle_name = f"embedded_{tab}", path=self.state_path)
                    print(f"TRAVELLER embedding: {tab} - LOADED")
                except Exception as e:
                    raise ValueError(f"embedded_{tab} Not found: {e} - Please embed the data model first")
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
                                            "TEST - ACTIVITIES":"ACTIVITY ID",
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
            if "FLIGHTS" in tab:
                # Only combine columns "Origin" and "Destination"
                df["Text"] = df.apply(lambda row: ", ".join([f"{col}: {row[col]}" for col in df.columns if col in ["FLIGHT ID", "Origin", "Destination", "Price"]]), axis=1)
                # df["Text"] = df.apply(lambda row: ", ".join([f"{col}: {row[col]}" for col in df.columns]), axis=1)
            else:
                df["Text"] = df.apply(lambda row: ", ".join([f"{col}: {row[col]}" for col in df.columns]), axis=1)
            # set the title
            df["Title"] = df[data_model_keys[tab]]
            # ensure Title has no NaNs or None
            df["Title"] = df["Title"].dropna()
            # drop everything except for the title and text
            # df = df[["Title", "Text"]] # would this reduce ram? or should i just keep the original df? ans: yes it would reduce ram but not by much but it would make the data model more efficient
            # print col names and number of rows
            if verbose:
                print(f"tab: {tab} - {df.columns} - {len(df)}")
            tables[tab] = df

        print("data model ready for embedding")
        return tables

    # =====================================================================
    # EMBEDDINGS
    # =====================================================================

    def embed_data_model(self, 
                         tables,                                     
                         reembed_table = {"TEST - CLIENT":False,
                                          "TEST - CLIENT REQUEST":False,
                                          "TEST - FLIGHTS":True,
                                          "TEST - ACCOMODATIONS":False,
                                          "TEST - ACTIVITIES":False,
                                          "TEST - SERVICES":False,
                                          }, 
                         embedding_model = None, 
                         embed_id = 0
                         ):
        if embedding_model is None:
            embedding_model = self.embedding_model

        for embed_step_id,tab in enumerate(tables.keys()):
            # print(f"TRAVELLER embedding: {tab}")
            if reembed_table[tab]: 
                try:
                    embed_df = self.model_specialist.embed_df(tables[tab],
                                                                title = "Title", 
                                                                text = "Text",
                                                                model=embedding_model)
                    tables[tab] = embed_df
                except Exception as e:
                    raise ValueError(f"Embed_df FAILED: \n{e}\n - Please investigate and debug the error")
                
                pickle_helper.pickle_this(data=embed_df, pickle_name = f"embedded_{tab}", path=self.state_path)
                print(f"TRAVELLER embedding: {tab} - EMBEDDED SAVED")

            else:
                tables[tab] = pickle_helper.pickle_this(data=None, pickle_name = f"embedded_{tab}", path=self.state_path)
                print(f"TRAVELLER embedding: {tab} - LOADED")


            if embed_step_id == len(tables) - 1:
                embed_step_id=""
            
        #     pickle_helper.pickle_this(data=tables, pickle_name=f"embedded_data_model_{embed_id}", path=self.state_path)
        #     print(f"TRAVELLER embedding: {tab} - SAVED")
        # print(f"TRAVELLER_STATE_{embed_id}{embed_step_id} - SAVED in {self.state_path}")
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
        elif isinstance(topN_results, pd.DataFrame):
            topN_results = topN_results.to_dict(orient='records')
        return topN_results

    
    # =====================================================================
    # TRAVELLER MAIN SKILLS
    # =====================================================================


    # ---------------------------------------------------------------------
    # LEVEL 1 SKILLS
    # ---------------------------------------------------------------------

    def I_recommend_flights(self, 
                            content,
                            topN = 3, 
                            task_type = "retrieval_query"):
        """
        This function will recommend the topN most relevant flights given the client request
        """
        context_data = "TEST - FLIGHTS"

        return self.search_context_data(context_data = context_data, 
                                        content = content,
                                        topN = topN,
                                        task_type = task_type)
    
    def I_recommend_accomodations(self,
                                    content,
                                    topN = 3, 
                                    task_type = "retrieval_query"):
        """
        This function will recommend the topN most relevant accomodations given the client request
        """
        context_data = "TEST - ACCOMODATIONS"

        return self.search_context_data(context_data = context_data, 
                                        content = content,
                                        topN = topN,
                                        task_type = task_type)
    def I_recommend_activities(self,
                                content,
                                topN = 3, 
                                task_type = "retrieval_query"):
        """
        This function will recommend the topN most relevant services given the client request
        """

        context_data = "TEST - ACTIVITIES"

        return self.search_context_data(context_data = context_data, 
                                        content = content,
                                        topN = topN,
                                        task_type = task_type)
    
    def I_recommend_services(self,
                             content,
                             topN = 3,
                             task_type = "retrieval_query"):
        """
        This function will recommend the topN most relevant services given the client request
        """

        context_data = "TEST - SERVICES"

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
            I have a few flights, accomodations, activities and services that I can recommend for a particular travel proposal.
            Please summarise them in a travel package format. so for the flights table please get Name, Type, Location and Price and Description information.
            for the accomodations table please get the accomodation details
            for the services table please get the service details, which are all pertinent to building a travel package. 
            If there are no flights, accomodations, or services that are relevant to the travel proposal, then please indicate that there are no flights, accomodations, or services that are relevant to the travel proposal.
            """
        flights = self.I_recommend_flights(travel_proposal, topN = topN, task_type = task_type)
        accomodations = self.I_recommend_accomodations(travel_proposal, topN = topN, task_type = task_type)
        activities = self.I_recommend_activities(travel_proposal, topN = topN, task_type = task_type)
        services = self.I_recommend_services(travel_proposal, topN = topN, task_type = task_type)
        if chatbot:
            prompt = f"""
            {custom_prompt}
            these are the information: 
            flights:
            {flights}
            accomodations:
            {accomodations}
            activities:
            {activities}
            services:
            {services}
            """
            response = self.model_specialist.prompt(model_name = chatbot_model_name,
                                                    prompt = prompt)
            pprint(response.text)
        else:
            pprint(f"flights:\n{flights}")
            pprint(f"accomodations:\n{accomodations}")
            pprint(f"activities:\n{activities}")
            pprint(f"services:\n{services}")
            response = None

        return {"flights":flights, "accomodations":accomodations, "activities": activities, "services":services, "response":response}
    

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
                                    initial_query,
                                    model_name = "gemini-pro",
                                    topN = 3, 
                                    task_type = "retrieval_query", 
                                    ):
            """
            This function will recommend the topN most relevant travel logistics given the client request
            """
            # Firstly we segment the client_request into the buckets
            prompt = f"""You are a prompt engineer for a travel company. Given the following unstructured request from a client: {initial_query}
                        Segment the query into:
                        1) Client
                        2) Client Request
                        3) Flights
                        4) Accomodations
                        5) Activities
                        6) Services, 
                        So for example, if a client request is "The client Shaik needs to go Singapore with VIP driver for 5 days, with a focus on arab/malay street",
                        you would segment it into and return:
                        'client: Shaik
                        client_request: The client Shaik needs to go Singapore with VIP driver for 5 days, with a focus on arab/malay street
                        flights: Singapore
                        accomodations: Singapore near arab/malay street
                        activities: segmented_query:arab/malay street tour
                        services: segmented_query:VIP driver for 5 days'
                        """
            segments = self.model_specialist.prompt(model_name = model_name, prompt = prompt)
            # extract the segments
            client,client_request,flights,accomodations,activities,services = segments.text.split("\n")

            # Now we can use the segments to generate the travel package
            # Get historical client data
            client_recommendation = self.I_recommend_client(client, topN = topN, task_type = task_type)
            client_request_recommendation = self.I_recommend_client_request(client_request, topN = topN, task_type = task_type)
            # Get travel logistics
            flights = self.I_recommend_flights(flights, topN = topN, task_type = task_type)
            accomodations = self.I_recommend_accomodations(accomodations, topN = topN, task_type = task_type)
            activities = self.I_recommend_activities(activities, topN = topN, task_type = task_type)
            services = self.I_recommend_services(services, topN = topN, task_type = task_type)

            # inventory_package = self.II_recommend_travel_logistics(travel_proposal, topN = topN, task_type = task_type)
            
            UX_prompt = f"""You are a travel agent who is given a set of RECOMMENDATIONs for a travel package. 
                        You are to compile a travel package based on the RECOMMENDATIONs given at the end.
                        The following is the client request: {initial_query}
                        And the following is the client's historical matching data:
                        {client_recommendation}
                        {client_request_recommendation}

                        The package must include the following sections:
                        "Summary"
                        introductory and summary of the trip in one paragraph.
                        The summary should describe in vivid detail, the main attractions, activities, and experiences that the travelers can enjoy in the trip_recommendation. 

                        "Journey Highlights"
                        A list of the main features and most exciting aspects of the package.
                        the highlights must end off with a bold line: "Your journey takes you to: x - y - z"

                        "Itinerary" 
                        This section is an itenerary list that shows the day-by-day, hour-by-hour plan of the trip.
                        The itinerary should include the name, location, and description of each place or activity that the travelers will visit or do each day. 
                        Each day of the itinerary should be planned out from start to end (using information from the RECOMMENDATIONs only).
                        eg: 
                        '1600hrs: Fly to location X by flight A (FLIGHT ID: _), 1800hrs: check in at accomodation A (ACCOMODATION ID: _), 2000hrs: dinner at location Y, etc.'
                        '0800hrs: Breakfast at accomodation A (ACCOMODATION ID: _). 1000hrs: do activity A (ACTIVITY ID: _) at location X, Go to location Y by service B (SERVICE ID: _) 1200hrs: lunch at location Y, 1400hrs: do activity B (ACTIVITY ID: _) at location Z, etc.'
        
                        A highlights and inclusions section that lists the main features and benefits of the package. 
                        The section should mention what is included in the price, such as flights, accommodation, meals, guides, entrance fees, etc. 
                        A pricing section that shows the calculated SUM prices for the package (these prices should be referred from the RECOMMENDATIONs only). 
                        The section must calculate the total cost, using information from the prices of the RECOMMENDATIONs given below only AND NOT generated.

                        All information derived here should be based on the RECOMMENDATIONs below and MUST NOT be generated.
                        All information derived from the RECOMMENDATIONs must be referenced by the relevant ID of the RECOMMENDATION.
                        If there are no matching RECOMMENDATIONs, then please indicate that there are no matching RECOMMENDATIONs and provide fillers.

                        RECOMMENDATIONs: 
                        This trip_recommendation comes with the following hotel RECOMMENDATIONs:
                        {accomodations}

                        This trip_recommendation comes with the following flight RECOMMENDATIONs:
                        {flights}

                        This trip_recommendation comes with the following activities RECOMMENDATIONs:
                        {activities}

                        This trip_recommendation comes with the following services RECOMMENDATIONs:
                        {services}
                        """
            response_UX = self.model_specialist.prompt(UX_prompt, model_name = model_name)    
            pprint(response_UX.text)                   
            return {"prompt": UX_prompt, "response": response_UX}
                         

