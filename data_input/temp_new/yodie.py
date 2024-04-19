import base64
import json
import logging
import os

import pandas as pd
import requests

## Logging

# Configure logging
logging.basicConfig(level=logging.INFO, filename='logs/yodie.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')


## API Credentials

# API endpoint
yodie_url = "https://cloud-api.gate.ac.uk/process/yodie-en"

# Define all API keys and passwords
credentials_list = [
    ("gchocm8wu1bu", "tfw116fbq9zspxa6ual2"),  # personal
    ("gctfv777nhf8", "qwwrauaiae4uy5rk5922"),  # misc
    ("gcd7x4c1smcj", "v91l23g3xwbfiuc8fja8")   # 101
    # ("gcqvt0b2pp2e", "jv8p0otujzo07xxhmu13")   # uw
]

def prepare_headers(credentials):
    """
    Encode credentials and prepare headers.
    """
    key_id, password = credentials
    credentials_encoded = base64.b64encode(f"{key_id}:{password}".encode('utf-8')).decode('utf-8')
    return {
        'Content-Type': 'text/plain',
        'Authorization': f'Basic {credentials_encoded}'
    }

# List of headers
headers_list = [prepare_headers(creds) for creds in credentials_list]


## Entity Extraction

request_count = 0

def gate_ner(doc: str, headers):
    """
    Get the name entity recognition response from yodie api.
    """
    response = requests.post(yodie_url, data=doc.encode('utf-8'), headers = headers).json()
    return response

def write_out(doc: str, doc_id: str):
    """
    Write out json file.
    """
    global request_count

    # Key rotation every 100 requests
    index = (request_count // 100) % len(headers_list)
    current_headers = headers_list[index]
    logging.info(f"Using header {index} for request {request_count}")

    # Send request
    res = gate_ner(doc, current_headers)
    doc_name = os.path.join("yodie_ner", f"new_{doc_id}.json")
    with open(doc_name, 'w') as f:
        json.dump(res, f)
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
    logging.info(f"Generated file {doc_name} with size {file_size} bytes")

    # Log a warning if file size is less than 100 bytes
    if file_size < 100:
        logging.warning(f"File {doc_name} is smaller than expected with size {file_size} bytes")

    request_count += 1

# Load the data
data = pd.read_csv("filter_data01.csv", index_col = 0)

data.iloc.apply(lambda x: write_out(doc = x["text"], doc_id = x["news_id"]), axis = 1)
