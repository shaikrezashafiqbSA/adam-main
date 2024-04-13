from RAG.librarian import Librarian 
"""
these are my inputs (showcase data set)
- layman words
- effective comms - avoid gravitation wells
"""

librarian = Librarian(librarian_LLM_model = "GEMINI")

# SELECT SPECIALIST DATABASE
librarian.select_specialist(specialist = "traveller", specialist_LLM_model = "GEMINI")

# Ask librarian to get acquinted with the specialist database
librarian.Traveller.load_data_model(reembed = False,
                                    embed_id = 0,
                                    data_model_keys = {"TEST - CLIENT":"CLIENT ID",
                                                        "TEST - CLIENT REQUEST":"CLIENT ID",
                                                        "TEST - FLIGHTS":"FLIGHT ID",
                                                        "TEST - ACCOMODATIONS":"ACCOMODATION ID",
                                                        "TEST - SERVICES":"SERVICE ID",
                                                        }
                                    )

# Data Model data quality to be checked (dropped all irrelevant data - invoice number, other ids, empty cells)