import base64
import streamlit as st
from pathlib import Path

def load_css(css_file):
    """Load the CSS file and apply styles."""
    with open(css_file, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def img_to_bytes(img_path):
    """Read an image file and encode it as base64."""
    img_bytes = Path(img_path).read_bytes()
    return base64.b64encode(img_bytes).decode()

def img_to_html(img_path):
    """Generate an HTML img tag containing a base64 encoded image."""
    return "<img src='data:image/jpeg;base64,{}' class='img-fluid'>".format(img_to_bytes(img_path))


def main():
    # Configure page settings
    st.set_page_config(
        page_title="Glambda: Team Lambda",
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
    st.markdown(f"""
        <h1 class="title"> Team 💻</h1>
        <div class="team-container">
            <div class="member">
                {img_to_html("asset/img/jiashu-chen.jpg")}
                <div class="member-name">Jiashu Chen</div>
            </div>
            <div class="member">
                {img_to_html("asset/img/qianqian-liu.JPG")}
                <div class="member-name">Qianqian Liu</div>
            </div>
            <div class="member">
                {img_to_html("asset/img/juntong-wu.jpg")}
                <div class="member-name">Juntong Wu</div>
            </div>
            <div class="member">
                {img_to_html("asset/img/chesie-yu.JPG")}
                <div class="member-name">Chesie Yu</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown("# Team 💻")
    st.sidebar.header("Explore More")
    st.sidebar.markdown("Navigate through different sections of our platform to explore various features and datasets.", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
