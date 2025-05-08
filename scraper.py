from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime
import os
from dotenv import load_dotenv
import praw
import mysql.connector
import sys
from datetime import datetime, timedelta

# Load environment variables (ensure your .env file is accessible by Airflow)
load_dotenv()

# Airflow DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.now() - timedelta(days=1),
    'retries': 1,
}

# Reddit API credentials (it's better to manage these as Airflow Connections or Variables)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
REDDIT_APP_NAME = "newsbot_airflow"
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")

# Database configuration (ideally, manage this as an Airflow Connection)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("DB_PASSWORD"),
    "database": "reddit_posts",
    "auth_plugin": "mysql_native_password"
}

# Subreddits to scrape
SUBREDDITS = [
    'datascience',
    'MachineLearning',
    'LanguageTechnology',
    'deeplearning',
    'datasets',
    'visualization',
    'dataisbeautiful',
    'learnpython'
]

def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def create_table():
    conn = connect_db()
    if not conn:
        print("Database connection failed for table creation.")
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reddit_posts (
                post_id VARCHAR(20) PRIMARY KEY,
                title TEXT,
                selftext TEXT,
                url TEXT,
                author VARCHAR(50),
                score INT,
                publish_date DATETIME,
                num_of_comments INT,
                permalink TEXT,
                flair TEXT,
                subreddit VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                full_text TEXT
            )
        """)
        conn.commit()
        print("Table 'reddit_posts' created or already exists.")
        return True
    except mysql.connector.Error as err:
        print(f"Database error during table creation: {err}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_reddit_client():
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_SECRET,
            user_agent=REDDIT_APP_NAME,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD
        )
        reddit.user.me()  # test credentials
        print("Successfully authenticated with Reddit.")
        return reddit
    except Exception as e:
        print(f"Reddit authentication failed: {e}")
        raise  # Re-raise the exception to fail the Airflow task

def insert_post(post):
    conn = connect_db()
    if not conn:
        print("Database connection failed for inserting post.")
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reddit_posts (
                post_id, title, selftext, url, author, score,
                publish_date, num_of_comments, permalink,
                flair, subreddit, full_text
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                title=VALUES(title),
                selftext=VALUES(selftext),
                score=VALUES(score),
                num_of_comments=VALUES(num_of_comments),
                full_text=VALUES(full_text)
        """, (
            post['post_id'],
            post['title'],
            post['selftext'],
            post['url'],
            post['author'],
            post['score'],
            post['publish_date'],
            post['num_of_comments'],
            post['permalink'],
            post['flair'],
            post['subreddit'],
            post['full_text']
        ))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Insert error: {err}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def scrape_subreddit(subreddit_name, limit=20):
    reddit = get_reddit_client()
    print(f"\nScraping r/{subreddit_name} (hot, {limit} posts)...")

    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = subreddit.hot(limit=limit)

        saved_count = 0
        for post in posts:
            if post.stickied:
                continue

            post_data = {
                'post_id': post.id,
                'title': post.title,
                'selftext': post.selftext if post.selftext not in ["[removed]", "[deleted]"] else "",
                'url': post.url,
                'author': str(post.author),
                'score': post.score,
                'publish_date': datetime.utcfromtimestamp(post.created_utc),
                'num_of_comments': post.num_comments,
                'permalink': post.permalink,
                'flair': post.link_flair_text or "",
                'subreddit': subreddit_name,
                'full_text': f"{post.title}\n\n{post.selftext}" if post.selftext else post.title
            }

            if insert_post(post_data):
                saved_count += 1

        print(f"✅ Saved {saved_count}/{limit} posts from r/{subreddit_name}")
        return saved_count
    except Exception as e:
        print(f"Error scraping r/{subreddit_name}: {e}")
        raise  # Re-raise the exception to fail the Airflow task

with DAG(
    dag_id='reddit_scraper_automation',
    default_args=default_args,
    description='Scrapes hot posts from specified subreddits and stores them in a database',
    schedule_interval='@daily',
  # Run once every hour at the beginning of the hour
    catchup=False,
) as dag:
    create_table_task = PythonOperator(
        task_id='create_reddit_posts_table',
        python_callable=create_table,
    )

    scrape_tasks = []
    for subreddit in SUBREDDITS:
        scrape_task = PythonOperator(
            task_id=f'scrape_{subreddit}',
            python_callable=scrape_subreddit,
            op_kwargs={'subreddit_name': subreddit, 'limit': 20},
        )
        scrape_tasks.append(scrape_task)

    create_table_task >> scrape_tasks

