from langchain.document_loaders import ReadTheDocsLoader


# Create a ReadTheDocsLoader object with the URL of the website
loader = ReadTheDocsLoader('rtdocs')

# Load the documents
docs = loader.load()

# Check if any documents were loaded
if len(docs) > 0:
    # Print the first document
    print(docs[0].page_content)
else:
    print("No documents found")

import tiktoken
tokenizer = tiktoken.get_encoding('cl100k_base')

# create the length function
def tiktoken_len(text):
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)

tiktoken.encoding_for_model('gpt-3.5-turbo')
token_counts = [tiktoken_len(doc.page_content) for doc in docs]

print(f"""Min: {min(token_counts)}
Avg: {int(sum(token_counts) / len(token_counts))}
Max: {max(token_counts)}""");


from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=20,  # number of tokens overlap between chunks
    length_function=tiktoken_len,
    separators=['\n\n', '\n', ' ', '']
)

chunks = text_splitter.split_text(docs[0].page_content)
len(chunks)

tiktoken_len(chunks[0]), tiktoken_len(chunks[1])

import hashlib
m = hashlib.md5()  # this will convert URL into unique ID

url = docs[0].metadata['source'].replace('rtdocs/', 'https://')
print(url)

# convert URL to unique ID
m.update(url.encode('utf-8'))
uid = m.hexdigest()[:12]
print(uid)

data = [
    {
        'id': f'{uid}-{i}',
        'text': chunk,
        'source': url
    } for i, chunk in enumerate(chunks)
]
data

from tqdm.auto import tqdm

documents = []

for doc in tqdm(docs):
    url = doc.metadata['source'].replace('rtdocs/', 'https://')
    m.update(url.encode('utf-8'))
    uid = m.hexdigest()[:12]
    chunks = text_splitter.split_text(doc.page_content)
    for i, chunk in enumerate(chunks):
        documents.append({
            'id': f'{uid}-{i}',
            'text': chunk,
            'source': url
        })

len(documents)

import json

with open('train.jsonl', 'w') as f:
    for doc in documents:
        f.write(json.dumps(doc) + '\n')


documents = []

with open('train.jsonl', 'r') as f:
    for line in f:
        documents.append(json.loads(line))

len(documents)