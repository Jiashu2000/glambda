## Draw Graph

input_path = "../data_intermediate"
output_path = "../output"
testing_path = "../testing_outputs"

import pandas as pd
from datetime import date

# read relations

relations = pd.read_csv(input_path + '/filtered_relations.csv', index_col = 0)
relations = relations.groupby(['node1', 'node2', "relation"]).size().reset_index()
relations = relations.rename(columns = {0:"count"})
nodes = set(pd.concat([relations['node1'], relations['node2']], axis=0).unique())

# read nodes
node_info = pd.read_csv(input_path + '/node_info.csv', index_col = 0) 
node_info = node_info.loc[node_info.node_name.isin(nodes)]

#exclude_nodes = ['Full Article']
#node_info = node_info[~node_info.node_name.isin(exclude_nodes)]

import networkx as nx
from bokeh.io import show
from bokeh.models import Plot, TapTool, ColumnDataSource, LabelSet, StaticLayoutProvider, Circle, MultiLine
from bokeh.models.widgets import Div
from bokeh.models.graphs import NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.plotting import figure
from bokeh.models.renderers import GraphRenderer, GlyphRenderer
from bokeh.layouts import layout, row
from bokeh.models import CustomJS
from bokeh.plotting import from_networkx
from bokeh.models import Range1d
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.transform import linear_cmap
from bokeh.palettes import Category20
from bokeh.io import output_file, show
from plot_text import header 
import math

G = nx.Graph()

## Add nodes to the graph
for index, row in node_info.iterrows():
    G.add_node(
        str(row['node_name']),
        cluster_id = row['cluster'], 
        node_link = row['node_link'], 
        news_link = row['news_links'],
        node_degree = row['degree']
    )

## Add edges to the graph
for index, row in relations.iterrows():
    G.add_edge(
        str(row["node1"]),
        str(row["node2"]),
        title=row["relation"],
        weight=row['count']
    )

elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > 2]
esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= 2]

for u,v in G.edges():
    G[u][v]['color'] = 'grey' if G[u][v]['weight'] <= 2 else 'black'

pos = nx.drawing.spring_layout(G, scale=20, center=(0, 0),  k=0.6, iterations=20)
node_ids = list(G.nodes())
degrees = dict(nx.degree(G))
number_to_adjust_by = 15
adjusted_node_size = dict([(node,  2*degree+number_to_adjust_by) for node, degree in nx.degree(G)])
#1.5*degree+number_to_adjust_by

node_cluster_id = [G.nodes()[n]['cluster_id'] for n in G.nodes()]
node_link = [G.nodes()[n]['node_link'] for n in G.nodes()]
node_news_link = [G.nodes()[n]['news_link'] for n in G.nodes()]
node_degree = [G.nodes()[n]['node_degree'] for n in G.nodes()]
adjusted_node_degree = [adjusted_node_size[n] for n in G.nodes()]

start_ids = [a for a,b in G.edges()]
end_ids = [b for a,b in G.edges()]
weights = [G[a][b]['weight'] for a,b in G.edges()]
colors = [G[a][b]['color'] for a,b in G.edges()]

graph_layout = pos
label_layout = pos
x_graph, y_graph = [v[0] for v in graph_layout.values()], [v[1] for v in graph_layout.values()]
x_label, y_label = [v[0] for v in label_layout.values()], [v[1] for v in label_layout.values()]

node_ds = ColumnDataSource(data=dict(index=list(G.nodes()),
                                     x = x_graph,
                                     y = y_graph,
                                     cluster_id = node_cluster_id, 
                                    node_link = node_link,
                                    node_news_link= node_news_link,
                                     node_degree = node_degree,
                                    adjusted_node_degree = adjusted_node_degree),
                           name="Node Renderer")
edge_ds = ColumnDataSource(data=dict(start= start_ids,
                                      end=end_ids,
                                      weight = weights,
                                      color = colors),
                            name="Edge Renderer")

size_by_this_attribute = 'adjusted_node_degree'
color_by_this_attribute = "cluster_id"

mapper = linear_cmap(field_name=color_by_this_attribute, 
                     palette=Category20[20],
                     low=min(node_ds.data[color_by_this_attribute]) ,high=max(node_ds.data[color_by_this_attribute]))

color_palette = Spectral8
minimum_value_color = min(node_ds.data[color_by_this_attribute])
maximum_value_color = max(node_ds.data[color_by_this_attribute])

#Choose colors for node and edge highlighting
node_highlight_color = 'white'
edge_highlight_color = 'black'

