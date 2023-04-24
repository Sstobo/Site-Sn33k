import os
import json
import hashlib
from langchain.document_loaders import ReadTheDocsLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm.auto import tqdm
import tiktoken
import pdfplumber

tokenizer = tiktoken.get_encoding('cl100k_base')

def tiktoken_len(text):
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)

def process_pdf_files(folder_path):
    # Get all files in the folder
    all_files = os.listdir(folder_path)

    # Filter out PDF files
    pdf_files = [file for file in all_files if file.endswith('.pdf')]

    # Initialize tokenizer and text_splitter
    tokenizer = tiktoken.get_encoding('cl100k_base')
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=20,
        length_function=tiktoken_len,
        separators=['\n\n', '\n', ' ', '']
    )

    documents = []

    # Process each PDF file
    for pdf_file in tqdm(pdf_files):
        try:
            file_path = os.path.join(folder_path, pdf_file)

            # Load the PDF content
            with pdfplumber.open(file_path) as pdf:
                content = ' '.join(page.extract_text() for page in pdf.pages)

            # Generate a unique ID based on the file path
            m = hashlib.md5()
            m.update(file_path.encode('utf-8'))
            uid = m.hexdigest()[:12]

            # Split the content into chunks
            chunks = text_splitter.split_text(content)

            # Create document data
            for i, chunk in enumerate(chunks):
                documents.append({
                    'id': f'{uid}-{i}',
                    'text': chunk,
                    'source': file_path
                })

            # Delete the PDF file after processing (optional)
            os.remove(file_path)

        except Exception as e:
            print(f"Error processing file {pdf_file}: {e}")

    # Save the documents to a JSONL file
    with open('train.jsonl', 'a') as f:
        for doc in documents:
            f.write(json.dumps(doc) + '\n')

    return documents

# Call the function with the folder path "pdfdocs"
folder_path = "pdfs"
documents = process_pdf_files(folder_path)