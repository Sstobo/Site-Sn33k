# Website Scraper and Vectorizer

This Python repository contains a set of scripts that allow you to scrape a website, clean the data, organize it, chunk it, and then vectorize it. The resulting vectors can be used for a variety of machine learning tasks, such as similarity search or clustering.

## Files

- `cleaner.py`: This script downloads a website using wget, reads and cleans the HTML files using Beautiful Soup, and saves the resulting text files in a specified directory.
- `chunker.py`: This script splits the text files into smaller chunks, using a recursive character-based text splitter. The resulting chunks are saved in a JSONL file.
- `vectorizor.py`: This script loads the JSONL file, creates embeddings using OpenAI's text-embedding-ada-002 model, and indexes the embeddings using Pinecone.

## Requirements

- Python 3.x
- OpenAI API key
- Pinecone API key
- `bs4` Python library
- `jsonlines` Python library
- `tqdm` Python library
- `tiktoken` Python library
- `pinecone-client` Python library

## Usage

1. Clone the repository and navigate to the project directory.
2. Install the required Python libraries using `pip install -r requirements.txt`.
3. Set up your OpenAI and Pinecone API keys.
4: copy and run the wget command: 
  `wget -r -A.html -P rtdocs https://your-website # download the website`
5. Run `cleaner.py` to download and clean the website data. - This will break down the directory structure into on list of html docs.
6. Run `chunker.py` to split the text files into smaller chunks. This outputs train.json in the root
7. Run `vectorizor.py` to create embeddings and index them using Pinecone. This will vectorize train.json

Note: Before running `vectorizor.py`, make sure to set up a Pinecone database with 1536 dimensions.
