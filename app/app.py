'''
Twitter App
'''
from flask import Flask, request, redirect, jsonify, render_template
import time
import datetime
import json
from .twitter import TwitterAPI
from .db import Sqlite
from . import controller
from . import nlp
from collections import Counter

from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.utils import simple_preprocess
from sklearn.manifold import TSNE

app = Flask(__name__)
sql = Sqlite('app/db/db.sqlite')
bearer_key = sql.get_bearer_key()

if bearer_key:
    twitter = TwitterAPI(bearer_key[0])

#################################### INDEX #####################################
@app.route('/')
def index():
    return render_template(
        'index.html',
        active_page='index'
        )

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

@app.route('/users/<username>')
def users_id(username):
    start = time.time()
    user = sql.get_user_by_username(username)
    tweets = sql.get_user_timeline(username)
    clean_tweets = []

    for tweet in tweets:
        preprocessed_text = nlp.preprocessing(tweet[1]).split()
        lemmatized_text = nlp.lemmatization(preprocessed_text)
        clean_text = nlp.remove_stopwords(lemmatized_text)
        clean_tweets.append(clean_text)

    #dictionary = nlp.gensim.corpora.dictionary.Dictionary(result)
    #doc_term_matrix = [dictionary.doc2bow(text) for text in result]
    #Lda = nlp.gensim.models.ldamodel.LdaModel
    #ldamodel = Lda(doc_term_matrix, num_topics=5, id2word=dictionary, passes=10)

    cv = nlp.CountVectorizer()
    cd = cv.fit_transform([' '.join(tweet) for tweet in clean_tweets])
    lda = nlp.LDA(n_components=5)
    lda.fit(cd)

    topics = []
    for index, topic in enumerate(lda.components_):
        topics.append([cv.get_feature_names()[i] for i in topic.argsort()[-5:]])

    topics = nlp.flatten_list(topics)
    topics = Counter(topics)

    total = time.time() - start

    return render_template(
        '/users/profile.html',
        active_page='users',
        title=user[1] + ' - ' + str(total),
        username=user[2],
        user=user,
        topics=topics
        )
@app.route('/users/<username>/followers')
def users_followers(username):
    result = sql.get_user_followers(username, 1000)
    user = sql.get_user_by_username(username)
    return render_template(
        '/users/grid.html',
        active_page='users',
        sub_menu='followers',
        username=user[2],
        title=user[1],
        result=result
        )

@app.route('/users/<username>/following')
def users_following(username):
    result = sql.get_user_following(username, 1000)
    user = sql.get_user_by_username(username)
    return render_template(
        '/users/grid.html',
        active_page='users',
        sub_menu='following',
        username=user[2],
        title=user[1],
        result=result
        )

@app.route('/users/<username>/mutual')
def users_mutual_following(username):
    result = sql.get_mutual_following(username)
    user = sql.get_user_by_username(username)
    return render_template(
        '/users/grid.html',
        active_page='users',
        sub_menu='mutual',
        username=user[2],
        title=user[1],
        result=result
        )

@app.route('/users/<username>/timeline')
def users_timeline(username):
    try:
        user = sql.get_user_by_username(username)
        last_tweet = sql.get_user_last_tweet_date(username)

        user_id = user[0]
        username = user[2]

        if last_tweet[0] is not None:
            result = twitter.timeline(user_id, start_time=last_tweet[0])
            if result['meta']['result_count'] > 0:
                controller.add_timeline(result)
            result = sql.get_user_timeline(username, limit=40)
        else:
            result = twitter.timeline(user_id)
            if result['meta']['result_count'] > 0:
                controller.add_timeline(result)
            result = sql.get_user_timeline(username, limit=40)

        return render_template(
            '/users/timeline.html',
            active_page='users',
            sub_menu='timeline',
            title=user[1],
            username=user[2],
            user=user,
            result=result
            )

    except Exception as e:
        return render_template('error.html', error=e)

@app.route('/users/<username>/settings')
def users_settings(username):
    user = sql.get_user_by_username(username)
    result = ''
    return render_template(
        '/users/settings.html',
        active_page='users',
        sub_menu='settings',
        title=user[1],
        username=user[2],
        result=result
        )

@app.route('/users/<username>/add_user_and_follows')
def add_user_and_follows(id):
    result = controller.add_user_and_follows(id)
    return f'{result}'

################################### SETTINGS ###################################
@app.route('/settings/scan')
def scan():
    result = controller.add_user_and_follows('arseniytyurin')
    return f'{result}'

@app.route('/settings')
def settings():
    account = sql.account()[0]
    account = {
        'username': account[1],
        'bearer_key': account[2]
    }
    user = sql.get_user_by_username(account['username'])

    return render_template(
        'settings.html',
        active_page='settings',
        account=account,
        )

@app.route('/settings/update_account', methods=['GET','POST'])
def update_account():
    if request.method == 'POST':
        global twitter
        try:
            sql.update_account(request.form)
            bearer_key = request.form['bearer_key']
            twitter = TwitterAPI(bearer_key)
            controller.update_twitter_api(bearer_key)
            #user = twitter.user_lookup(username=request.form['username'])
            return redirect('/settings')
        except Exception as e:
            return f'{e}'
