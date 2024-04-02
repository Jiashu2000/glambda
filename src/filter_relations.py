# Filter Relations & Match Node Name to Entity

import pandas as pd
from textblob import TextBlob
import re

input_path = "../data_intermediate"
output_path = "../data_intermediate"

raw_relations = pd.read_csv(input_path + "/raw_relations.csv", index_col = 0)
entities = pd.read_csv(input_path + "/entity_list.csv", index_col = 0)

# Create entity list
entity_set = set(list(entities['ent_name']))

# Add fixed key words as entities
fixed_set = ["lgbt", 'dei', 'diversity']
for ent in fixed_set:
    entity_set.add(ent)

# First transformation: extract nouns from subject, object
def extract_nouns(text):
    blob = TextBlob(text)
    return blob.noun_phrases

raw_relations['node1_t1'] = raw_relations.apply(lambda x: extract_nouns(x['subject']), axis = 1)
raw_relations['node2_t1'] = raw_relations.apply(lambda x: extract_nouns(x['object']), axis = 1)

# Second transformation: match node name to entity list
def match_node_entity(node_name, node_nouns):
    """
    Case1: Node name is in the entity list. 
        Use the node name. For instance, if "LGBT Community" is in the entity list, use it directly.
    
    Case2: Node name is not in the entity list, but the noun list created from the previous step is not empty.
        Select the first noun from the noun list and find relevant entity for the selected noun.

        Case2-a: if a relevant entity is found, use the relevant entity as new node name. For instance, if the noun list is [france], relevant node is "France".

        Case2-b: if no relevant entity is found, use the select noun as new node name. For instance, if the noun list is [leader's stance], no relevant node is found. Therefore, "leader's stance" is used as the new node.
    
    Case3: If node name is not in the entity list and noun list is empty
        Return None
    """
    if node_name in entity_set:
        return node_name
    if len(node_nouns) > 0:
        node_name = node_nouns[0]
        return find_relevant_entity(node_name)
    return None

def find_relevant_entity(node_name):
    """
    Find the most relevant entity for the node name.
    Relevance is determined by the number of matched words.
    """
    entity_list = list(entity_set)
    if node_name in entity_set:
        return node_name
    match_perc = 0
    best_match = None
    node_words = node_name.lower().split()
    for ent in entity_list:
        ent_words = ent.lower().split()
        match_cnt = 0
        for w1 in node_words:
            for w2 in ent_words:
                if w1 == w2:
                    match_cnt += 1
        if (match_cnt/len(ent_words) >= 0.5) and (match_cnt/len(node_words) >= 0.5) and (match_cnt/len(ent_words) > match_perc):
            match_perc = match_cnt/len(ent_words)
            best_match = ent
    
    if best_match is not None:
        return best_match
    node_name = re.sub(r"’ s", '', node_name)
    node_name = re.sub(r"'s", '', node_name)
    return node_name

raw_relations['node1_t2'] = raw_relations.apply(lambda x: match_node_entity(x['subject'], x['node1_t1']), axis = 1)
raw_relations['node2_t2'] = raw_relations.apply(lambda x: match_node_entity(x['object'], x['node2_t1']), axis = 1)

# Select relations if both nodes are not None
filtered_relations = raw_relations[(raw_relations['node1_t2'].notnull()) & (raw_relations['node2_t2'].notnull())]

# Third transformation: deal with nodes with similar names within one news. For instance, "leader's stance" and "catholic leader's stance"

node_set = set(filtered_relations['node1_t2']).union(set(filtered_relations['node2_t2']))
node_list = sorted(list(node_set), key = lambda x: len(x))

def similar_node(node1, node2):
    """
    Determine if two nodes are similar.
    """
    node1_wl = node1.lower().split()
    node2_wl = node2.lower().split()
    node1_len = len(node1_wl)
    node2_len = len(node2_wl)
    matched = 0
    for w1 in node1_wl:
        for w2 in node2_wl:
            if w1 == w2:
                matched += 1
    return (matched/node1_len >= 0.5) & (matched/node2_len >= 0.5)

final_node_list = list()
transformation_map = {}

for node in node_list:
    if node in entity_set:
        final_node_list.append(node)

for node in node_list:
    node_flag = False
    if node in entity_set:
        continue
    for fn in final_node_list:
        if similar_node(node, fn):
            transformation_map[node] = fn
            node_flag = True
        if node_flag:
            break
    if not node_flag: 
        final_node_list.append(node)

def transform_node(node_name):
    if node_name in transformation_map:
        return transformation_map[node_name].title()
    return node_name.title()

filtered_relations['node1_t3'] = filtered_relations.apply(lambda x: transform_node(x['node1_t2']), axis = 1)
filtered_relations['node2_t3'] = filtered_relations.apply(lambda x: transform_node(x['node2_t2']), axis = 1)

# Forth transformation: drop duplicate relations within one news

transformed_relations = filtered_relations.drop_duplicates(subset = ['news_id', 'node1_t3', 'node2_t3'], keep ='first')
transformed_relations.to_csv(output_path + "/transformed_relations.csv")