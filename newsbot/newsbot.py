#!/usr/bin/env python3
"""
Streamlit Newsbot Viewer for Reddit Posts
"""

import streamlit as st
import pandas as pd
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from PIL import Image

# Load environment variables
load_dotenv()

# Streamlit UI Config
st.set_page_config(page_title="Tech Talk Trends", layout="wide")

# --- Header Section ---
with st.container():
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        script_dir = os.path.dirname(__file__)
        image_path = os.path.join(script_dir, "communityIcon.jpg")


        image = Image.open(image_path)
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

def load_data():
    try:
        script_dir = os.path.dirname(__file__)
        csv_path = os.path.join(script_dir, "clean_news.csv")
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()


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

# --- Main Content Area ---
st.markdown("---")
if sub_filter != "All":
    st.subheader(f"Latest from r/{sub_filter}")
    df = load_data()
    
    if df.empty:
        st.warning("No posts found or data not loaded.")
    else:
        # Filter by subreddit if not "All"
        filtered_df = df[df['subreddit'] == sub_filter] if sub_filter != "All" else df
        
        # Sort by publish_date descending
        filtered_df = filtered_df.sort_values('publish_date', ascending=False).head(limit)
        
        # Two-column layout for posts and AI help
        col_posts, col_ai = st.columns([3, 1], gap="large")

        with col_posts:
            num_to_show = 5
            if "visible_posts" not in st.session_state:
                st.session_state.visible_posts = num_to_show

            for i, row in filtered_df.head(st.session_state.visible_posts).iterrows():
                with st.expander(f"**{row['title']}** (⬆️ {row['score']})"):
                    st.markdown(f"**Subreddit:** r/{row['subreddit']}")
                    st.markdown(f"**Published:** {pd.to_datetime(row['publish_date']).strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown(row["full_text"][:750] + ("..." if len(row["full_text"]) > 750 else ""))
                    st.markdown(f"[Discuss on Reddit](https://reddit.com{row['permalink']})", unsafe_allow_html=True)

            if st.session_state.visible_posts < len(filtered_df):
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