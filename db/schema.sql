/* Twitter */

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  name TEXT,
  username TEXT,
  description TEXT,
  profile_image_url TEXT,
  location TEXT,
  created_at TEXT,
  tweet_count INTEGER,
  followers_count INTEGER,
  following_count INTEGER,
  verified INTEGER,
  last_updated TEXT,
  scanned INTEGER
);

DROP TABLE IF EXISTS tweets;
CREATE TABLE tweets (
  id INTEGER PRIMARY KEY,
  text TEXT,
  created_at TEXT,
  author_id INTEGER,
  conversation_id INTEGER,
  in_reply_to_user_id INTEGER,
  referenced_tweets TEXT,
  geo TEXT,
  retweet_count INTEGER,
  reply_count INTEGER,
  like_count INTEGER,
  quote_count INTEGER,
  lang TEXT,
  source TEXT,
  sentiment INTEGER
);

DROP TABLE IF EXISTS following;
CREATE TABLE following (
  user_id INTEGER,
  following_id INTEGER
);

DROP TABLE IF EXISTS account;
CREATE TABLE account (
  user_id INTEGER PRIMARY KEY,
  username TEXT,
  bearer_key TEXT
)

/*

DROP TABLE IF EXISTS mentions;
CREATE TABLE mentions (

);
DROP TABLE user_hashtags;
CREATE TABLE user_hashtags (
  user_id INTEGER,
  hashtag TEXT,
  count INTEGER,
  date TEXT
)

DROP TABLE hashtags;
CREATE TABLE hashtags (
  id INTEGER PRIMARY KEY,
  hashtag TEXT PRIMARY KEY
)

DROP TABLE tweets;
CREATE TABLE tweets (
  id INTEGER,
  text TEXT,
  sentiment INTEGER,

)

DROP TABLE topics;
CREATE TABLE topics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  topic TEXT
)
*/
