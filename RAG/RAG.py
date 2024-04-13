

class RAG: 
    def __init__(self, 
                 data_models: dict,):
        # data_models={
        # "travel": {"data": ["flights", "accommodations", "activities", "services", "insurance"],
        #            "LLM_model":"gemini-pro-ultra",
        #            "embedding_model":"models/embedding-001"},
        # "islam": {"data": ["hadith", "quran"],
        #           "LLM_model":"claude-3-opus-20240229",
        #           "embedding_model":"models/embedding-001"}
        #           },

        self.data_models = data_models

    def 