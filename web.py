#!/usr/bin/env python

#kristenwidman
#12/5/2012

import sys
import pymongo
from flask import Flask, render_template, redirect, request
import twitter_get_urls
import link_shortener

app = Flask(__name__)

conn = pymongo.Connection("mongodb://localhost", safe=True)

db = conn.link_shortener
links = db.links


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

@app.route("/tweets")
def display_shorts():
#display form
#take user input and return 5 (full) links
    return render_template('twitter.html')
    #get links
    #l = twitter_get_urls.get_tweet_urls("hacker")
    #for header in request.headers:
        #print header
    #return render_template('twitter.html', links=l)

#@app.route("/link_shortener")
#def shorten_links():

@app.route("/static-tweets")
def display_static_tweets():
    sl = ["m6y3ju", "m3ju"]
    return render_template('links.html', links=sl)

@app.route("/<variable>")
def url_redirection(variable):
    db_id = link_shortener.return_id(variable)
    url = link_shortener.return_full_url_2(db_id)
    print 'url to redirect to', url
    rel_headers = ['Referer', 'User-Agent', 'Accept-Language']
    try:
        browser = request.user_agent.browser
        platform = request.user_agent.platform
        version = request.user_agent.version
        language = request.user_agent.language
        print 'browser: %s,\nplatform: %s,\nversion: %s,\nlanguage: %s' % (browser, platform, version, language)
        links.update({'_id':db_id},{'$push': {'browser':browser, "platform":platform, "version":version, "language":language}})
        print 'added to db!'
    except:
        print 'error parsing user agent!'
    return redirect(url), 307

if __name__=="__main__":
    app.run(host='0.0.0.0', port=80)
