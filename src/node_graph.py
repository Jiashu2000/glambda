## Draw Graph

input_path = "../data_intermediate"
output_path = "../output"
testing_path = "../testing_outputs"

import pandas as pd
from datetime import date

# read nodes
node_info = pd.read_csv(input_path + '/node_graph_info.csv', index_col = 0) 

node_info = node_info[node_info.news_count > 3]

# read topics
with open(input_path + '/cluster_keywords.txt') as f:
    topics = f.readlines()

# read cluster
cluster = pd.read_csv(input_path + '/cluster_info.csv', index_col = 0)

import networkx as nx
from bokeh.io import show
from bokeh.models import Plot, TapTool, ColumnDataSource, LabelSet, StaticLayoutProvider, Circle, MultiLine, TextInput, Div, Paragraph, Slider
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

G = nx.Graph()

## Add nodes to the graph
for index, row in node_info.iterrows():
    G.add_node(
        str(row['ent_name']),
        cluster_id = row['assigned_cluster'], 
        node_link = row['ent_link'], 
        news_link = row['news_links'],
        node_degree = row['news_count']
    )

pos = nx.drawing.spring_layout(G, scale = 20, center=(0, 0),  k=0.6, iterations=20)
node_ids = list(G.nodes())
number_to_adjust_by = 15
adjusted_node_size = dict([(node, 0.8*degree+number_to_adjust_by) for node, degree in nx.degree(G)])

node_cluster_id = [G.nodes()[n]['cluster_id'] for n in G.nodes()]
node_link = [G.nodes()[n]['node_link'] for n in G.nodes()]
node_news_link = [G.nodes()[n]['news_link'] for n in G.nodes()]
node_degree = [G.nodes()[n]['node_degree'] for n in G.nodes()]
adjusted_node_degree = [1.5 * G.nodes()[n]['node_degree'] + number_to_adjust_by  for n in G.nodes()]

graph_layout = pos
label_layout = pos
x_graph, y_graph = [v[0] for v in graph_layout.values()], [v[1] for v in graph_layout.values()]
x_label, y_label = x_graph, y_graph
# random.uniform(0, 1) *
node_ds = ColumnDataSource(data=dict(index=list(G.nodes()),
                                     x = x_graph,
                                     y = y_graph,
                                     cluster_id = node_cluster_id, 
                                    node_link = node_link,
                                    node_news_link= node_news_link,
                                     node_degree = node_degree,
                                    adjusted_node_degree = adjusted_node_degree),
                           name="Node Renderer")

fill_node_ds = ColumnDataSource(data=dict(index=list(G.nodes()),
                                     x = x_graph,
                                     y = y_graph,
                                     cluster_id = node_cluster_id,
                                    node_link = node_link,
                                    node_news_link= node_news_link,
                                     node_degree = node_degree,
                                    adjusted_node_degree = adjusted_node_degree),
                           name="Node Renderer")

cluster_ds = ColumnDataSource(data=dict(index=list(cluster.cluster),
                                      cluster_rep = list(cluster.news_links)))

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
                                                  data_source=fill_node_ds),
                      layout_provider=StaticLayoutProvider(graph_layout=graph_layout),
                      selection_policy=NodesAndLinkedEdges(),
                          inspection_policy = NodesAndLinkedEdges())

label_ds = ColumnDataSource(data=dict(index=list(G.nodes()),
                                      x = x_label,
                                      y = y_label,
                                      cluster_id = node_cluster_id))

fill_label_ds = ColumnDataSource(data=dict(index=list(G.nodes()),
                                      x = x_label,
                                      y = y_label,
                                      cluster_id = node_cluster_id))

labels = LabelSet(x='x', y='y', text='index', source=fill_label_ds, 
                  background_fill_color='white', text_font_size='10px', background_fill_alpha=.7)

div = Div(text="""Click on a node to see entity link and news links.""",height=300, width=300)
div2 = Div(text="""Choose a cluster to see representative news""",height=300, width=300)

title = "News Topic Graph"

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

plot.add_tools(TapTool(callback=CustomJS(args={'src': fill_node_ds,'div': div}, code="""
    String.prototype.format = function() {
      a = this;
      for (k in arguments) {
        a = a.replace("{" + k + "}", arguments[k])
      }
      return a
    }
""")))

plot.scatter('x', 'y', size='adjusted_node_degree', 
          source=fill_node_ds,
          fill_color=mapper,
          line_alpha=0.3,
          line_color="black")

