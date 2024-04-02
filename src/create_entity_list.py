
# Find Named Entities in the KG


import pandas as pd

input_path = "../data_intermediate"
output_path = "../data_intermediate"


entity_df = pd.read_csv(input_path+"/parsed_entities.csv", index_col = 0)

def remove_suffix(name):
    """
    Some entity has a name like "Taylor Swift's". need to remove 's at the end
    """
    if name.endswith("'s"):
        return name[:-2]
    return name

entity_df['ent_name'] = entity_df['ent_name'].apply(lambda x: remove_suffix(x))
entity_df.to_csv(output_path + '/parsed_entities.csv')

entities = entity_df[['ent_name', "ent_link", 'ent_class', "ent_conf"]]

# drop duplicates based on entity link to DBpedia, which makes sure that there is no duplicate entity.
entities = entities.drop_duplicates(subset = ['ent_link'], keep = 'first')

entities = entities.reset_index(drop = True)

entities.to_csv(output_path + '/entity_list.csv')