graph_plot = GraphRenderer(node_renderer=GlyphRenderer(glyph=Circle(size= size_by_this_attribute, 
                                                                    fill_color = mapper),
                                                       hover_glyph=Circle(size=size_by_this_attribute, fill_color = node_highlight_color),
                                                       selection_glyph=Circle(size=size_by_this_attribute, fill_color = node_highlight_color),
                                                       nonselection_glyph=Circle(size= size_by_this_attribute, 
                                                                    fill_color = mapper),
                                                  data_source=node_ds),
                      edge_renderer=GlyphRenderer(glyph=MultiLine(line_alpha=0.5, line_width= 2, line_color = 'color'),
                                                  selection_glyph=MultiLine(line_width = 2, line_color = edge_highlight_color),
                                                  hover_glyph=MultiLine(line_width = 2, line_color = edge_highlight_color),
                                                  data_source=edge_ds),
                      layout_provider=StaticLayoutProvider(graph_layout=graph_layout),
                      selection_policy=NodesAndLinkedEdges(),
                          inspection_policy = NodesAndLinkedEdges())

label_ds = ColumnDataSource(data=dict(index=list(G.nodes()),
                                      x = x_label,
                                      y = y_label))
labels = LabelSet(x='x', y='y', text='index', source=label_ds, 
                  background_fill_color='white', text_font_size='10px', background_fill_alpha=.7)

div = Div(text="""Click on a node to see entity link and news links.""",height=300, width=300)

title = "News Knowledge Graph"

HOVER_TOOLTIPS = [("Node Name", "@index"),
                 ("Node Link", "@node_link"),
                 ("Node Cluster", "@cluster_id"),
                 ("Node Degree", "@node_degree")]

plot = figure(x_range=Range1d(-22.1, 22.1), 
              y_range=Range1d(-22.1, 22.1), 
              tooltips = HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset",
            active_scroll='wheel_zoom',
             plot_width = 1000, 
             plot_height = 600, 
              name='main_plot', 
             title = title)

plot.add_tools(TapTool(callback=CustomJS(args={'src': node_ds,'div': div}, code="""
    String.prototype.format = function() {
      a = this;
      for (k in arguments) {
        a = a.replace("{" + k + "}", arguments[k])
      }
      return a
    }
""")))

callback = CustomJS(args={'src': node_ds, 'div': div}, code="""
    if (src.selected.indices.length > 0){
        var ind = src.selected.indices[0];
        var node_name = src.data['index'][ind];
        var node_link = src.data['node_link'][ind];
        var cluster_id = src.data['cluster_id'][ind];
        var node_news_link = src.data['node_news_link'][ind].split(',')
        const entity_name = "<p1><b>Node Name:</b> " + node_name.toString() + "<br>";
        const entity_link = "<b>Node Link:</b> <a href=" + node_link + ">" + node_link + "</a></p1><br>";
        var news_link = "<b>Relate News Link:</b><br>";
        if (node_news_link.length > 0) {
            for (let i = 0; i < node_news_link.length; i++) {
                news_link = news_link + "<a href=" + node_news_link[i] + ">" + node_news_link[i] + "</a><br>";
            }
        }
        div.text = entity_name + entity_link + news_link;
    } else { 
        div.text = "Click on a plot to see the link to the article.";
    }
""")

plot.js_on_event('tap', callback)

# STYLE
header.sizing_mode = "stretch_width"
header.style={'color': '#2e484c', 'font-family': 'Julius Sans One, sans-serif;'}
header.margin=5

#description.style ={'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
#description.sizing_mode = "stretch_width"
#description.margin = 5

#description2.sizing_mode = "stretch_width"
#description2.style ={'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
#description2.margin=10

#description_slider.style ={'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
#description_slider.sizing_mode = "stretch_width"

#description_search.style ={'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
#description_search.sizing_mode = "stretch_width"
#description_search.margin = 5

##slider.sizing_mode = "stretch_width"
##slider.margin=15

##keyword.sizing_mode = "scale_both"
##keyword.margin=15

div.style={'color': '#BF0A30', 'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
div.sizing_mode = "stretch_width"
div.margin = 20

#3text_banner.style={'color': '#0269A4', 'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
#text_banner.sizing_mode = "stretch_width"
#text_banner.margin = 20

plot.sizing_mode = "stretch_width"
plot.margin = 5

#dataset_description.sizing_mode = "stretch_width"
#dataset_description.style ={'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
#dataset_description.margin=10

#notes.sizing_mode = "stretch_width"
#notes.style ={'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
#notes.margin=10

#cite.sizing_mode = "stretch_width"
#cite.style ={'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}#
#cite.margin=10

#r = row(div_curr,text_banner)
#r.sizing_mode = "stretch_width"

plot.renderers.append(graph_plot)
plot.renderers.append(labels)

# LAYOUT OF THE PAGE
l = layout([
    [header],
    #[description],
    #[description_slider, description_search],
    ##[slider, keyword],
    ##[text_banner],
    [plot],
    [div],
    #[description2, dataset_description, notes, cite],
])
l.sizing_mode = "scale_both"

today_date = date.today()
# show
file_name = output_path + '/knowledge_graph_' + str(today_date) + '.html'
output_file(file_name)
show(l)