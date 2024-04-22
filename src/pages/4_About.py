import streamlit as st

def load_css(css_file):
    """Load the CSS file and apply styles."""
    with open(css_file, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    # Configure page settings
    st.set_page_config(
        page_title="Glambda: About",
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
        <div class="about-content-container">
            <h1 class="title"> About 🏳️‍🌈</h1>
            <div class="summary">PLEASE CHANGE THIS DESCRIPTION IT IS JUST PLACEHOLDER TEXT WRITTEN BY CHATGPT!!</div>
            <div class="summary">Welcome to our interactive visualization platform!! This dynamic tool is designed to enhance the production of the Glamazon newsletter. 
            Powered by an advanced knowledge graph, this platform is built upon comprehensive LGBTQ news data, 
            providing deep insights and trends in LGBTQ-related news. Our goal is to facilitate the editorial process and 
            enrich the Glamazon newsletter with engaging and informative visual content. This tool allows users to explore 
            connections, discover patterns, and gain a clearer understanding of the landscape of LGBTQ news, making every 
            edition of the newsletter more impactful and insightful.</div>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown("# About 🏳️‍🌈")
    st.sidebar.header("Explore More")
    st.sidebar.markdown("Navigate through different sections of our platform to explore various features and datasets.", unsafe_allow_html=True)

    # Feedback
    st.subheader("Feedback")
    st.text_area("Let us know what you think about our platform:")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")

if __name__ == "__main__":
    main()
