# search box 

import streamlit as st
import pandas  as pd
import chromadb
from chromadb.utils import embedding_functions

input_path = "../data_intermediate"
output_path = "../output"
testing_path = "../testing_outputs"

def search():
    df = pd.read_csv(input_path + "/filter_data.csv", index_col =0)

    CHROMA_DATA_PATH = "chroma_data/"
    EMBED_MODEL = "all-MiniLM-L6-v2"
    COLLECTION_NAME = "glambda"

    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"},
    )

    docs = df.text.tolist()
    ids = [str(x) for x in df.index.tolist()] 

    collection.add(
        documents=docs,
        ids=ids
    )

    query = st.text_input("Search for News")

    # hit enter to initiate the search. 
    # previously use button #st.button("Search"):
    if query:
        st.write(f"You searched for: {query}")

        query_results = collection.query(
            query_texts= query,
            n_results=5,
        )
        
        return_docs = query_results["documents"]
        return_news_id = return_ids = [int(iid) for iid in query_results["ids"][0]]

        if return_news_id:
            st.write("Results:")
            for idx, news_id in enumerate(return_news_id):
                news_title = df.iloc[news_id]['title']
                news_link = df.iloc[news_id]['url']
                st.markdown(f"{idx+1}: {news_title} - [Read more]({news_link})")
        else:
            st.write("No results found")

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
            <h1 class="title">Glambda: News Search Box</h1>
            <div class="description">This is a placeholder for description.</div>
            <div class="instruction">Type questions or keywords in the search box to find related news.</div>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown("# Search Box 🔍")

    query = st.text_input("Search for News")

    # model set up
    df = pd.read_csv(input_path + "/filter_data.csv", index_col =0)

    CHROMA_DATA_PATH = "chroma_data/"
    EMBED_MODEL = "all-MiniLM-L6-v2"
    COLLECTION_NAME = "glambda"

    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"},
    )

    docs = df.text.tolist()
    ids = [str(x) for x in df.index.tolist()] 

    collection.add(
        documents=docs,
        ids=ids
    )

    # hit enter to initiate the search. 
    # previously use button #st.button("Search"):
    if query:
        st.write(f"You searched for: {query}")

        query_results = collection.query(
            query_texts= query,
            n_results=5,
        )
        
        return_docs = query_results["documents"]
        return_news_id = return_ids = [int(iid) for iid in query_results["ids"][0]]

        if return_news_id:
            st.write("Results:")
            for idx, news_id in enumerate(return_news_id):
                news_title = df.iloc[news_id]['title']
                news_link = df.iloc[news_id]['url']
                st.markdown(f"{idx+1}: {news_title} - [Read more]({news_link})")
        else:
            st.write("No results found")

if __name__ == "__main__":
    main()