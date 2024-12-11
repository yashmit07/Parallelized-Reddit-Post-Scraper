
import praw
import prawcore
import json
import datetime
import time
import argparse
import validators
import re
import requests
from bs4 import BeautifulSoup
import ray  # Import Ray for parallelization

# To run the program do: python scraper.py <Subreddit Name> <# of top posts>
# example: python scraper.py Programming 100

# Make sure you install PRAW and all the other libraries for it to work

# Code needed to make PRAW (Python Reddit API Wrapper) work

# Initialize Ray
ray.init()

# Function to convert post.created_utc return to YYYY-MM-DD HOUR:MINUTE:SECOND format
def get_date(post):
    time = post.created_utc
    return datetime.datetime.fromtimestamp(time)

# Function to fetch the title of a URL
@ray.remote
def get_title(url):
    try:
        page = requests.get(url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
            return soup.title.text if soup.title else 'No Title'
        else:
            return 'ERROR: Invalid Page'
    except requests.RequestException:
        return 'ERROR: Could Not Retrieve Title'

# Extract links from a text body
@ray.remote
def get_links(text):
    return re.findall(r'https?://\S+', text)

# Process a single post
@ray.remote
def process_post(post):
    post_data = {
        "Title": post.title,
        "ID": post.id,
        "Author": str(post.author),
        "Date": str(get_date(post)),
        "URL": post.url,
        "Score": post.score,
        "Body": post.selftext,
        "HTML Title": {},
        "Comments": []
    }

    # Extract links and their HTML titles
    links = ray.get(get_links.remote(post.selftext))
    html_titles = ray.get([get_title.remote(link) for link in links])
    post_data["HTML Title"] = dict(zip(links, html_titles))

    # Fetch top comments
    crawled_comments = []
    try:
        post.comments.replace_more(limit=0)
    except prawcore.exceptions.TooManyRequests:
        time.sleep(60)
    comments = post.comments.list()
    for comment in comments[:20]:
        crawled_comments.append({
            'Comment Body': comment.body,
            'Comment Author': str(comment.author)
        })
    post_data["Comments"] = crawled_comments

    return post_data

# Initialize Reddit API
reddit = praw.Reddit(
    client_id="aAXuKXHkpglxK4rSy5Sjqw",
    client_secret="rozvEYfPuTGdaGGySRVtnOgKCR8dxA",
    user_agent="search engine by u/_HyP3_"
)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Crawls subreddit and pulls top posts.')
parser.add_argument('subreddit', metavar='<sub Name>', type=str, nargs=1, help='The name of the subreddit')
parser.add_argument('topLim', metavar='t', type=int, nargs=1, help='The limit of top posts')
args = parser.parse_args()

# Start the timer
start_time = time.time()

# Fetch subreddit posts
subreddit = reddit.subreddit(args.subreddit[0])
subreddit_top_posts = subreddit.top(limit=args.topLim[0])

# Process posts
post_refs = [process_post.remote(post) for post in subreddit_top_posts]
crawled_posts = ray.get(post_refs)

# Write output to a JSON file
output_file = args.subreddit[0] + '_postsRay.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(crawled_posts, f, indent=4, ensure_ascii=False)

# Stop the timer and print elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Execution Time: {elapsed_time:.2f} seconds")
