import urllib3
import json
import certifi
from time import strptime

import datetime
from datetime import date, timedelta
from time import mktime
import time
import calendar

import pymongo
from pymongo import MongoClient


LOW_TIME_SPAN_30 = datetime.timedelta(days = 30)

APP_ID = "670503923052642"
APP_SECRET = "9f9c0575573d52e3cfe9a07c2f02d106"
ACCESS_TOKEN = "access_token=" + APP_ID + "|" + APP_SECRET
GRAPH_FB = "https://graph.facebook.com/"

class Post:
    def __init__(self, _id, _message, _created_time):
        self.id = _id
        self.message = _message
        self.created_time = _created_time
        self.likes = -1
        self.comments = -1
        self.shares = -1
        self.score = -1
    def set_summary(self, _likes, _comments, _shares):
        self.likes = _likes
        self.comments = _comments
        self.shares = _shares
        self.score = self.likes + self.comments * 2 + self.shares * 3
    def display(self):
        print(self.id, self.message, self.created_time)
    def get_date(self):
        return date.fromtimestamp(mktime(self.created_time))
    def convert_to_dict(self, post_list):
        post_document = {
            "id" : self.id,
            "message" : self.message,
            "created_time" : self.created_time,
            "likes" : self.likes,
            "comments" : self.comments,
            "shares" : self.shares,
            "score" : self.score
        }

def build_post_url (username):
    graph_facebook = "https://graph.facebook.com/"
    link_end = "/posts/?key=value&access_token="
    app_id = "670503923052642"
    app_secret = "9f9c0575573d52e3cfe9a07c2f02d106"
    post_url = graph_facebook + username + link_end + app_id + "|" + app_secret
    print (post_url)
    return post_url

def build_post_summary_url(post_id):
    #https://graph.facebook.com/440837215986285_993518624051472/?fields=shares,likes.summary(true),comments.summary(true)&access_token=670503923052642%7C9f9c0575573d52e3cfe9a07c2f02d106
    link_end = str(post_id) + "/?fields=shares,likes.summary(true),comments.summary(true)&"
    return GRAPH_FB + link_end + ACCESS_TOKEN


def get_json_from_url(post_url):
    # Download content from webpage
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    r = http.request ("GET", post_url)
    content = r.data

    # Decode content and parse json
    decoded_content = content.decode("utf-8")
    json_data = json.loads(decoded_content)
    return json_data
    
  
def extract_page(json_page, post_list):

    post_jsons = json_page['data']

    for post_json in post_jsons:
        if 'message' in post_json:
            id = post_json['id']
            message = post_json['message']
            created_time = strptime(post_json["created_time"], "%Y-%m-%dT%H:%M:%S+0000")
            created_date = date(created_time.tm_year, created_time.tm_mon, created_time.tm_mday)
            print(id, end = '')
            print(created_date)
            if date.today() - LOW_TIME_SPAN_30 <= created_date:
                post = Post(id, message, created_time)
                post_list.append(post)
            else:
                return False
    return True          
     
def extract_posts_within_30_days(fb_url):
    post_list = []

    page_url = fb_url
    
    while True:
        # Download json from a page
        json_page = get_json_from_url(page_url)

        # Extract posts from this page
        result = extract_page(json_page, post_list)
        
        if not result:
            break

        page_url = json_page['paging']['next']
                
    return post_list
                
def get_likes_shares_comments(post):
    post_id = post.id
    post_summary_url = build_post_summary_url(post_id)
    post_summary_json = get_json_from_url(post_summary_url)

    #print("Getting summary of", post_id)
    likes = int(post_summary_json["likes"]["summary"]["total_count"])
    comments = int(post_summary_json["comments"]["summary"]["total_count"])
    if "shares" in post_summary_json.keys():
        shares = int(post_summary_json["shares"]["count"])
    else:
        shares = 0
    post.set_summary(likes, comments, shares)

def get_post_score(post):
    return post.score



post_url = build_post_url("ftuconfessions")

post_list = extract_posts_within_30_days(post_url)

for post in post_list:
    get_likes_shares_comments(post)

#for post in post_list:
#    print(post.likes,'x1', post.comments, 'x2', post.shares, 'x3', post.score)

sorted_post_list = sorted(post_list, key=get_post_score, reverse=True)


for post in sorted_post_list[:10]:
    print(post.likes,'x1', post.comments, 'x2', post.shares, 'x3', post.score)


client = MongoClient ("localhost", 27017)
db = client ["GD"]
post_collection = db ["posts"]

##for post in post_list:
for post in sorted_post_list[:10]:
    p_list = post.convert_to_dict(post.__dict__)
    post_collection.insert_one(post.__dict__)
    
client.close()
