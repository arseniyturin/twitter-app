from db import Sqlite
from twitter import TwitterAPI
import time
import datetime
import json
from utils import save_json

sql = Sqlite('db/db.sqlite')
bearer_key = sql.get_bearer_key()
twitter = TwitterAPI(bearer_key)


def update_twitter_api(bearer_key):
    global twitter
    twitter = TwitterAPI(bearer_key)

def add_user(user):
    data_for_sql = parse_user_json(user)
    data_for_sql['last_updated'] = time.time()
    sql.add_user(tuple(data_for_sql.keys()), tuple(data_for_sql.values()))

def add_tweet(tweet):
    data_for_sql = parse_tweet_json(tweet)
    sql.add_tweet(tuple(data_for_sql.keys()), tuple(data_for_sql.values()))

def add_timeline(data):
    for tweet in data['data']:
        if not sql.check_tweet_id(tweet['id']):
            add_tweet(tweet)

def pretty_time(time):
    time = time.replace('Z','')
    return datetime.datetime.fromisoformat(time).strftime('%H:%M - %b %d, %Y')

def parse_user_json(user):
    fields = [
        'id', #default
        'name', #default
        'username',
        'created_at',
        'location',
        'description',
        'verified',
        'profile_image_url',
        'public_metrics/tweet_count',
        'public_metrics/followers_count',
        'public_metrics/following_count'
        ]
    data = {}
    for field in fields:
        if field.find('/') != -1:
            sub = field.split('/')
            data[sub[1]] = user[sub[0]].get(sub[1], '')
        else:
            data[field] = user.get(field, '')

    return data

def parse_tweet_json(tweet):
    fields = [
        'id', #default
        'text', #default
        'created_at',
        'author_id',
        'conversation_id',
        'in_reply_to_user_id',
        'geo',
        'referenced_tweets/id',
        'referenced_tweets/type',
        'public_metrics/retweet_count',
        'public_metrics/reply_count',
        'public_metrics/like_count',
        'public_metrics/quote_count',
        'lang',
        'source'
        ]

    data = {}
    for field in fields:
        if field.find('/') != -1:
            sub = field.split('/')
            if sub[0] == 'referenced_tweets':
                if 'referenced_tweets' in tweet:
                    data['referenced_tweets_' + sub[1]] = tweet[sub[0]][0].get(sub[1], '')
                else:
                    data['referenced_tweets_' + sub[1]] = ''

            if sub[0] == 'public_metrics':
                if 'public_metrics' in tweet:
                    data[sub[1]] = tweet[sub[0]].get(sub[1], '')
                else:
                    data[sub[1]] = ''
        else:
            data[field] = tweet.get(field, '')

    return data


def add_user_and_follows(id):
    '''
    Function requests user information and list of followers and following
    up to 1000 each.
    '''
    try:
        if not sql.check_user_id(id):
            user = twitter.user_lookup(id=id)
            add_user(user)
            save_json(user, filename=username, path='./data/users')
        else:
            user = sql.get_user_by_id(id)
            username = user[2]
            name = user[1]
        # Get user following
        try:
            following_users = twitter.following_lookup(id, 1000)
            followers_users = twitter.followers_lookup(id, 1000)

            save_json(
                following_users,
                filename=username+'_following',
                path='./data/users'
                )
            save_json(
                followers_users,
                filename=username+'_follwers',
                path='./data/users'
                )

            # Insert following information into DB + relationship
            for user in following_users['data']:
                if not sql.check_user_id(user['id']):
                    name, username = add_user(user)

                if not sql.check_following(id, user['id']):
                    sql.add_following(id, user['id'])

            for user in followers_users['data']:
                if not sql.check_user_id(user['id']):
                    name, username = add_user(user)

                if not sql.check_following(user['id'], id):
                    sql.add_following(user['id'], id)

            sql.set_scanned(id, 1)

        except:
            return 0

        return 1
    except:
        return 0
