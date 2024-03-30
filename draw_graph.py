
# Draw Graph from Relations


import pandas as pd
import networkx as nx
import seaborn as sns
import random


input_path = "/Users/jiashu/Desktop/Capstone/kg_v0/data_intermediate/transformed_relations.csv"

usecols = ['news_id', 'node1_t3', 'node2_t3', "relation"]
relations = pd.read_csv(input_path, usecols=usecols)
relations = relations.groupby(['node1_t3', 'node2_t3', "relation"]).count().reset_index().rename(columns = {"node1_t3":"node1", "node2_t3": "node2", "news_id":"count"})
relations = relations.loc[relations['node1'] != relations['node2']]
print(relations.head())
nodes = pd.concat([relations['node1'], relations['node2']], axis=0).unique()

G = nx.Graph()

## Add nodes to the graph
for node in nodes:
    G.add_node(
        str(node)
    )

## Add edges to the graph
for index, row in relations.iterrows():
    G.add_edge(
        str(row["node1"]),
        str(row["node2"]),
        title=row["relation"],
        weight=row['count']
    )

communities_generator = nx.community.girvan_newman(G)
top_level_communities = next(communities_generator)
next_level_communities = next(communities_generator)
communities = sorted(map(sorted, next_level_communities))
print("Number of Communities = ", len(communities))
print(communities)


palette = "hls"

## Now add these colors to communities and make another dataframe
def colors2Community(communities) -> pd.DataFrame:
    ## Define a color palette
    p = sns.color_palette(palette, len(communities)).as_hex()
    random.shuffle(p)
    rows = []
    group = 0
    for community in communities:
        color = p.pop()
        group += 1
        for node in community:
            rows += [{"node": node, "color": color, "group": group}]
    df_colors = pd.DataFrame(rows)
    return df_colors


colors = colors2Community(communities)
colors

for index, row in colors.iterrows():
    G.nodes[row['node']]['group'] = row['group']
    G.nodes[row['node']]['color'] = row['color']
    G.nodes[row['node']]['size'] = G.degree[row['node']]


from pyvis.network import Network

graph_output_directory = "test/index_0330.html"

net = Network(
    notebook=False,
    # bgcolor="#1a1a1a",
    cdn_resources="remote",
    height="900px",
    width="100%",
    select_menu=True,
    # font_color="#cccccc",
    filter_menu=False,
)

net.from_nx(G)
# net.repulsion(node_distance=150, spring_length=400)
net.force_atlas_2based(central_gravity=0.015, gravity=-31)
# net.barnes_hut(gravity=-18100, central_gravity=5.05, spring_length=380)
net.show_buttons(filter_=["physics"])

net.show(graph_output_directory, notebook=False)