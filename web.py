#!/usr/bin/env python

#kristenwidman
#12/5/2012

from flask import Flask, render_template, redirect, request
import twitter_get_urls
import link_shortener

app = Flask(__name__)

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

@app.route("/tweets")
def display_shorts():
    #get links
    l = twitter_get_urls.get_tweet_urls("hackerschool")
    #render_template with links - call in loop? or somehow determine which
    return render_template('twitter.html', links=l)

@app.route("/link_shortener")
def shorten_links():
    

@app.route("/<variable>")
def url_redirection(variable):
    url = link_shortener.return_full_url_2(variable)
    print 'url to redirect to', url
    for header in request.headers:
        print header
    return redirect(url), 301

if __name__=="__main__":
    app.run(host='0.0.0.0', port=80)
