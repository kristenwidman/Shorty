#!/usr/bin/env python

#kristenwidman
#Dec 17, 2012

from datetime import datetime, timedelta
from pymongo import MongoClient
from email.message import Message
from smtplib import SMTP
from constants import username, password
from link_shortener import short_url_by_bit_encoding

conn = MongoClient("mongodb://localhost", safe=True)

db = conn.link
links = db.links

def email_updates():
    cur = find_clicked_records()
    email_dict = map_info_to_emails(cur)
    send_emails(email_dict)
#TODO: add new records to email

def find_clicked_records():
    now = datetime.utcnow()
    yesterday = now - timedelta(hours=24)
    cur = links.aggregate([{"$unwind":"$clicks"},
                    {"$match": {"clicks.date":{"$gt": yesterday}}},
                    {"$project": {"_id":1, "platform":"$clicks.platform",
                    "version":"$clicks.version", "language":"$clicks.language",
                    "browser": "$clicks.browser", "email":1, "url":1}}])
    return cur

def map_info_to_emails(cur):
    email_dict = {}
    url_dict = {}
    for doc in cur[u'result']:
        email_addr = doc[u'email']
        url = doc[u'url']
        _id = doc[u'_id']
        info = {'platform':doc[u'platform'],'version':doc[u'version'],
                'language':doc[u'language'],'browser':doc[u'browser']}
        item_dict = {}
        if email_addr in email_dict:
            if (url,_id) in email_dict[email_addr]:
                email_dict[email_addr][(url,_id)].append(info)
            else:
                email_dict[email_addr][(url,_id)] = [info]
        else:
            email_dict[email_addr] = {(url,_id):[info]}
    print repr(email_dict)
    return email_dict

#{u'kristen.widman@gmail.com': {(u'https://twitter.com/isissuira/status/281153786410586113', 68): [{'platform': u'macos', 'version': u'23.0.1271.97', 'language': None, 'browser': u'chrome'}], (u'https://twitter.com/Isis_dalix33/status/281153939037114368', 65): [{'platform': u'macos', 'version': u'23.0.1271.97', 'language': None, 'browser': u'chrome'}], (u'https://twitter.com/Isis_Esp/status/281153904933236737', 67): [{'platform': u'macos', 'version': u'23.0.1271.97', 'language': None, 'browser': u'chrome'}, {'platform': u'macos', 'version': u'23.0.1271.97', 'language': None, 'browser': u'chrome'}]}}

def send_emails(email_dict):
    for entry in email_dict:
        to_email = entry
        text = "Here is your daily digest for shortened urls."
        for url, _id in email_dict[entry]:
            short_url = short_url_by_bit_encoding(_id)
            text += "\n\nShortened url, '%s', (mapping to %s) received the following traffic in the last 24 hours (each click event listed separately):" % (short_url, url)
            text +="\n---------------------------"
            for list_item in email_dict[entry][(url,_id)]:
                for item in list_item:
                    print list_item[item]
                    if list_item[item] is not None:
                        text += '\n%s: ' % (item)
                        text += list_item[item]
                text +="\n---------------------------"
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
