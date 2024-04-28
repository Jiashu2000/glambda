## Draw Graph
import pandas as pd
import streamlit as st

input_path = "../data_intermediate"
output_path = "../output"
testing_path = "../testing_outputs"

# read news
usecols = ['news_id', 'text', 'cluster', 'x_pos', 'y_pos']
news_cluster = pd.read_csv(input_path + '/news_cluster.csv', usecols = usecols)

news = pd.read_csv(input_path + '/filter_data.csv', usecols = ['url', 'news_id', 'title'])
news_df= pd.merge(news, news_cluster, left_on = 'news_id', right_on ='news_id')

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

# create data source
news_ds = ColumnDataSource(data=dict(index=list(news_df.news_id),
                                     cluster = list(news_df.cluster),
                                      news_title = list(news_df.title),
                                       news_link = list(news_df.url),
                                     news_text = list(news_df.text),
                                     x = list(news_df.x_pos),
                                     y = list(news_df.y_pos)
                                    ))

fill_news_ds = ColumnDataSource(data=dict(index=list(news_df.news_id),
                                     cluster = list(news_df.cluster),
                                      news_title = list(news_df.title),
                                       news_link = list(news_df.url),
                                     news_text = list(news_df.text),
                                     x = list(news_df.x_pos),
                                     y = list(news_df.y_pos)
                                    ))

cluster_ds = ColumnDataSource(data=dict(index=list(cluster.cluster),
                                      cluster_rep_link = list(cluster.news_links),
                                       cluster_rep_title = list(cluster.news_titles)))

color_by_this_attribute = "cluster"

mapper = linear_cmap(field_name=color_by_this_attribute, 
                     palette=Category20[20],
                     low=min(news_ds.data[color_by_this_attribute]) ,high=max(news_ds.data[color_by_this_attribute]))

HOVER_TOOLTIPS = [("News ID", "@index"),
                  ("News Cluster", "@cluster"),
                 ("News Title", "@news_title"),
                 ("News Link", "@news_link"),
                 ("News Text", "@news_text")]

plot = figure(tooltips = HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset",
            active_scroll='wheel_zoom',
             plot_width = 1000, 
             plot_height = 600, 
              name='main_plot')

plot.scatter('x', 'y', size=10, 
          source=fill_news_ds,
          fill_color=mapper,
          line_alpha=0.3,
          line_color="black")

header = Div(text="""<h1>Glambda: News Topic Graph</h1>""")
description = Div(text="""PLACEHOLDER FOR DESCRIPTION""",height=50, width=300)

slider = Slider(start=0, end=10, value=10, step=1, title="Cluster #")
slider_description = Div(text="""<b>Slide to check a specific news cluster</b>""",height=20, width=300)
cluster_news_div = Div(text="""""",height=100, width=300)
# cluster_news_div = Div(text="""<b>Cluster Representative News</b>: Slide to specific cluster to see representative news.""",height=100, width=300)

cluster_keywords_div = Div(text= """""", height=25)
# cluster_keywords_div = Div(text= """<b>Cluster Keywords</b>: Slide to specific cluster to see the keywords.""", height=25)

cluster_summary_div = Div(text= """PLACEHOLDER FOR SUMMARY""", height=25)

node_detail_div = Div(text="""<b>Click on a node to check news details.</b>""",height=100, width=300)

plot.add_tools(TapTool(callback=CustomJS(args={'src': fill_news_ds,'div': node_detail_div}, code="""
    String.prototype.format = function() {
      a = this;
      for (k in arguments) {
        a = a.replace("{" + k + "}", arguments[k])
      }
      return a
    }
""")))

def input_callback(plot, news_ds, fill_news_ds, slider, out_text, topics): 
    
    callback = CustomJS(args=dict(p=plot, news_ds = news_ds, fill_news_ds = fill_news_ds, 
                                  slider = slider, out_text=cluster_keywords_div, topics = topics), code="""
                var B = slider.value;

                var news_data = news_ds.data;
                var fill_news_data = fill_news_ds.data;

                fill_news_data['x']=[];
                fill_news_data['y']=[];
                        
                if (Number(B) == '10') {
                    out_text.text = '';
                        
                    for (var i = 0; i <= news_data.x.length; i++) {
                        fill_news_data['y'].push(news_data['y'][i]);
                        fill_news_data['x'].push(news_data['x'][i]);
                    }
                } 
                else {
                    out_text.text = '<b>Cluster Keywords</b>: ' + topics[Number(B)];
                    for (var i = 0; i <= news_data.x.length; i++) {
                        if (news_data['cluster'][i] == Number(B)) {
                            fill_news_data['y'].push(news_data['y'][i]);
                        } 

                        else { 
                            fill_news_data['y'].push(undefined);  
                        }
                        fill_news_data['x'].push(news_data['x'][i]);
                    }
                }
                        
                fill_news_ds.change.emit();    
                """) 
    return callback

