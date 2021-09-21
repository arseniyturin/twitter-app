'''
    -----------------------------
    Twitter API
    Author: Arseny Turin
    Date: Aug 8, 2021
    -----------------------------
    Functions:

    - user_lookup
    - followers_lookup
    - following_count
    - timeline
    - mentions
    - search_tweets

'''
import urllib.request
import json

class TwitterAPI:
    def __init__(self, bearer_token):
        '''Accept two arguments: bearer token and optional API version'''
        try:
            self._bearer_token = bearer_token
        except(ValueError):
            Exception('Please provide correct token')

        self.api = "https://api.twitter.com/2"
        print(f"You're using Twitter API version 2")

        # Specify what user or tweet information include into response
        self.FIELDS = {
            'user': [
                'id', #default
                'name', #default
                'username',
                'created_at',
                'protected',
                'location',
                'url',
                'description',
                'verified',
                'entities',
                'profile_image_url',
                'public_metrics'
            ],
            'tweet': [
                'id', #default
                'text', #default
                'created_at',
                'author_id',
                'conversation_id',
                'in_reply_to_user_id',
                'referenced_tweets',
                'geo',
                'public_metrics',
                'lang',
                'source',
            ]
        }


    def __repr__(self):
        return f'''
            TwitterAPI
            token: {self._bearer_token}
        '''

    def __print__(self):
        return f'''
            TwitterAPI
            token: {self._bearer_token}
        '''

    ################################# TWEETS ###################################
    def tweet_lookup(self, id):
        '''Returns a tweet with specific id'''
        pass

    def search_tweets(self, q, max_results=10):
        '''Query tweets with specific fields'''
        q = urllib.parse.quote(q)
        fields = ','.join(FIELDS['tweet'])
        url = (
            self.api +
            f'/tweets/search/recent?query={q}'
            f'&fweet.fields={fields}'
            f'&max_results={max_results}'
            )
        response = self._connect_to_endpoint(url)
        return response

    def sample_stream(self):
        '''https://api.twitter.com/2/tweets/sample/stream'''
        pass

    def timeline(self, id, start_time='2011-01-01T00:00:00Z', max_results=100):
        '''
        Retrieve user\'s tweets
        https://api.twitter.com/2/users/:id/tweets
        '''
        fields = ','.join(self.FIELDS['tweet'])
        url = (
            self.api +
            f'/users/{id}/tweets?'
            f'tweet.fields={fields}'
            f'&start_time={start_time}'
            f'&max_results={max_results}'
            )
        response = self._request(url)
        return response
        #except:
    #        return response

    def mentions(self, id, max_results=10):
        '''
        Retrieve user\'s mentions
        https://api.twitter.com/2/users/:id/mentions
        '''
        fields = ','.join(self.FIELDS['tweet'])
        url = (
            self.api +
            f'/users/{id}/mentions?'
            f'tweet.fields={fields}'
            f'&max_results={max_results}'
            )
        response = self._request(url)
        return response

    def filtered_stream(self):
        pass

    def sampled_stream(self):
        pass

    def likes(self):
        pass

    ################################## USERS ###################################
    def following_lookup(self, id, max_results=100):
        '''
        GET /2/users/:id/following
        '''
        fields = ','.join(self.FIELDS['user'])
        url = (
            self.api +
            f'/users/{id}/following?'
            f'user.fields={fields}'
            f'&max_results={max_results}'
            )
        response = self._request(url)
        return response

    def followers_lookup(self, id, max_results=100):
        '''
        GET /2/users/:id/followers

        Request information about user followers
        Takes user id as a parameter, max_results is optional (100 default)

        '''
        fields = ','.join(self.FIELDS['user'])
        url = (
            self.api +
            f'/users/{id}/followers?'
            f'user.fields={fields}'
            f'&max_results={max_results}'
            )
        response = self._request(url)
        return response

    def user_lookup(self, id='', username=''):
        '''
        Request information about user.\n
        Enter a single username or comma-separated usernames (ex: elonmusk,potato)
        '''

        fields = ','.join(self.FIELDS['user'])

        if id != '':
            url = self.api + f'/users/{id}?user.fields={fields}'
        if username != '':
            url = self.api + f'/users/by/username/{username}?user.fields={fields}'

        response = self._request(url)
        return response

    ################################# REQUEST ##################################
    def _request(self, url):
        '''
        Make a request to Twitter server.
        url - string (ex: http://twitter.com)
        headers - dict (ex: {'Header': 'Value', 'Header2': 'Value2'})
        '''
        headers = {'Authorization': f'Bearer {self._bearer_token}'}
        request = urllib.request.Request(url=url, headers=headers)
        with urllib.request.urlopen(request) as r:
            status = r.status
            if status != 200:
                raise Exception(f'Request returned an error: {status}')
            else:
                response = r.read().decode('utf-8')
                return json.loads(response)
