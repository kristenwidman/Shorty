#A link shortener and click recorder, a la bit.ly#

##[In Progress]##

##Overview:##
1. Scrapes twitter for tweets including a search string and pulls the top 5.
2. Inserts these into a mongodb collection with an incrementing id and
    computes a shortened url ending from the associated id. Two algorithms
    written to compute the url in a semi-random fashion using encoding
    to base 32 (undercase letters + numbers minus the confusing ones) and
    bit-swapping.
[TODO:
3. Urls posted online. Clicks are redirected to real url and information
    about the clicker is logged.
4. Text sent to me whenever a link is clicked.
5. Email digest about link-clicks and stats about browsers and operating
    systems sent once per day.
] 