input_callback_1 = input_callback(plot, news_ds, fill_news_ds, slider, cluster_keywords_div, topics)
slider.js_on_change('value', input_callback_1)

cluster_callback = CustomJS(args=dict(src = cluster_ds, slider = slider, out_text=cluster_news_div), code="""
            var B = slider.value;
            
            if (Number(B) == '10') {
                out_text.text = ''
            } 
            else {
                var node_news_link = src.data['cluster_rep_link'][Number(B)].split(', ');
                var node_news_title = src.data['cluster_rep_title'][Number(B)].split('; ');
                var news_link = "<b>Cluster Representative News:</b><br>";
                if (node_news_link.length > 0) {
                    for (let i = 0; i < node_news_link.length; i++) {
                        news_link = news_link + '*' + "&nbsp;&nbsp;" + node_news_title[i] + "&nbsp;&nbsp;&nbsp;&nbsp;" + "<a href=" + node_news_link[i] + ">" + "Read More" + "</a><br>";
                    }
                }
                out_text.text = news_link;
            }
            out_text.change.emit();
            """) 

slider.js_on_change('value', cluster_callback)

callback = CustomJS(args={'src': fill_news_ds, 'div': node_detail_div}, code="""
    if (src.selected.indices.length > 0){
        var ind = src.selected.indices[0];
        var news_id = src.data['index'][ind];
        var news_link = src.data['news_link'][ind];
        var news_title = src.data['news_title'][ind];
        var news_text = src.data['news_text'][ind];
        var cluster_id = src.data['cluster'][ind];
        const title = "<p1><b>News Title:</b> " + news_title + "<br>";
        const link = "<b>News Link:</b> <a href=" + news_link + ">" + news_link + "</a><br>";
        const text = "<b>News Description:</b>" + news_text + "</p1><br>";
        div.text = title + link + text;
    } else { 
        div.text = "<b>Click on a node to see entity link and news links.</b>";
    }
""")

plot.js_on_event('tap', callback)

# STYLE
header.sizing_mode = "stretch_width"
header.style={'color': '#2e484c', 'font-family': 'Georgia, serif'}
header.margin=5

description.style ={'color': '#800000', 'font-family':'Georgia, serif', 'font-size': '1.1em'}
description.sizing_mode = "stretch_width"
description.margin = 5

slider_description.style={'color': '#800000', 'font-family': 'Georgia, serif', 'font-size': '1.1em'}
slider_description.sizing_mode = "stretch_width"
slider_description.margin = 5

#description2.sizing_mode = "stretch_width"
#description2.style ={'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
#description2.margin=10

#description_slider.style ={'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
#description_slider.sizing_mode = "stretch_width"

#description_search.style ={'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif;', 'font-size': '1.1em'}
#description_search.sizing_mode = "stretch_width"
#description_search.margin = 5

#slider.sizing_mode = "stretch_width"
#slider.margin=15

##keyword.sizing_mode = "scale_both"
##keyword.margin=15

node_detail_div.style={'color': '#000080', 'font-family': 'Georgia, serif', 'font-size': '1.1em'}
node_detail_div.sizing_mode = "stretch_width"
node_detail_div.margin = 10

cluster_news_div.style={'color': '#000080', 'font-family': 'Georgia, serif', 'font-size': '1.1em'}
cluster_news_div.sizing_mode = "stretch_width"
cluster_news_div.margin = 10

cluster_keywords_div.style={'color': '#000080', 'font-family': 'Georgia, serif', 'font-size': '1.1em'}
cluster_keywords_div.sizing_mode = "stretch_width"
cluster_keywords_div.margin = 10

# plot.sizing_mode = "stretch_width"
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
# plot.renderers.append(labels)

# LAYOUT OF THE PAGE
l = layout([
    #[header],
    #[description],
    #[slider_description],
    [slider],
    #[description_slider, description_search],
    [cluster_keywords_div],
    [cluster_news_div],
    [plot],
    [node_detail_div],
    #[description2, dataset_description, notes, cite],
])
l.sizing_mode = "scale_both"


# show
# file_name = output_path + '/node_graph_0416.html'
# output_file(file_name)
# show(l)


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
        page_title="Glambda: LGBTQ Node Graph",
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
            <h1 class="title">Glambda: News Topic Graph</h1>
            <div class="description">This is a placeholder for description.</div>
            <div class="instruction">Slide to check a specific news cluster.</div>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown("# Topic Graph 📈")

    # Bokeh plot
    st.markdown("""
        <div class="plot-container">
    """, unsafe_allow_html=True)
    display_graph(l)
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()


