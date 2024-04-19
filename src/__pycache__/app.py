## Draw Graph

import pandas as pd
import networkx as nx
import streamlit as st 
from bokeh.models.graphs import NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.models.widgets import Div
from bokeh.models import (Circle, ColumnDataSource, CustomJS, GlyphRenderer, 
                          GraphRenderer, LabelSet, MultiLine, Range1d, 
                          StaticLayoutProvider, TapTool)
from bokeh.palettes import Category20, Spectral8
from bokeh.plotting import figure
from bokeh.layouts import layout, row
from bokeh.transform import linear_cmap



## Data Loading and Preprocessing

# Path
input_path = "../data_intermediate"

# Relations
relations = pd.read_csv(input_path + "/filtered_relations.csv", index_col = 0)
relations = relations.groupby(["node1", "node2", "relation"]).size().reset_index()
relations = relations.rename(columns = {0:"count"})
nodes = set(pd.concat([relations["node1"], relations["node2"]], axis=0).unique())

# Nodes
node_info = pd.read_csv(input_path + "/node_info.csv", index_col = 0) 
node_info = node_info.loc[node_info.node_name.isin(nodes)]



## Graph Construction w/ NetworkX

# Initialize a graph object
G = nx.Graph()

# Add nodes to the graph
for index, row in node_info.iterrows():
    G.add_node(
        str(row["node_name"]),
        cluster_id = row["cluster"], 
        node_link = row["node_link"], 
        news_link = row["news_links"]
    )

# Add edges to the graph
for index, row in relations.iterrows():
    G.add_edge(
        str(row["node1"]),
        str(row["node2"]),
        title=row["relation"],
        weight=row["count"]
    )

# Classify edges based on weight
elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 2]
esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 2]

# Assign colors based on weight
for u,v in G.edges():
    G[u][v]["color"] = "grey" if G[u][v]["weight"] <= 2 else "black"



## Graph Data Setup for Bokeh 

# Calculate node position using spring layout algorithm
pos = nx.spring_layout(G, scale=20, center=(0, 0), k=0.2, iterations=30)

# Collect node and edge information
node_ids = list(G.nodes())
degrees = dict(nx.degree(G))
number_to_adjust_by = 15
adjusted_node_size = dict(
    [(node, 1.5*degree+number_to_adjust_by) for node, degree in nx.degree(G)]
)

# Collect additional node attributes
node_cluster_id = [G.nodes()[n]["cluster_id"] for n in G.nodes()]
node_link = [G.nodes()[n]["node_link"] for n in G.nodes()]
node_news_link = [G.nodes()[n]["news_link"] for n in G.nodes()]
node_degree = [degrees[n] for n in G.nodes()]
adjusted_node_degree = [adjusted_node_size[n] for n in G.nodes()]

# Collect edge information
start_ids = [a for a, b in G.edges()]
end_ids = [b for a, b in G.edges()]
weights = [G[a][b]["weight"] for a, b in G.edges()]
colors = [G[a][b]["color"] for a, b in G.edges()]

# Position and Layout
graph_layout = pos
label_layout = pos
x_graph, y_graph = [v[0] for v in graph_layout.values()], [v[1] for v in graph_layout.values()]
x_label, y_label = [v[0] for v in label_layout.values()], [v[1] for v in label_layout.values()]


# Configure nodes data source
node_ds = ColumnDataSource(
    data=dict(
        index=list(G.nodes()),
        x = x_graph,
        y = y_graph,
        cluster_id = node_cluster_id, 
        node_link = node_link,
        node_news_link= node_news_link,
        node_degree = node_degree,
        adjusted_node_degree = adjusted_node_degree
    ),
    name="Node Renderer"
)

# Configure edges data source
edge_ds = ColumnDataSource(
    data=dict(
        start= start_ids,
        end=end_ids,
        weight = weights,
        color = colors
    ),
    name="Edge Renderer"
)


# Visual encoding w/ Mappers and Glyphs
size_by_this_attribute = "adjusted_node_degree"
color_by_this_attribute = "cluster_id"

# Color Maps
mapper = linear_cmap(
    field_name=color_by_this_attribute, 
    palette=Category20[20],
    low=min(node_ds.data[color_by_this_attribute]),
    high=max(node_ds.data[color_by_this_attribute])
)

# Color Settings
color_palette = Spectral8
minimum_value_color = min(node_ds.data[color_by_this_attribute])
maximum_value_color = max(node_ds.data[color_by_this_attribute])

# Choose colors for node and edge highlighting
node_highlight_color = "white"
edge_highlight_color = "black"


