import streamlit as st 

def load_css(css_file):
    """Load the CSS file"""
    with open(css_file, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    # Configure page settings
    st.set_page_config(
        page_title="Glambda",
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
            <h1 class="title">Glambda</h1>
            <div class="description">This is a placeholder for description.</div>
            <div class="instruction">I don't know what to put on the home page yet...</div>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown("# Glambda 🌈")

if __name__ == "__main__":
    main()


