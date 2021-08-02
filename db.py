import sqlite3
from utils import sqlite_escape

class Sqlite:

    def __init__(self, path):
        try:
            self.connection = sqlite3.connect(path, check_same_thread=False)
            self.cursor = self.connection.cursor()
        except:
            print(f"Can't connect to sqlite db: {path}")
            raise

    def test(self):
        result = self.cursor.execute('select * from accounta;').fetchall()
        return result

    def update_account(self, data):

        username = data['username']
        bearer_key = data['bearer_key']

        result = self.cursor.execute(
            """
                SELECT COUNT(*)
                FROM account;
            """
            ).fetchall()
        if result[0][0] == 0:
            self.cursor.execute(
                f"""
                    INSERT INTO account
                    VALUES ('{username}', '{bearer_key}');
                """
                )
            self.connection.commit()
        else:
            self.cursor.execute(
                f"""
                    UPDATE account
                    SET username='{username}',
                        bearer_key='{bearer_key}';
                """
                )
            self.connection.commit()

    def account(self):
        result = self.cursor.execute(
            """
                SELECT *
                FROM account
                LIMIT 1;
            """
            ).fetchall()
        if result:
            return result
        else:
            return [('','','')]

    def get_bearer_key(self):
        result = self.cursor.execute(
            f"""
                SELECT bearer_key
                FROM account
                LIMIT 1;
            """
            ).fetchall()
        return result

    def get_user_by_id(self, id):
        result = self.cursor.execute(
            f"""
                SELECT *
                FROM users
                WHERE id = {id}
                LIMIT 1;
            """
            ).fetchone()
        return result

    def get_user_by_username(self, username):
        result = self.cursor.execute(
            f"""
                SELECT *
                FROM users
                WHERE username = '{username}';
            """
            ).fetchone()
        return result

    def check_user_id(self, id):
        result = self.cursor.execute(
            f"""
                SELECT EXISTS (
                    SELECT 1
                    FROM users
                    WHERE id = {id}
                    );
            """
            ).fetchall()
        return result[0][0]

    def check_tweet_id(self, id):
        result = self.cursor.execute(
            f"""
                SELECT EXISTS (
                    SELECT 1
                    FROM tweets
                    WHERE id = {id}
                    );
            """
            ).fetchall()
        return result[0][0]

    def show_tables(self):
        result = self.cursor.execute(
            """
                SELECT name
                FROM sqlite_master
                WHERE
                TYPE='table';
            """
            ).fetchall()
        return result

    def top_50(self):
        result = self.cursor.execute(
            f"""
                SELECT *
                FROM users
                ORDER BY followers_count
                DESC LIMIT 50
            """
            ).fetchall()
        return result

    def set_scanned(self, id, value):
        self.cursor.execute(
            f"""
                UPDATE users
                SET scanned = {value}
                WHERE id = {id};
            """
            )
        self.connection.commit()

    def scanned_users(self, limit=20):
        """ Get scanned users """
        result = self.cursor.execute(
            f"""
                SELECT *
                FROM users
                WHERE scanned = 1
                LIMIT {limit};
            """
        ).fetchall()
        return result

    def user_followers(self, id, limit=1000):
        """ Select user's followers """
        result = self.cursor.execute(
            f"""
                SELECT *
                FROM users
                WHERE id IN (
                    SELECT user_id
                    FROM following
                    WHERE following_id = {id}
                    LIMIT {limit}
                );
            """
        ).fetchall()
        return result

    def user_following(self, id, limit=1000):
        """ Select user's following """
        result = self.cursor.execute(
            f"""
                SELECT *
                FROM users
                WHERE id IN (
                    SELECT following_id
                    FROM following
                    WHERE user_id = {id}
                    LIMIT {limit}
                );
            """
        ).fetchall()
        return result

    def check_following(self, user_id, following_id):
        """ Check if following exists user_id -> following_id """
        result = self.cursor.execute(
            f"""
                SELECT EXISTS (
                    SELECT 1 FROM following
                    WHERE user_id = {user_id}
                    AND following_id = {following_id})
                    LIMIT 1;
            """
        ).fetchall()
        return result[0][0]

    def add_tweet(self, fields, values):
        pass

    def add_user(self, fields, values):
        """
        Add user to the `users` table
        """
        try:
            self.cursor.execute(
                f"""
                    INSERT INTO users {fields}
                    VALUES (
                        '{values[0]}', -- id
                        '{sqlite_escape(values[1])}', -- name
                        '{values[2]}', -- username
                        '{values[3]}', -- created_at
                        '{sqlite_escape(values[4])}', --location
                        '{sqlite_escape(values[5])}', -- description
                        '{values[6]}', -- verified
                        '{values[7]}', -- profile_image_url
                        '{values[8]}', -- tweet_count
                        '{values[9]}', -- followers_count
                        '{values[10]}', -- following_count
                        '{values[11]}' -- last_updated
                        );
                """
            )
            self.connection.commit()
        except:
            raise

    def delete_user(self, id):
        self.cursor.execute(
            f"""
                DELETE FROM users
                WHERE id = {id};
            """
        )
        self.connection.commit()

    def tweet_time(self):
        result = self.cursor.execute(
            """
                SELECT STRFTIME('%H', created_at) AS hours, count(*)
                FROM tweets
                GROUP BY hours
            """
        ).fetchall()
        return result

    def tweet_length_distribution(self):
        result = self.cursor.execute(
        """
            SELECT tweets_length, COUNT(*)
            FROM (
                SELECT
                    CASE
                        WHEN LENGTH(text) BETWEEN 0 AND 50 THEN '(0, 50)'
                        WHEN LENGTH(text) BETWEEN 50 AND 100 THEN '(50, 100)'
                        WHEN LENGTH(text) BETWEEN 100 AND 150 THEN '(100, 150)'
                        WHEN LENGTH(text) BETWEEN 150 AND 200 THEN '(150, 200)'
                        WHEN LENGTH(text) BETWEEN 200 AND 250 THEN '(200, 250)'
                        WHEN LENGTH(text) BETWEEN 250 AND 300 THEN '(250, 300)'
                        WHEN LENGTH(text) > 300 THEN '(300+)'
                    END AS tweets_length
                FROM tweets
                )
            GROUP BY tweets_length;
        """
        ).fetchall()
        return result

    def average_tweet_length(self):
        '''
        Returns average tweet length between verified and not verified accounts
        '''
        result = self.cursor.execute(
            """
                SELECT t1.verified, AVG(t2.avg_len)
                FROM users AS t1
                JOIN (
                    SELECT author_id, LENGTH(text) AS avg_len
                    FROM tweets
                    ) AS t2
                ON t1.id = t2.author_id
                GROUP BY t1.verified;
            """
        ).fetchall()
        return result

    def rank_mutual_following(self):
        """
        This request returns users who have most mutual following in the
        sorted order
        """
        result = self.cursor.execute(
        """
            WITH scanned_ids AS (SELECT id FROM users WHERE scanned=1)
            SELECT t1.name, t2.followers
            FROM users AS t1
            JOIN (
                SELECT following_id, COUNT(user_id) AS followers
                FROM (
                    SELECT * FROM following
                    WHERE user_id IN (
                        SELECT following_id
                        FROM following
                        WHERE user_id IN scanned_ids
                        )
                    AND following_id IN scanned_ids
                    )
                    GROUP BY following_id
                ) AS t2
            ON t1.id = t2.following_id
            ORDER BY t2.followers DESC;
        """
        ).fetchall()
        return result

    def mutual_following(self, id):
        """ Returns mutual following of the user """
        result = self.cursor.execute(
        f"""
            SELECT *
            FROM users
            WHERE id IN (
                SELECT following_id
                FROM following
                WHERE user_id = {id}
                AND following_id IN (
                    SELECT user_id
                    FROM following
                    WHERE following_id = {id}
                    )
                )
        """
        ).fetchall()
        return result

    def add_following(self, user_id, following_id):
        self.cursor.execute(
        f"""
            INSERT INTO following
            VALUES ({user_id}, {following_id})
        """
        )
        self.connection.commit()

    def add_recently_viewed(self):
        self.cursor.execute('add user id')
        self.connection.commit()

    def recently_viewed(self):
        result = self.cursor.execute('select recently viewed users')
        return result

    def add_tweet(self, fields, values):
        try:
            self.cursor.execute(
            f"""
                INSERT INTO tweets {fields}
                VALUES (
                    '{values[0]}', -- id
                    '{sqlite_escape(values[1])}', -- text
                    '{values[2]}', -- created_at
                    '{values[3]}', -- author_id
                    '{values[4]}', -- conversation_id
                    '{values[5]}', -- in_reply_to_user_id
                    '{values[6]}', -- geo
                    '{values[7]}', -- referenced_tweets_id
                    '{values[8]}', -- referenced_tweets_type
                    '{values[9]}', -- retweet_count
                    '{values[10]}', -- reply_count
                    '{values[11]}', -- like_count
                    '{values[12]}', -- quote_count
                    '{values[13]}', -- lang
                    '{values[14]}' -- source
                    -- + default sentiment
                    );
            """
            )
            self.connection.commit()
        except:
            raise


    def last_tweet_date(self, id):
        result = self.cursor.execute(
            f"""
                SELECT MAX(created_at)
                FROM tweets
                WHERE author_id = {id};
            """
            ).fetchone()
        return result

    def timeline(self, id):
        result = self.cursor.execute(
            f"""
                SELECT *
                FROM tweets
                WHERE author_id = {id}
                ORDER BY created_at DESC
                LIMIT 100;
            """
            ).fetchall()

        return result

    def last_tweets(self, max_results=10):
        result = self.cursor.execute(
            f"""
                SELECT u.id,
                    u.username,
                    u.profile_image_url,
                    t.text,
                    t.created_at
                FROM users AS u
                JOIN tweets AS t
                ON u.id = t.author_id
                ORDER BY t.created_at DESC
                LIMIT {max_results};
            """
            ).fetchall()

        return result
