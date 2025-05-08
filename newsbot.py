#!/usr/bin/env python3
"""
Streamlit Newsbot Viewer for Reddit Posts - Using Streamlit DB Connection
"""

import streamlit as st
from datetime import datetime
import os
import requests
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()

# Initialize Streamlit DB connection
@st.cache_resource
def get_db_connection():
    return st.connection("mysql", type="sql", url=os.getenv("DATABASE_URL"))

def fetch_posts(subreddit=None, limit=20):
    conn = get_db_connection()
    
    base_query = "SELECT title, url, score, subreddit, publish_date, full_text FROM reddit_posts"
    
    if subreddit and subreddit != "All":
        query = f"{base_query} WHERE subreddit = :subreddit ORDER BY publish_date DESC LIMIT :limit"
        params = {"subreddit": subreddit, "limit": limit}
    else:
        query = f"{base_query} ORDER BY publish_date DESC LIMIT :limit"
        params = {"limit": limit}
    
    try:
        return conn.query(query, params=params)
    except Exception as err:
        st.error(f"Failed to fetch posts: {err}")
        return []

def generate_with_gemini(prompt):
    api_key = os.getenv("GEM_API")
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI Config
st.set_page_config(page_title="Tech Talk Trends", layout="wide")

# --- Header Section ---
with st.container():
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        image = Image.open("communityIcon_hrq90p2z27k11 (2).jpg")
        st.image(image, width=60)
    with col_title:
        st.title("Tech Talk Trends")
    st.markdown("> *Stay informed on the latest in tech and data.*")

# --- Introduction Section ---
with st.container():
    st.subheader("Explore the Pulse of Tech on Reddit")
    st.markdown("""
    Reddit is a vibrant platform for staying updated on the newest trends and discussions in technology. 
    Its community-driven format allows for real-time conversations and valuable insights. 
    Whether you're a seasoned expert or just starting, Reddit offers a unique way to connect with the tech world.
    """)
    st.markdown("""
    **With this app, you can:**
    - Discover trending news in the data science and tech fields.
    - Explore discussions from leading subreddits.
    - Get AI-powered explanations for complex terms.
    """)

# --- Sidebar for Filtering ---
with st.sidebar:
    st.header("Filter Content")
    subreddits = [
        'All',
        'datascience',
        'MachineLearning',
        'LanguageTechnology',
        'deeplearning',
        'datasets',
        'visualization',
        'dataisbeautiful',
        'learnpython'
    ]
    sub_filter = st.selectbox("Select Subreddit", subreddits)
    limit = st.slider("Number of Posts to Display", 5, 50, 10)
    st.markdown("---")
    st.subheader("About This App")
    st.info("This application aggregates the latest and most popular posts from various technology-focused subreddits on Reddit.")
    st.subheader("How to Use")
    st.markdown("""
    1. **Choose a Subreddit:** Select a topic from the dropdown to see relevant posts.
    2. **Adjust Post Count:** Use the slider to determine how many posts are displayed.
    3. **Expand for Details:** Click on a post title to see more information and a link to the original Reddit thread.
    4. **AI Assistance:** Enter a keyword in the right panel to get a brief explanation.
    """)

# --- Main Content Area ---
st.markdown("---")
if sub_filter != "All":
    st.subheader(f"Latest from r/{sub_filter}")
    all_posts = fetch_posts(sub_filter, limit)
    if all_posts.empty:
        st.warning("No posts found in the selected subreddit.")
    else:
        # Two-column layout for posts and AI help
        col_posts, col_ai = st.columns([3, 1], gap="large")

        with col_posts:
            num_to_show = 5
            if "visible_posts" not in st.session_state:
                st.session_state.visible_posts = num_to_show

            for i, post in all_posts.head(st.session_state.visible_posts).iterrows():
                with st.expander(f"**{post['title']}** (⬆️ {post['score']})"):
                    st.markdown(f"**Subreddit:** r/{post['subreddit']}")
                    st.markdown(f"**Published:** {post['publish_date'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown(post["full_text"][:750] + ("..." if len(post["full_text"]) > 750 else ""))
                    st.markdown(f"[Discuss on Reddit](https://reddit.com{post['url']})", unsafe_allow_html=True)

            if st.session_state.visible_posts < len(all_posts):
                if st.button("Load More Posts"):
                    st.session_state.visible_posts += 5

        with col_ai:
            st.subheader("💡 Need Help Understanding a Term?")
            keyword = st.text_input("Enter the word:")
            if keyword:
                with st.spinner(f"Getting explanation for '{keyword}'..."):
                    explanation = generate_with_gemini(f"Explain '{keyword}' simply for someone interested in tech.")
                    st.info(f"**{keyword}:**\n\n{explanation}")

else:
    st.info("👈 Use the sidebar to select a subreddit and explore the latest tech discussions.")

# --- Footer ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>© 2025 Joyce Kimaiyo</p>", unsafe_allow_html=True)