## Twitter App for topic modeling, user segmentation, sentiment analysis, etc..


**Current state**: access to Twitter Api to read users, tweets and store them in db

**To Do**: 

1. Put entire app in a folder with `app/__init__.py` as a module, have top level `.py` script to start app with gunicorn as a server
2. Polish interface, add general functionality, fix bugs
3. **Modeling**: focus on main goal - topic modeling. Things to add: user classification, identifying trends, etc. 
4. Host it on personal website

- **app.py** - main file with all the routes
- **controller.py** - functions that are used in app.py for twitter api
- **db.py** - functions for working with sqlite db
- **twitter.py** - access to twitter api
- **utils.py** - general helper functions
- **/data** - old folders with users and tweets in .json format
- **/db** - sqlite db for tweets and users
- **/static** - images, css
- **/templates** - html

