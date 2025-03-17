#!/usr/bin/env python
# coding: utf-8

# !pip install praw

# # Function to check user profiles for specific links containing keywords
# def check_user_profile(username):
#     user = reddit.redditor(username)
#     try:
#         # Check links in the user's public description
#         profile_text = user.subreddit["public_description"]
#         
#         # Find all links in the profile text
#         links = re.findall(r'https?://[^\s]+', profile_text)
#         
#         for link in links:
#             if any(keyword in link.lower() for keyword in keywords):
#                 return True
#         
#         # Check links in the user's "Links" section (if they exist)
#         for link in user.subreddit["links"]:
#             if any(keyword in link["url"].lower() for keyword in keywords):
#                 return True
# 
#     except Exception as e:
#         print(f"Error accessing profile of {username}: {e}")
#     
#     return False
# 

# # Monitor new posts within the last 30 minutes
# def process_new_submissions():
#     current_time = datetime.now(timezone.utc)
#     for submission in subreddit.new(limit=50):  # Fetch recent submissions
#         post_time = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
#         time_difference = (current_time - post_time).total_seconds() / 60  # Convert to minutes
# 
#         print(f"Post: {submission.title}, Time difference: {time_difference} minutes")
# 
#         if time_difference > 1440:  # Skip posts older than 30 minutes
#             continue
# 
#         author = submission.author.name
#         print(f"Checking user: {author}")  # Debugging line
# 
#         if check_user_profile(author):  # Check for links with specific keywords
#             print(f"Reporting: {author}")  # Debugging line
#             report_reason = "Mog_bot: Test, please ignore this report."
#             submission.report(report_reason)  # Report the post

# process_new_submissions()

# In[ ]:





# In[ ]:


#trying this using scraping


# In[1]:


import praw
import re
import time
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
import json  # Add this line at the top of your code
from urllib.parse import urlparse


# In[2]:


time.sleep(2) #keeps us from hitting reddit API limits


# In[3]:


# Reddit API Credentials
reddit = praw.Reddit(
    client_id="lAofMRkJRtAKcZUW3ulyYg",
    client_secret="xbwAawh2qDnY82DFy8E9K22B1vNo4Q",
    user_agent="mog_bot",
    username="mog_bot",
    password="kupopo123"
)


# In[4]:


# Define the subreddit
subreddit_name = "finalfantasy"
subreddit = reddit.subreddit(subreddit_name)


# In[5]:


print(f"Logged in as: {reddit.user.me()}")


# In[6]:


# Function to extract the domain name from a URL
def extract_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc  # Extract just the domain (e.g., www.amazon.com)


# In[7]:


# Function to check user profiles for links in the "Links" section
def check_user_profile(username):
    # Send an HTTP request to fetch the user's profile page
    user_profile_url = f"https://www.reddit.com/user/{username}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(user_profile_url, headers=headers)
        
        # If the request was successful
        if response.status_code == 200:
            print(f"Successfully fetched profile for u/{username}.")
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for all <faceplate-tracker> elements with the 'social_link' noun
            faceplate_elements = soup.find_all('faceplate-tracker', {'noun': 'social_link'})
            
            # List to store the extracted links
            found_links = []

            for faceplate in faceplate_elements:
                # Extract the JSON data from the 'data-faceplate-tracking-context' attribute
                tracking_data = faceplate.get('data-faceplate-tracking-context')

                if tracking_data:
                    # Parse the JSON data to extract the URL
                    try:
                        tracking_json = json.loads(tracking_data)
                        social_link = tracking_json.get('social_link', {})
                        url = social_link.get('url')
                        
                        if url:
                            # Shorten the URL to just the domain name
                            domain = extract_domain(url)
                            found_links.append(domain)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON for u/{username}: {e}")
            
            # If links are found, report them
            if found_links:
                print(f"Links found in u/{username}'s profile: {found_links}")
                # Construct the report with the found links, limiting it to under 100 characters
                report_reason = f"Mog_bot: User profile links found: {', '.join(found_links[:5])}."
                return report_reason  # Return the report message with links (limiting to 5 domains if needed)
            else:
                print(f"No 'social_link' found in u/{username}'s profile.")
        
        else:
            print(f"Failed to retrieve profile for u/{username}. HTTP status code: {response.status_code}")

    except Exception as e:
        print(f"Error accessing profile of {username}: {e}")
    
    return None  # Return None if no report is generated


# In[8]:


# Check if the report was successfully made by logging the submission ID and report reason
def process_new_submissions():
    current_time = datetime.now(timezone.utc)
    for submission in subreddit.new(limit=10):  # Fetch recent submissions
        post_time = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
        time_difference = (current_time - post_time).total_seconds() / 60  # Convert to minutes

        print(f"Processing submission: {submission.title} by {submission.author.name} at {post_time}")

        if time_difference > 120:  # Skip posts older than 30 minutes
            continue

        author = submission.author.name
        try:
            report_reason = check_user_profile(author)  # Check for links in profile
            if report_reason:  # If links are found, report the post
                print(f"Reporting post: {submission.title}")
                result = submission.report(report_reason)  # Attempt to report the post
                if result is None:  # If result is None, report was successful
                    print(f"Reported: {author} - {report_reason}")
                else:
                    print(f"Failed to report: {author}. Result: {result}")
            else:
                print(f"No report reason for u/{author}")
        except Exception as e:
            print(f"Error processing submission {submission.id}: {e}")


# In[16]:


process_new_submissions()


# In[ ]:


# Send a GET request to the user's profile page
user_profile_url = "https://www.reddit.com/user/ItsWhimsicalSage/"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(user_profile_url, headers=headers)

# If the request is successful, print the HTML content
if response.status_code == 200:
    print(response.text)  # This will output the raw HTML, look for the "Links" section
else:
    print(f"Failed to fetch profile. HTTP status code: {response.status_code}")


# In[11]:


# Report the newest post
def report_newest_post():
    # Fetch the newest post
    submission = next(subreddit.new(limit=1))  # Get the most recent post
    
    print(f"Reporting post: {submission.title} by {submission.author}")
    
    # Report the post with a reason
    submission.report(reason="This is a test report for the newest post.")
    
    print(f"Reported post: {submission.title} with reason: 'This is a test report for the newest post.'")


# In[13]:


#this report does show up in queue
report_newest_post()


# In[ ]:
