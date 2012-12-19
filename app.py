#!/usr/bin/env python

#kristenwidman
#12/5/2012

from datetime import datetime
from pymongo import Connection
from flask import Flask, render_template, redirect, request
from twitter_get_urls import get_tweet_urls
from link_shortener import return_id, return_full_url_2

app = Flask(__name__)

conn = Connection("mongodb://localhost", safe=True)

db = conn.link
links = db.links

app.vars = {}

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

@app.route("/tweets", methods=['GET','POST'])
def input_search():
    if request.method == 'GET':
        return render_template('twitter.html')
    else:
        search_term = request.form['twitter_search']
        email = request.form['email']
        now  = datetime.utcnow()
        app.vars['search'] = search_term
    #get links
        l = get_tweet_urls(search_term, email, now)
    #for header in request.headers:
        #print header
        return render_template('links.html', links=l, title=app.vars['search'])

#@app.route("/link_shortener")
#def shorten_links():

@app.route("/static-tweets")
def display_static_tweets():
    sl = ["m6f", "yf"]
    return render_template('links.html', links=sl, title='Static Links')

@app.route("/<variable>") #"http://www.kristenwidman.com/<variable>")
def url_redirection(variable):
    db_id = return_id(variable)
    url = return_full_url_2(db_id)
    print 'url to redirect to', url
    rel_headers = ['Referer', 'User-Agent', 'Accept-Language']
    try:
        browser = request.user_agent.browser
        platform = request.user_agent.platform
        version = request.user_agent.version
        language = request.user_agent.language
        now  = datetime.utcnow()
        print 'browser: %s,\nplatform: %s,\nversion: %s,\nlanguage: %s' % (browser, platform, version, language)
        links.update({'_id':db_id},{'$push': {'clicks': {'date':now, 'browser':browser,
            "platform":platform, "version":version, "language":language}}})
        print 'added to db!'
    except:
        print 'error parsing user agent!'
    return redirect(url), 307

if __name__=="__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
