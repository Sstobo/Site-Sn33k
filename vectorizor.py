## pip install -U openai pinecone-client jsonlines
## set up pinecone database with 1536 dimensions
import jsonlines
import openai
import pinecone

# Set up OpenAI and Pinecone API keys
OPENAI_API_KEY = ""
PINECONE_API_KEY = ""
INDEX_NAME = ""
PINECONE_ENVIRONMENT=""

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
    for i in range(0, len(data), batch_size):
        text_batch = [item["text"] for item in data[i:i+batch_size]]
        ids_batch = [str(n) for n in range(i, i+min(batch_size, len(data)-i))]
        res = openai.Embedding.create(input=text_batch, engine=model)
        embeds = [record["embedding"] for record in res["data"]]
        to_upsert = zip(ids_batch, embeds)
        index.upsert(vectors=list(to_upsert))

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
