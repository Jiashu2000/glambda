# Relation Extraction using Standford NLP


import pandas as pd
from openie import StanfordOpenIE

input_path = "data_intermediate"
output_path = "data_intermediate"

properties = { 'openie.affinity_probability_cap': 1 / 3,}

usecols = ['news_id', "text"]
news_df = pd.read_csv(input_path+"/filter_data.csv", index_col = 0, usecols = usecols)
raw_relations = pd.DataFrame(columns = ['news_id', "subject", "relation", "object"])

def raw_relation_extraction(news_text):
    raw_relations = []
    with StanfordOpenIE(properties=properties) as client:
        for triple in client.annotate(news_text):
            print('|-', triple)
            raw_relations.append(triple)
    return raw_relations

for idx, row in news_df.iterrows():
    news_id = idx
    news_raw_rels = raw_relation_extraction(row['text'])
    for raw_rel in news_raw_rels:
        new_row = {"news_id": news_id, "subject": raw_rel['subject'], "relation": raw_rel['relation'], "object": raw_rel["object"]}
        raw_relations.loc[len(raw_relations)] = new_row

raw_relations.to_csv(output_path + "/raw_relations.csv")
