from flask import Flask, render_template, request, jsonify, session 

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
    if 'itinerary_buckets' not in session:  # Initialize at the start of a conversation
        session['itinerary_buckets'] = None
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json['message']

    # Semantic Decomposition (check if this needs modification)
    if 'itinerary_buckets' in session:
        # Use existing itinerary_buckets for a follow-up query
        itinerary_buckets = session['itinerary_buckets']

            # Generate Travel Package (with updated arguments)
        convo_package = librarian.Traveller.III_generate_travel_package(
            initial_query=None,
            followup_query=message,  # Pass the message as a follow-up query if necessary
            itinerary_buckets=itinerary_buckets,
            topN=6, 
            model_name="gemini-pro"
        )
    else:
        # Generate initial itinerary_buckets 
        itinerary_buckets = librarian.Traveller.III_semantic_decomposition(message)
        session['itinerary_buckets'] = itinerary_buckets  # Store for follow-ups

        # Generate Travel Package (with updated arguments)
        convo_package = librarian.Traveller.III_generate_travel_package(
            initial_query=message,
            followup_query=None,  # Pass the message as a follow-up query if necessary
            itinerary_buckets=itinerary_buckets,
            topN=6, 
            model_name="gemini-pro"
        )

    raw_response = convo_package["response"].text
    return jsonify({'bot_response': raw_response})

@app.route('/reset_session')
def reset_session():
    session.pop('itinerary_buckets', None)  # Remove 'itinerary_buckets' if it exists
    return "Session Reset"

if __name__ == '__main__':
    app.secret_key = 'your_secret_key1'  # Add a secret key for sessions
    app.run(debug=True)
