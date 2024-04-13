from flask import Flask, render_template, request, jsonify

from RAG.librarian import Librarian 

librarian = Librarian(librarian_LLM_model = "GEMINI")

# SELECT SPECIALIST DATABASE
librarian.select_specialist(specialist = "traveller", specialist_LLM_model = "GEMINI", )

# Ask librarian to get acquinted with the specialist database
librarian.Traveller.load_data_model(reembed = False,
                                    embed_id = 0,
                                    data_model_keys = {"TEST - CLIENT":"CLIENT ID",
                                                        "TEST - CLIENT REQUEST":"CLIENT ID",
                                                        "TEST - FLIGHTS":"FLIGHT ID",
                                                        "TEST - ACCOMODATIONS":"ACCOMODATION ID",
                                                        "TEST - ACTIVITIES":"ACTIVITY ID",
                                                        "TEST - SERVICES":"SERVICE ID",
                                                        },
                                    reembed_table = {"TEST - CLIENT":True,
                                                    "TEST - CLIENT REQUEST":True,
                                                    "TEST - FLIGHTS":True,
                                                    "TEST - ACCOMODATIONS":True,
                                                    "TEST - ACTIVITIES":True,
                                                    "TEST - SERVICES":True,
                                                    }
                                                    
                                    )

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json['message']
    convo_package = librarian.Traveller.III_generate_travel_package(initial_query = message,
                                                                 topN = 6, 
                                                                 model_name = "gemini-pro",
                                                                 )
    return jsonify({'bot_response': convo_package["response"].text})

def chat():
    message = request.json['message']
    convo_package = librarian.Traveller.III_generate_travel_package(initial_query = message,
                                                                 topN = 6, 
                                                                 model_name = "gemini-pro",
                                                                 )
    return jsonify({'bot_response': convo_package["response"].text})

if __name__ == '__main__':
    app.run(debug=True)
