
# Name Entity Recognition using Yodie

import pandas as pd
import requests
import time
import json

input_path = "../data_intermediate"
output_path = "../data_intermediate/yodie_ner"
yodie_url = "https://cloud-api.gate.ac.uk/process/yodie-en"

# read data
data = pd.read_csv(input_path+"/filter_data.csv", index_col = 0)

headers = {'Content-Type': 'text/plain'}

def gate_ner(doc: str):
    """
    Get the name entity recognition response from yodie api.
    """
    response = requests.post(yodie_url, data = doc, headers = headers).json()
    return response

def write_out(doc: str, doc_id: str):
    """
    write out json file
    """
    # the yodie website has speed limit. request too often will block accounts.
    time.sleep(3)
    res = gate_ner(doc)
    doc_name = f"{output_path}/new_{doc_id}.json"
    with open(doc_name, 'w') as f:
        json.dump(res, f)

data.apply(lambda x: write_out(doc = x["text"], doc_id = x["news_id"]), axis = 1)
