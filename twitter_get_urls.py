#!/usr/bin/env python

#kristenwidman
#Nov 20, 2012

import requests
import os
from link_shortener import create_link

def get_tweet_urls(query):
    payload = {'q': query}
    r = requests.get("http://search.twitter.com/search.json",
                        params=payload)
    js = r.json
    results = js[u'results']
    i = 0
    while i < 5:
        tweet = results[i]
        username = tweet['from_user']
        id_str = tweet['id_str']
        base_url = "https://twitter.com/"
        tweet_url = os.path.join(base_url,username,'status',id_str)
        created_date = tweet[u'created_at']
        text = tweet[u'text']
        short_url = create_link(tweet_url)
        print created_date, tweet_url, short_url, text,'\n'
        i += 1

get_tweet_urls("hackerschool")
