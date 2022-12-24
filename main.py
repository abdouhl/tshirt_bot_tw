import tweepy
from os.path import join, dirname
from dotenv import load_dotenv
import os
from deta import Deta

load_dotenv(join(dirname(__file__), '.env'))

twitter_auth_keys = {
	"consumer_key"        : os.environ.get("TSHIRT_BOT_CONSUMER_KEY"),
	"consumer_secret"     : os.environ.get("TSHIRT_BOT_CONSUMER_SECRET"),
	"access_token"        : os.environ.get("TSHIRT_BOT_ACCESS_TOKEN"),
	"access_token_secret" : os.environ.get("TSHIRT_BOT_ACCESS_TOKEN_SECRET")
}

auth = tweepy.OAuthHandler(
        twitter_auth_keys['consumer_key'],
        twitter_auth_keys['consumer_secret']
        )
auth.set_access_token(
        twitter_auth_keys['access_token'],
        twitter_auth_keys['access_token_secret']
        )
api = tweepy.API(auth)

deta = Deta(os.environ.get("DETA_KEY"))
done_comments = deta.Base("done_comments")

statuses = api.mentions_timeline(count = 200)
statuses.reverse()

comment_id = ""
status_id = ""
comment_screen_name = ""
tweet_it = False
for status in statuses:
    p = done_comments.fetch({"value": status.id_str})
    if p.count != 0:
        continue
    if status.in_reply_to_screen_name =="TurnTweetInto" or status.in_reply_to_screen_name == "abdou_hll":
        done_comments.put(status.id_str)
        continue
    try:
        full_status = api.get_status(id=status.id_str, tweet_mode = "extended" )
        full_in_replay_status = api.get_status(id=status.in_reply_to_status_id_str, tweet_mode = "extended" )
    except:
        done_comments.put(status.id_str)
        continue
    if '@TurnTweetInto' not in full_status.full_text[full_status.display_text_range[0]:full_status.display_text_range[1]]:
        done_comments.put(status.id_str)
        continue
    comment_id = status.id_str
    status_id = status.in_reply_to_status_id_str
    comment_screen_name = status.author.screen_name
    tweet_it = True
    break


if not tweet_it:
	statuses = api.search_tweets("@MakeItAQuote",result_type = "recent",count=200)
	statuses.reverse()
	for status in statuses:
		p = done_comments.fetch({"value": status.id_str})
		if p.count != 0:
			continue
		if status.in_reply_to_screen_name =="TurnTweetInto" or status.in_reply_to_screen_name == "abdou_hll":
			done_comments.put(status.id_str)
			continue
		try:
			full_status = api.get_status(id=status.id_str, tweet_mode = "extended" )
			full_in_replay_status = api.get_status(id=status.in_reply_to_status_id_str, tweet_mode = "extended" )
		except:
			done_comments.put(status.id_str)
			continue
		if '@TurnTweetInto' not in full_status.full_text[full_status.display_text_range[0]:full_status.display_text_range[1]]:
			done_comments.put(status.id_str)
			continue
		comment_id = status.id_str
		status_id = status.in_reply_to_status_id_str
		comment_screen_name = status.author.screen_name
		tweet_it = True
		break



if tweet_it :
	api.update_status(status=f'@{comment_screen_name}\nhttps://www.turntweetinto.com/clothes/{status_id}', in_reply_to_status_id = comment_id)
	done_comments.put(comment_id)



