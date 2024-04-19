
# Group Node Information

input_path = "../data_intermediate"
output_path = "../data_intermediate"


import pandas as pd
from collections import Counter

"""
Node is entities identified from each news. 
Each news is assigned to one cluster.
Therefore, entities identified from the news is assigned to relevant cluster. 
One entity could be assigned to multiple cluster. 
Choose one cluster to present on the graph.
"""

entities = pd.read_csv(input_path + "/parsed_entities.csv", usecols = ['news_id', 'ent_name', 'ent_link'])
entity_node = entities.drop_duplicates(subset = ['news_id', 'ent_link'], keep = 'first')

exclude_nodes = ['LGBT', 'LGBTQ', 'LGBTQ+', 'Queer', 'Full Article', 'RT.com', 'Breitbart', 'Forbes', 'The Advocate', 'And The', 'NBC']

entity_node = entity_node[~entity_node.ent_name.isin(exclude_nodes)]

usecols = ['news_id', 'cluster']
news_clusters = pd.read_csv(input_path + "/news_cluster.csv", usecols=usecols)

entity_info = pd.merge(entity_node, news_clusters, on = 'news_id')

entity_info = entity_info.groupby('ent_link').agg({
    'news_id': list,
    "cluster": list,
    "ent_name": "min"
})
entity_info = entity_info.reset_index()
entity_info['ent_name'] = entity_info.apply(lambda x: x['ent_name'].title(), axis = 1)

def choose_cluster(row):
    cluster_list = row['cluster']
    c = Counter(cluster_list)
    return max(c, key = c.get)

entity_info['assigned_cluster'] = entity_info.apply(lambda x: choose_cluster(x), axis = 1)

news = pd.read_csv(input_path + "/filter_data.csv", usecols = ['url', 'news_id', 'title'])
news_link_dict= {t[2]: t[1] for t in news.itertuples(index = False)}

def concat_news(news_id):
    news = ""
    for iid in news_id:
        news += news_link_dict[iid] + ", "
    return news[:-2]

entity_info['news_links'] = entity_info.apply(lambda x: concat_news(x['news_id']), axis = 1)
entity_info['news_count'] = entity_info.apply(lambda x: len(x['news_id']), axis = 1)
entity_info['news_id'] = entity_info.apply(lambda x: ",".join([str(i) for i in x['news_id']]), axis = 1)

entity_info.to_csv(output_path + '/node_graph_info.csv')

# cluster info
cluster = pd.read_csv(input_path + '/cluster_keywords.csv', index_col = 0)
cluster['rep_news'] = cluster.apply(lambda x: set(x['repre_news'].split(',')), axis = 1)

def concat_news(repre_news):
    news = ""
    for iid in repre_news.split(','):
        news += news_link_dict[int(iid)] + ", "
    return news[:-2]

cluster['news_links'] = cluster.apply(lambda x: concat_news(x['repre_news']), axis = 1)
cluster.to_csv(output_path + "/cluster_info.csv")