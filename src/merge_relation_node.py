
# Merge Relations & Group Node Information

input_path = "../data_intermediate"
output_path = "../data_intermediate"

"""
Two kinds of relations are used in the knowledge graph.

1. Semantic relations. Extracted from raw text using Stanford Core NLP.
    For instance, France (node1) has (relation) new prime minister (node2)
2. Statistic (Cluster-Entity) relations. Extracted by clustering and topic modeling.
    For instance, France (entity node) belongs to Cluster Node 1 (cluster node)
"""

import pandas as pd

# Semantic Relations

semantic_relations = pd.read_csv(input_path + "/transformed_relations.csv", usecols = ['news_id', 'node1_t3', 'node2_t3', 'relation'])
semantic_relations = semantic_relations.rename(columns = {'node1_t3': 'node1', 'node2_t3': 'node2'})


# Statistic Relations

"""
currently only consider cluster - entity. could add keyword - entity in the future.
"""

news_entities = semantic_relations.melt(
    id_vars = ['news_id'],
    value_vars = ['node1', 'node2'],
    value_name = 'node'
)[['news_id', 'node']]

# If an entity appears more than once in the news relations, drop the duplicate.
news_entities  = news_entities.drop_duplicates(subset = ['news_id', 'node'], keep = 'first')

usecols = ['news_id', 'cluster']
news_clusters = pd.read_csv(input_path + "/news_cluster.csv", usecols=usecols)

cluster_entity = pd.merge(news_clusters, news_entities, left_on = 'news_id', right_on = 'news_id')
cluster_entity['node1'] = cluster_entity.apply(lambda x: "Cluster " + str(x['cluster']), axis = 1)

statistic_relations = cluster_entity[['node', 'node1']]
statistic_relations.rename(columns= {'node': 'node2'}, inplace = True)
statistic_relations['relation'] = 'Cluster-Entity'
statistic_relations = statistic_relations[['node1', 'node2', 'relation']]

statistic_relations.to_csv(output_path + "/cluster_entity.csv")

# Merge relations

semantic_relations = semantic_relations[['node1', 'node2', 'relation']]
merged_relations = pd.concat([semantic_relations, statistic_relations])
merged_relations.reset_index(drop = True, inplace= True)
merged_relations.to_csv(output_path + "/merged_relations.csv")


# Group information for each node

# Cluster node

cluster_node = news_clusters.groupby('cluster')['news_id'].apply(list).to_frame().reset_index()
cluster_node['node_link'] = None
cluster_node['node_name'] = cluster_node.apply(lambda x: 'Cluster ' + str(x['cluster']), axis = 1)
cluster_node.drop(columns = ['cluster'], inplace = True)

# Entity node

entities = pd.read_csv(input_path + "/parsed_entities.csv", usecols = ['news_id', 'ent_name', 'ent_link'])
entity_node = entities.drop_duplicates(subset = ['news_id', 'ent_name'])
entity_node = entity_node.groupby('ent_name')['news_id'].apply(list).to_frame().reset_index()
entity_node['ent_name'] = entity_node.apply(lambda x: x['ent_name'].title(), axis = 1)

entity_link = entities.drop_duplicates(subset = ['ent_name'], keep = 'first')[['ent_name', 'ent_link']]
entity_node = pd.merge(entity_node, entity_link)
entity_node = entity_node.rename(columns = {'ent_name': "node_name", 'ent_link': "node_link"})

# Merge nodes

nodes = pd.concat([cluster_node, entity_node])
nodes.reset_index(drop=True, inplace= True)

news = pd.read_csv(input_path + "/filter_data.csv", usecols = ['url', 'news_id', 'title'])
news_link_dict= {t[2]: t[1] for t in news.itertuples(index = False)}

def concat_news(news_id):
    news = ""
    for iid in news_id:
        news += news_link_dict[iid] + ", "
    return news[:-2]

nodes['news_links'] = nodes.apply(lambda x: concat_news(x['news_id']), axis = 1)
nodes['news_id'] = nodes.apply(lambda x: ",".join([str(i) for i in x['news_id']]), axis = 1)

node_cluster = cluster_entity.drop_duplicates(subset = ['node'], keep = 'first')[['cluster', 'node']]
node_info = pd.merge(nodes, node_cluster, left_on = 'node_name', right_on = 'node', how = 'left')

def calc_news_size(row):
    if row['node_name'].startswith("Cluster"):
        return 10
    news_list = row['news_id'].split(',')
    return len(news_list)

node_info['degree'] = node_info.apply(lambda x: calc_news_size(x), axis = 1)

def transform_cluster_node(row):
    if row['node_name'].startswith("Cluster"):
        return int(row['node_name'][-1])
    return row['cluster']

node_info['cluster'] = node_info.apply(lambda x: transform_cluster_node(x), axis = 1)
node_info['cluster'] = node_info['cluster'].fillna(-1).astype('int')
node_info = node_info.drop(columns = ['node'])

show_node = node_info[node_info['degree'] > 1]
show_node_set = set(show_node.node_name)

show_node.to_csv(output_path + "/node_info.csv")

# Filter relations. Only keep relations with two nodes matched to entities
node_set = set(show_node['node_name'])
merged_relations['node1_flag'] = merged_relations.apply(lambda x : x['node1'] in node_set, axis = 1)
merged_relations['node2_flag'] = merged_relations.apply(lambda x : x['node2'] in node_set, axis = 1)
filtered_relations = merged_relations[merged_relations['node1_flag'] & merged_relations['node2_flag']]
filtered_relations.reset_index(drop=True, inplace= True)
filtered_relations = filtered_relations[['node1', 'node2', 'relation']]

filtered_relations.to_csv(output_path + '/filtered_relations.csv')