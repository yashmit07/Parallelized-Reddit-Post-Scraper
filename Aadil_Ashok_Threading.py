import os
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
import threading

#Using "threading" library to parallelize the scraper

def sorting_through_posts(crawled_posts,subreddit_top_posts, i, j):
    while(i <= j):
        post = subreddit_top_posts[i]
        json_string = '{"Title":"title", "ID":"ID", "Author":"author", "Date":"created", "URL":"URL", "Score":"score", "Body":"selfText", "HTML Title":"html title", "Comments":"comments"}'
        postJSON = json.loads(json_string)
        
        #get post info
        postJSON['Title'] = post.title
        postJSON['ID'] = post.id
        postJSON['Author'] = str(post.author)
        postJSON['URL'] = post.url
        postJSON['Score'] = post.score
        postJSON['Body'] = post.selftext
        postJSON['Date'] = str(get_date(post))

        #if post has links in body, get title of link
        if post.is_self: 
            links = get_links(post.selftext)

        html_links = get_links(post.selftext)
        html_titles = {url: get_titles(url) for url in html_links}
        postJSON['HTML Title'] = html_titles
        
        #get top comments
        crawled_comments = []
        try:
            post.comments.replace_more(limit=0)
        except prawcore.exceptions.TooManyRequests:
            print(f"Subreddit Rate Limit Exceeded. \n")
            time.sleep(60)
            return
        post_comments = post.comments.list()
        for comment in post_comments[:20]:  #this number specifies how many comments are parsed
            crawled_comments.append({
                'Comment Body' : comment.body,
                'Comment Author': str(comment.author)
            })
        postJSON['Comments'] = crawled_comments
        crawled_posts.append(postJSON)
        i = i + 1


#To run the program do: python scraper.py <Subreddit Name> <# of top posts>
#example: python scraper.py Programming 100

#make sure you install PRAW and all the other libraries for it to work

#code needed to make PRAW (Python Reddit API Wrapper) work
reddit = praw.Reddit(
    client_id = "aAXuKXHkpglxK4rSy5Sjqw",
    client_secret = "rozvEYfPuTGdaGGySRVtnOgKCR8dxA",
    user_agent = "search engine by u/_HyP3_"
)

#function to convert post.created_utc return to YYYY-MM-DD HOUR:MINUTE:SECOND format
def get_date(post):
    time = post.created_utc
    return datetime.datetime.fromtimestamp(time)

def get_titles(url):
    try:
        page = requests.get(url)
        if page.status_code == 200:
            soup  = BeautifulSoup(page.text, 'html.parser')
            if soup.title:
                return soup.title.text
            else:
                return 'No Title'
    except request.RequestException:
        return 'ERROR: Could Not Retrieve Title'
    
def get_links(text):
    print("FOUND LINK:", re.findall(r'\(https?://\S+\)', text))
    return re.findall(r'\(\(https?://\S+\)\)', text)

#code that takes in arguments from execution
parser = argparse.ArgumentParser(
        description='Crawls subreddit and pulls top posts.')
parser.add_argument('subreddit',metavar='<sub Name>', type=str, nargs=1, help='The name of the subreddit')
parser.add_argument('topLim',metavar='t', type=int, nargs=1, help='The limit of top posts')
args = parser.parse_args()

#using the subreddit argument to pass it to PRAW 
subreddit = reddit.subreddit(args.subreddit[0])

#Praw gets the number of top posts in our chosen subreddit based of the argument from execution
subreddit_top_posts_temp = subreddit.top(limit=args.topLim[0]) 

subreddit_top_posts = []
for post in subreddit_top_posts_temp:
    subreddit_top_posts.append(post)
#dictionary to store post data for now
crawled_posts = []

threads = os.cpu_count() #4
chunks = int(args.topLim[0]) // threads
if(chunks == 0):
    chunks = 1
  #i = 0, j = 1
i = 0
j = (i + chunks) - 1
if(j < i):
    j = i
thread_array = []
#The main for loop that collects all the data from all of the top posts and stores it into crawled_posts
for index in range(threads):
    post_data = threading.Thread(target=sorting_through_posts,args=(crawled_posts,subreddit_top_posts, i, j))
    thread_array.append(post_data)
    post_data.start()
    if(i == j):
        i = j + chunks
    else:
        i = j + 1
    j = j + chunks
    if(j >= int(args.topLim[0])):
        break
for post_data in thread_array:
    post_data.join()
if(int(args.topLim[0]) % threads != 0):
    sorting_through_posts(crawled_posts,subreddit_top_posts,i,len(subreddit_top_posts) - 1)
    
#dump all data into a json file called '<subreddit>_posts.json'
output_file = args.subreddit[0] + '_postsAadilAshok.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(crawled_posts, f, indent=4, ensure_ascii=False)

