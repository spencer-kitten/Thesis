# Comment out before runt
import tweepy
API = 'MUTl3aSDpI5gXgyOCCAp0sJnq'
API_S = 'v8NzKaGoVRehTpSmOvajzAmojWlC6BFOr4RM7GOcMjZZ8wXxP0'
Access = '314210908-lWzqrMPOsQzzS8h2L0D9hWogdDTHhLlXafBb36Ep'
Access_S = 'SkRtc2hpu31JBtr6dGe7Rxd52qXUt1OFea6vKiwyk668L'

auth = tweepy.OAuthHandler(API,API_S)
auth.set_access_token(Access, Access_S)
api = tweepy.API(auth)
