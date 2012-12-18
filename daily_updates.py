#!/usr/bin/env python

#kristenwidman
#Dec 17, 2012

from datetime import datetime, timedelta
from pymongo import Connection
from email.message import Message
from smtplib import SMTP
from constants import username, password
from link_shortener import short_url_by_bit_encoding

conn = Connection("mongodb://localhost", safe=True)

db = conn.link
links = db.links

def find_updated_records():
    now = datetime.utcnow()
    yesterday = now - timedelta(hours=2)
    cur = links.find({"date": {"$gt":yesterday}, "platform":{"$exists":True},
                    "browser":{"$exists":True}, "version":{"$exists":True},
                    "language":{"$exists":True}, "url":{"$exists":True}})
    return cur

#TODO: decode unicode for email so doesn't have 'u's' everywhere
#TODO: if multiple of same email, only send them one digest
def send_email(cur):
    for doc in cur:
        email = doc[u'email']
        url = doc[u'url']
        short_url = short_url_by_bit_encoding(doc[u'_id'])
        info = {'platform':doc[u'platform'],'version':doc[u'version'],
                'language':doc[u'language'],'browser':doc[u'browser']}
        text = "Your shortened url, %s, mapping to url, %s, received the following traffic in the last 24 hours:\n" % (short_url,url)
        for item in info:
            if info[item] != '[None]':
                text += '%s: %s,\n' % (item, info[item])
        print text
        email_username = username
        email_password = password
        msg = Message()
        msg['To'] = email
        msg['From'] = "widmanChristmasNames@gmail.com"
        msg['Subject'] = "Daily Link Shortener Digest"
        msg.set_payload(text)
        server = SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(email_username,email_password)
        server.sendmail(email_username, email, msg.as_string())
        server.quit()

'''
def send_email(cur):
    msg = format_email(cur)
    server = SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(email_username,email_ password)
    server.sendmail(email_username, email, msg.as_string())
    server.quit()
'''

if __name__=="__main__":
    cur = find_updated_records()
    send_email(cur)
