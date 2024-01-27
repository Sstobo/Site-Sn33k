## pip install -U openai pinecone-client jsonlines
## set up pinecone database with 1536 dimensions
import jsonlines
import openai
import pinecone
import os
from dotenv import load_dotenv

# Set up OpenAI and Pinecone API keys
# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
# Set up OpenAI and Pinecone API keys
# Load train.jsonl file
def load_data(file_path):
    data = []
    with jsonlines.open(file_path) as f:
        for item in f:
            data.append(item)
    return data

# Initialize OpenAI API
def init_openai(api_key):
    openai.api_key = api_key
    return "text-embedding-ada-002"

# Initialize Pinecone index
def init_pinecone(api_key, index_name, dimension):
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(index_name, dimension=dimension)
    return pinecone.Index(index_name)

# Create embeddings and populate the index
def create_and_index_embeddings(data, model, index):
    batch_size = 32
    for start_index in range(0, len(data), batch_size):
        # Correctly use 'pageContent' instead of 'text'
        text_batch = [item["pageContent"] for item in data[start_index:start_index+batch_size]]
        # Correct the references for ids_batch based on the new structure
        ids_batch = [
            f"{item['metadata']['txtPath'].split('/')[-1]}_{i}"  # Use 'txtPath' from within 'metadata'
            for i, item in enumerate(data[start_index:start_index+batch_size])
        ]
        res = openai.Embedding.create(input=text_batch, engine=model)
        embeds = [record["embedding"] for record in res["data"]]
        # Update 'to_upsert' with the correct metadata structure
        to_upsert = [
            {
                "id": ids_batch[i],
                "values": embeds[i],
                "metadata": {
                    "txtPath": data[start_index + i]["metadata"]["txtPath"],
                    "pageContent": text_batch[i]
                }
            }
            for i in range(len(embeds))
        ]
        index.upsert(vectors=to_upsert)

if __name__ == "__main__":
    # Load the data from train.jsonl
    train_data = load_data("train.jsonl")

    # Initialize OpenAI Embedding API
    MODEL = init_openai(OPENAI_API_KEY)

    # Get embeddings dimension
    sample_embedding = openai.Embedding.create(input="sample text", engine=MODEL)["data"][0]["embedding"]
    EMBEDDING_DIMENSION = len(sample_embedding)

    # Initialize Pinecone index
    chatgpt_index = init_pinecone(PINECONE_API_KEY, INDEX_NAME, EMBEDDING_DIMENSION)

    # Create embeddings and populate the index with the train data
    create_and_index_embeddings(train_data, MODEL, chatgpt_index)
