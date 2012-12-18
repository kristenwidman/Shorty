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

def email_updates():
    cur = find_updated_records()
    email_dict = map_info_to_emails(cur)
    send_emails(email_dict)

def find_updated_records():
    now = datetime.utcnow()
    yesterday = now - timedelta(hours=24)
    cur = links.find({"date": {"$gt":yesterday}, "platform":{"$exists":True},
                    "browser":{"$exists":True}, "version":{"$exists":True},
                    "language":{"$exists":True}, "url":{"$exists":True}})
    return cur

def map_info_to_emails(cur):
    email_dict = {}
    for doc in cur:
        email_addr = doc[u'email']
        url = doc[u'url']
        _id = doc[u'_id']
        info = {'platform':doc[u'platform'],'version':doc[u'version'],
                'language':doc[u'language'],'browser':doc[u'browser']}
        item_dict = {}
        for item in info:
            l = []
            for r in info[item]:
                if r is not None:
                    i = r.encode('ascii')
                    l.append(i)
            if l != []:
                item_dict[item] = l
        if email_addr in email_dict:
            email_dict[email_addr][(url, _id)] = item_dict
        else:
            email_dict[email_addr] = {(url, _id): item_dict}
    return email_dict

def send_emails(email_dict):
    for entry in email_dict:
        to_email = entry
        text = "Here is your daily digest for shortened urls."
        for url, _id in email_dict[entry]:
            short_url = short_url_by_bit_encoding(_id)
            text += "\n\nShortened url, %s, (mapping to %s) received the following traffic in the last 24 hours:" % (short_url, url)
            for item in email_dict[entry][(url,_id)]:
                text += '\n%s: ' % (item)
                text += ', '.join(email_dict[entry][(url,_id)][item])
        print text
        send(to_email, text)

def format_message(to_email, text):
    msg = Message()
    msg['To'] = to_email
    msg['From'] = "widmanChristmasNames@gmail.com"
    msg['Subject'] = "Daily Link Shortener Digest"
    msg.set_payload(text)
    return msg

def send(to_email, text):
    msg = format_message(to_email, text)
    server = SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    server.sendmail(username, to_email, msg.as_string())
    server.quit()


if __name__=="__main__":
    email_updates()