callback = CustomJS(args={'src': fill_node_ds, 'div': div}, code="""
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

text_banner = Paragraph(text= 'Cluster Keywords: Slide to specific cluster to see the keywords.', height=25)
slider = Slider(start=0, end=10, value=10, step=1, title="Cluster #")
#keyword = TextInput(title="Search:")

text_banner2 = Paragraph(text= 'Cluster Representative News: Slide to specific cluster to see representative news.', height=25)
div2 = Div(text="""Cluster Representative News: Slide to specific cluster to see representative news.""",height=100, width=300)

def input_callback(plot, node_ds, fill_node_ds, label_ds, fill_label_ds, slider, out_text, topics): 
    
    callback = CustomJS(args=dict(p=plot, node_ds = node_ds, fill_node_ds = fill_node_ds, label_ds = label_ds, fill_label_ds = fill_label_ds, slider = slider, out_text=text_banner, topics = topics), code="""
                var B = slider.value;

                var node_data = node_ds.data;
                var fill_node_data = fill_node_ds.data;

                var label_data = label_ds.data;
                var fill_label_data = fill_label_ds.data;

                fill_node_data['x']=[];
                fill_node_data['y']=[];

                fill_label_data['x']=[];
                fill_label_data['y']=[];
                        
                if (Number(B) == '10') {
                    out_text.text = 'Keywords: Slide to specific cluster to see the keywords.'
                        
                    for (var i = 0; i <= node_data.x.length; i++) {
                        fill_node_data['y'].push(node_data['y'][i]);
                        fill_node_data['x'].push(node_data['x'][i]);
                    }

                    for (var i = 0; i <= label_data.x.length; i++) {
                        fill_label_data['y'].push(label_data['y'][i]);
                        fill_label_data['x'].push(label_data['x'][i]);
                    }
                } 
                else {
                    out_text.text = 'Keywords: ' + topics[Number(B)];
                    for (var i = 0; i <= node_data.x.length; i++) {
                        if (node_data['cluster_id'][i] == Number(B)) {
                            fill_node_data['y'].push(node_data['y'][i]);
                        } 
                        else { 
                            fill_node_data['y'].push(undefined);  
                        }
                        fill_node_data['x'].push(node_data['x'][i]);
                    }

                    for (var i = 0; i <= label_data.x.length; i++) {
                        if (label_data['cluster_id'][i] == Number(B)) {
                            fill_label_data['y'].push(label_data['y'][i]);
                        } 
                        else { 
                            fill_label_data['y'].push(undefined);  
                        }
                        fill_label_data['x'].push(label_data['x'][i]);
                    }
                }
                        
                fill_node_ds.change.emit();  
                fill_label_ds.change.emit();    
                """) 
    return callback

input_callback_1 = input_callback(plot, node_ds, fill_node_ds, label_ds, fill_label_ds, slider, text_banner, topics)

slider.js_on_change('value', input_callback_1)
#keyword.js_on_change('value', input_callback_1)

cluster_callback = CustomJS(args=dict(src = cluster_ds, slider = slider, out_text=div2), code="""
            var B = slider.value;
            
            if (Number(B) == '10') {
                out_text.text = 'Cluster Representative News: Slide to specific cluster to see representative news.'
            } 
            else {
                var node_news_link = src.data['cluster_rep'][Number(B)].split(',');
                var news_link = "<b>Cluster Representative News Link:</b><br>";
                if (node_news_link.length > 0) {
                    for (let i = 0; i < node_news_link.length; i++) {
                        news_link = news_link + "<a href=" + node_news_link[i] + ">" + node_news_link[i] + "</a><br>";
                    }
                }
                out_text.text = news_link;
            }
            out_text.change.emit();
            """) 

slider.js_on_change('value', cluster_callback)

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

div2.style={'color': '#BF0A30', 'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
div2.sizing_mode = "stretch_width"
div2.margin = 10

text_banner.style={'color': '#0269A4', 'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
text_banner.sizing_mode = "stretch_width"
text_banner.margin = 20

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

#plot.renderers.append(graph_plot)
plot.renderers.append(labels)

# LAYOUT OF THE PAGE
l = layout([
    [header],
    #[description],
    #[description_slider, description_search],
    [slider],
    [text_banner],
    [div2],
    [plot],
    [div],
    #[description2, dataset_description, notes, cite],
])
l.sizing_mode = "scale_both"


today_date = date.today()
# show
file_name = output_path + '/node_graph_' + str(today_date) + '.html'
output_file(file_name)
show(l)