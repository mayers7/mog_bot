import praw
import re
import time
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
import json  # Add this line at the top of your code
import os
from urllib.parse import urlparse

time.sleep(2) #keeps us from hitting reddit API limits

# Reddit API Credentials
reddit = praw.Reddit(
    client_id=os.getenv(REDDIT_CLIENT_ID),
    client_secret=os.getenv(REDDIT_CLIENT_SECRET),
    user_agent=os.getenv(REDDIT_USER_AGENT),
    username=os.getenv(REDDIT_USERNAME),
    password=os.getenv(REDDIT_PASSWORD),
)

# Define the subreddit
subreddit_name = "finalfantasy"
subreddit = reddit.subreddit(subreddit_name)


print(f"Logged in as: {reddit.user.me()}")


# Function to extract the domain name from a URL
def extract_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc  # Extract just the domain (e.g., www.amazon.com)


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


# Check if the report was successfully made by logging the submission ID and report reason
def process_new_submissions():
    current_time = datetime.now(timezone.utc)
    for submission in subreddit.new(limit=20):  # Fetch recent submissions
        post_time = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
        time_difference = (current_time - post_time).total_seconds() / 60  # Convert to minutes

        print(f"Processing submission: {submission.title} by {submission.author.name} at {post_time}")

        if time_difference > 15:  # Skip posts older than 15 minutes
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

process_new_submissions()
