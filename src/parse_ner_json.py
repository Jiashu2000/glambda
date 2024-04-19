
# Parse NER Json File


import pandas as pd
import json
import os
import base64

input_path = "../data_intermediate/yodie_ner"
output_path = "../data_intermediate"

# Encode the Key ID and Password in base64 for Basic Authentication
key_id = "gcqvt0b2pp2e"
password = "jv8p0otujzo07xxhmu13"
credentials = f"{key_id}:{password}"
encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

# create a data frame to store each identifies entity
entity_df = pd.DataFrame(columns = ["news_id", 'text', 'ent_name', 'ent_link', 
                             'ent_class', 'ent_specific_class','ent_conf'])


def parse_json(doc: dict, news_id):
    """
    parse json file for each news
    """
    if "entities" not in doc:
        print("json not read")
        return
    if len(doc['entities']) == 0:
        return
    text, entities = doc['text'], doc['entities']['Mention']
    num_entities = len(entities)
    for i in range(num_entities):
        ent = entities[i]
        start_idx = ent['indices'][0]
        end_idx = ent['indices'][1]
        ent_name = text[start_idx:end_idx]
        ent_link = ent['inst']
        ent_class = ent['dbpInterestingClasses']
        ent_specific_class = ent["dbpSpecificClasses"]
        ent_conf = ent['confidence']
        new_row = {"news_id": news_id, 'text': text, 'ent_name': ent_name, 'ent_link': ent_link, 
                   'ent_class':ent_class, 'ent_specific_class': ent_specific_class, 'ent_conf': ent_conf}
        entity_df.loc[len(entity_df)] = new_row


def read_json_files(path):
    """
    read and parse all json files in the directory
    """
    for filename in os.listdir(path):
        if filename.endswith('.json'):
            news_id = filename[5:-5]
            with open(os.path.join(path, filename), 'r') as f:
                doc = json.load(f)
                parse_json(doc, news_id)
                f.close()

read_json_files(input_path)

entity_df.to_csv(output_path +"/parsed_entities.csv")