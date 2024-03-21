from dotenv import load_dotenv
load_dotenv()
import os 

PORT_NUMBER = os.getenv("PORT_NUMBER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BARD_API_KEY = os.getenv("BARD_API_KEY")
BARD_API_KEY2 = os.getenv("BARD_API_KEY2")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
PINECONE_DIMENSION = int(os.getenv("PINECONE_DIMENSION"))

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
S3_REGION = os.getenv("S3_REGION")

TELEGRAM_TRAVELLER_API_KEY = os.getenv("TELEGRAM_TRAVELLER_API_KEY")