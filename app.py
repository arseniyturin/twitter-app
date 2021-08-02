'''
    $ export FLASK_APP=hello
    $ export FLASK_ENV=development
    $ flask run

    IDEAS
    1. How many people are you away from the celebrity?
    2. Classification of the users by their tweets
    3. Relationship between # of followers and # of likes
    4. Words cloud
    5. Trends by words used
    6.

    UTC-0 time: datetime.datetime.utcnow()

    arseniytyurin
    AAAAAAAAAAAAAAAAAAAAAGEHPAEAAAAA4wuxSZLDmhe4XWgNZnFyeyGBG2I%3Dw5LZ2iygmCiZEVo96lrtrCZLw8Tiaz4OkS9rED3sIjLIH154TJ
'''

from flask import Flask, request, redirect, jsonify, render_template
import time
import datetime
import json
from twitter import TwitterAPI
from utils import save_json
from db import Sqlite
import controller

app = Flask(__name__)
sql = Sqlite('db/db.sqlite')
bearer_key = sql.get_bearer_key()

if len(bearer_key) > 0:
    twitter = TwitterAPI(bearer_key[0][0])

#################################### INDEX #####################################
@app.route('/')
def index():
    return render_template(
        'index.html',
        active_page='index'
        )

@app.route('/test')
def test():
    try:
        result = sql.test()
    except Exception as e:
        return f'{e}'

    #if type(result) == str:
#        return render_template('error.html', error=result)
#    else:
#        return f'{sql.test()}'

#################################### TRENDS ####################################
@app.route('/trends')
def trends():
    return render_template(
        'trends.html',
        active_page='trends'
        )

#################################### TWEETS ####################################
@app.route('/tweets')
def tweets():
    result = sql.last_tweets()
    return render_template(
        '/tweets/tweets.html',
        active_page='tweets',
        result=result
        )

@app.route('/sample_stream')
def sample_stream():
    result = twitter.sample_stream()
    return f'{result}'

#################################### USERS #####################################
@app.route('/users')
def users():
    try:
        top_50 = sql.top_50()
        scanned = sql.scanned_users()
        return render_template(
            '/users/users.html',
            active_page='users',
            title='Top 50 Users',
            top_50=top_50,
            scanned=scanned
            )
    except Exception as e:
        return render_template('error.html', error=e)

@app.route('/ajax', methods=['GET','POST'])
def ajax():
    data = json.loads(request.data.decode())
    print(data["name"])
    return 'yes'
    #if request.method == 'POST':
    #    print(request.data.decode())
    #    return 'post'
    #if request.method == 'GET':
    #    print(request.data.decode())
    #    return 'get'

@app.route('/users/<id>')
def users_id(id):
    result = sql.get_user_by_id(id)
    return render_template(
        '/users/profile.html',
        active_page='users',
        title=result[1],
        user_id=result[0],
        result=result
        )

@app.route('/users/<id>/followers')
def users_followers(id):
    result = sql.user_followers(id, 1000)
    user = sql.get_user_by_id(id)
    return render_template(
        '/users/grid.html',
        active_page='users',
        sub_menu='followers',
        user_id=user[0],
        title=user[1],
        result=result
        )

@app.route('/users/<id>/following')
def users_following(id):
    result = sql.user_following(id)
    user = sql.get_user_by_id(id)
    return render_template(
        '/users/grid.html',
        active_page='users',
        sub_menu='following',
        user_id=user[0],
        title=user[1],
        result=result
        )

@app.route('/users/<id>/mutual')
def users_mutual_following(id):
    result = sql.mutual_following(id)
    user = sql.get_user_by_id(id)
    return render_template(
        '/users/grid.html',
        active_page='users',
        sub_menu='mutual',
        user_id=user[0],
        title=user[1],
        result=result
        )

@app.route('/users/<id>/timeline')
def users_timeline(id):
    try:
        user = sql.get_user_by_id(id)
        last_tweet = sql.last_tweet_date(id)

        if last_tweet[0] is not None:
            result = twitter.timeline(id, start_time=last_tweet[0])
            if result['meta']['result_count'] > 1:
                controller.add_timeline(result)
            result = sql.timeline(id)
        else:
            result = twitter.timeline(id)
            if result['meta']['result_count'] > 0:
                controller.add_timeline(result)
            result = sql.timeline(id)


        #if result['meta']['result_count'] > 0:
        #    save_json(result, filename=user[2], path='./data/tweets')
        #    controller.add_timeline(result)
        #    for tweet in result['data']:
        #        tweet.update(
        #            {'created_at': controller.pretty_time(tweet['created_at'])})

        return render_template(
            '/users/timeline.html',
            active_page='users',
            sub_menu='timeline',
            title=user[1],
            user_id=user[0],
            result=result
            )

    except Exception as e:
        return render_template('error.html', error=e)

@app.route('/users/<id>/settings')
def users_settings(id):
    user = sql.get_user_by_id(id)
    result = ''
    return render_template(
        '/users/settings.html',
        active_page='users',
        sub_menu='settings',
        title=user[1],
        user_id=user[0],
        result=result
        )

@app.route('/users/<id>/add_user_and_follows')
def add_user_and_follows(id):
    result = controller.add_user_and_follows(id)
    return f'{result}'

################################### SETTINGS ###################################
@app.route('/settings')
def settings():
    account = sql.account()[0]
    account = {
        'username': account[0],
        'bearer_key': account[1]
    }
    user = sql.get_user_by_username(account['username'])
    if user:
        followers = sql.user_followers(user[0])
        follows = sql.user_followers(user[0])
    else:
        followers = []
        follows = []

    return render_template(
        'settings.html',
        active_page='settings',
        account=account,
        followers=followers,
        follows=follows
        )

@app.route('/settings/update_account', methods=['GET','POST'])
def update_account():
    if request.method == 'POST':
        global twitter
        try:
            sql.update_account(request.form)
            bearer_key = request.form['bearer_key']
            controller.update_twitter_api(bearer_key)
            twitter = TwitterAPI(bearer_key)
            return redirect('/settings')
        except:
            raise

if __name__ == '__main__':
    app.run(threaded=True, debug=True, port=5000)