# Graph Renderers
graph_plot = GraphRenderer(
    node_renderer=GlyphRenderer(
        glyph=Circle(size= size_by_this_attribute, fill_color = mapper),
        hover_glyph=Circle(size=size_by_this_attribute, fill_color = node_highlight_color),
        selection_glyph=Circle(size=size_by_this_attribute, fill_color = node_highlight_color),
        nonselection_glyph=Circle(size= size_by_this_attribute, fill_color = mapper),
        data_source=node_ds
    ),
    edge_renderer=GlyphRenderer(
        glyph=MultiLine(line_alpha=0.5, line_width= 2, line_color = "color"),
        selection_glyph=MultiLine(line_width = 2, line_color = edge_highlight_color),
        hover_glyph=MultiLine(line_width = 2, line_color = edge_highlight_color),
        data_source=edge_ds
    ),
    layout_provider=StaticLayoutProvider(graph_layout=graph_layout),
    selection_policy=NodesAndLinkedEdges(),
    inspection_policy = NodesAndLinkedEdges()
)


# Label Configuration
label_ds = ColumnDataSource(
    data=dict(
        index=list(G.nodes()),
        x = x_label,
        y = y_label
    )
)
labels = LabelSet(
    x="x", 
    y="y", 
    text="index", 
    source=label_ds, 
    background_fill_color="white", 
    text_font_size="10px", 
    background_fill_alpha=.7
)



## Bokeh Plot Configuration

# Link Interactivity Container
div = Div(height=300, width=1000)

# Hover Tooltips
HOVER_TOOLTIPS = [
    ("Node Name", "@index"),
    ("Node Link", "@node_link"),
    ("Node Cluster", "@cluster_id"),
    ("Node Degree", "@node_degree")
]

# Create the plot
plot = figure(
    x_range=Range1d(-22.1, 22.1), 
    y_range=Range1d(-22.1, 22.1), 
    tooltips = HOVER_TOOLTIPS,
    tools="pan,wheel_zoom,save,reset",
    active_scroll="wheel_zoom",
    plot_width = 1000, 
    plot_height = 600, 
    name="main_plot"
)


# Set background color to transparent
plot.background_fill_color = None
plot.background_fill_alpha = 0 

# Set border color to transparent
plot.border_fill_color = None
plot.border_fill_alpha = 0

# Hide grid lines
plot.xgrid.visible = False
plot.ygrid.visible = False

# Hide axes
plot.xaxis.visible = False
plot.yaxis.visible = False

# Hide the plot border
plot.outline_line_color = None

# Fill the width of container
plot.sizing_mode = "stretch_width"

# Set the margin
plot.margin = 5

# Render the nodes, edges, and labels
plot.renderers.append(graph_plot)
plot.renderers.append(labels)



## JS Callbacks for Interactivity

# Add tap tool to allow interaction
plot.add_tools(TapTool(callback=CustomJS(args={"src": node_ds, "div": div}, code="""
    String.prototype.format = function() {
      a = this;
      for (k in arguments) {
        a = a.replace("{" + k + "}", arguments[k])
      }
      return a
    }
""")))

# Display node information when selected
callback = CustomJS(args={"src": node_ds, "div": div}, code="""
    if (src.selected.indices.length > 0){
        var ind = src.selected.indices[0];
        var node_name = src.data["index"][ind];
        var node_link = src.data["node_link"][ind];
        var cluster_id = src.data["cluster_id"][ind];
        var node_news_link = src.data["node_news_link"][ind].split(",")
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

plot.js_on_event("tap", callback)



## Page Layout

l = layout([
    [plot],
    [div],
])
l.sizing_mode = "scale_both"



## Streamlit Interface Configuration

def load_css(css_file):
    """Load the CSS file"""
    with open(css_file, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def display_graph(graph):
    """Display Bokeh plot"""
    st.bokeh_chart(graph, use_container_width=True)

def main():
    # Configure page settings
    st.set_page_config(
        page_title="Glambda: LGBTQ Knowledge Graph",
        page_icon="🏳️‍🌈",
        layout="wide"
    )

    # Load the CSS file
    load_css("asset/style.css")

    # Header
    st.markdown("""
        <div class="header-container">
            <header class="header-text">Glamazon@GSC: Creating a Culture of Inform and Inspire</header>
        </div>
    """, unsafe_allow_html=True)

    # Content
    st.markdown("""
        <div class="content-container">
            <h1 class="title">Glambda: News Knowledge Graph</h1>
            <div class="description">This is a placeholder for description.</div>
            <div class="instruction">Click on a node to see entity link and news links.</div>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.slider("Number of Clusters", 1, 20)
    st.sidebar.markdown("# Main page 🎈")
 
    # Bokeh plot
    st.markdown("""
        <div class="plot-container">
    """, unsafe_allow_html=True)
    display_graph(l)
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()


