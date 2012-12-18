#!/usr/bin/env python

#kristenwidman
#Nov 20, 2012

#Link shortener

import sys
from os import path
import struct
import bitstring
import pymongo

DEBUG = True
BASE_URL = "http://www.kristenwidman.com"

chars = 'm6yf3rjupeiq854xzna9dw2ctbsv7hgk'

conn = pymongo.Connection("mongodb://localhost", safe=True)

db = conn.link
links = db.links

counters = db.counters
if counters.find_one() == None:
    counters.insert({'_id':'counter','c':1})

#future:
#add url check - valid structure?
#add duplicate url check in db
#post urls online and work out redirects

def create_link_2(long_url, email, date):
    '''goes with _encode_by_bits below. see there for notes'''
    counter = counters.find_and_modify({'_id':'counter'},{'$inc':{'c':1}})
    link_id = counter[u'c']
    if DEBUG: print 'link_id:',link_id
    links.insert({'_id':link_id, 'url':long_url, 'date':date, 'email':email})
    short_url_end = short_url_by_bit_encoding(link_id)
    if DEBUG: print long_url, short_url_end
    #short_url = path.join(BASE_URL, short_url_end)
    return short_url_end

def return_id(short_url):
    #if DEBUG: print path.basename(short_url)
    return _determine_db_id_from_short_url_2(short_url)

def return_full_url_2(db_id):
    cursor = links.find({'_id':db_id},{'_id':False,'url':True})
    url = cursor.next()[u'url'].encode('utf-8')
    if DEBUG: print url
    return url
    #will need to perform a redirect

def short_url_by_bit_encoding(number):
    '''alternative way to encode. Goes with _encode_by_bits. see notes
        there. Note this does not force bitstrings to be >=24 bits long.
    '''
    ba = bitstring.BitArray(hex(number))
    bitshifted = _bitshift(ba)
    encoded = _encode_by_bits(bitshifted)
    return encoded

def _encode_by_bits(bitarray):
    '''alternative way to encode the number to a short url.
        This way encodes by using the bit positions and 1/0 to create
        a string. In essence, each letter/num in chars is assigned a 
        position in the bitarray. If that bit is set, the char appears
        in the short-url.
    Problems with this approach:
        1. urls get long if have a lot of set bits.
        2. for short numbers, only a small subset of the chars array
            gets used (i.e. for binary strings of length 8, only the
            first 8 letters of chars are used)
        3. only works for numbers up to 32 bytes (len(chars)). As this
            is 2**32-1 (very large), probably not a problem for this.
    '''
    code = ''
    for i, bit in enumerate(bitarray):
        if bit:
            code += chars[i]
    if DEBUG: print code
    return code

def _decode_by_bits(char_string):
    '''decoding method to go with _encode_by_bits. see that method for
        more info.
    '''
    last_index = chars.index(char_string[-1]) + 1
    if last_index % 4 != 0:
        last_index += 4 - (last_index % 4)
    bitarray = bitstring.BitArray(last_index)
    for c in char_string:
        index = chars.index(c)
        bitarray[index] = 1
    return int(bitarray.bin, 2)

def _determine_db_id_from_short_url_2(short_url):
    '''Decode the short url into the db id. Goes with the _decode_by_bits
        and _encode_by_bits functions. See notes on _encode_by_bits for
        more info.
    '''
    if DEBUG: print 'decoding'
    if DEBUG: print short_url
    num = _decode_by_bits(short_url)
    bb = bitstring.BitArray(hex(num))
    b_back = _bitshift(bb).bin
    if DEBUG: print 'deshifted binary:  ',b_back
    return int(b_back,2)


#######################################################################


def create_link(long_url):
    #insert item into database with incremental id
    #return this translation
        #do I need a base url too? start with localhost
    counter = counters.find_and_modify({'_id':'counter'},{'$inc':{'c':1}})
    link_id = counter[u'c']
    if DEBUG: print 'link_id:',link_id
    links.insert({'_id':link_id, 'url':long_url})
    short_url_end = _determine_short_url(link_id)
    if DEBUG: print long_url, short_url_end
    return short_url_end

def return_full_url(short_url):
    db_id = _determine_db_id_from_short_url(short_url)
    if DEBUG: print 'db id is:',db_id
    cursor = links.find({'_id':db_id},{'_id':False,'url':True})
    url = cursor.next()[u'url'].encode('utf-8')
    if DEBUG: print url
    #will need to perform a redirect
    return url

def _determine_short_url(number):
    '''One way to make short urls using the _encode function.
    This way makes the bitstring at least 24 bits long, and
    reverses the last 24 bits, then encodes the bits using the
    remainder method in_encode.
    '''
    ba = bitstring.BitArray(hex(number))
    dif = 24 - len(ba.bin)
    if dif > 0:
        pre = '0b'+'0'*dif
        ba.prepend(pre)
    if DEBUG: print 'bin repr from test ',ba.bin
    bitshifted = ba[0:-24].bin + _bitshift(ba[-24:]).bin
    dec = int(bitshifted,2)
    if DEBUG:print 'decimal rep',dec
    encoded = _encode(dec)
    return encoded

def _determine_db_id_from_short_url(short_url):
    '''Decode the short url into the db id. Goes with the _encode and
        _decode functions. See notes on _encode for more info.
    '''
    if DEBUG: print 'decoding'
    d = _decode(short_url)
    bb = bitstring.BitArray(hex(d))
    b_back = bb[0:-24].bin + _bitshift(bb[-24:]).bin
    if DEBUG: print 'deshifted binary:  ',b_back
    return int(b_back,2)

def _encode(number):
    '''Encoding scheme 1. Encodes a number by taking the remainder of
        the number/length of the chars string repeatedly and adding
        the char at the index of the chars string specified by that
        remainder #.
    Problems with this approach:
        1. Bitstrings are at least 24 bits long, so the strings are often
            longer than with the other approach, esp for low numbers.
            (note: making bitstrings >=24 bits long is done because
            otherwise on decoding, several strings might map to the same
            number)
        2. Sequentially added urls (seq numbered ids in db) have very
            similar urls. Not ideal.
    '''
    length = len(chars)
    if number < length:
        return chars[number]
    else:
        return _encode(number/length) + chars[(number % length)]

def _decode(char_string):
    '''Turns a shortened url string into a number. Goes with _encode.
        See _encode for more notes.
    '''
    #last_index = chars.index(char_string[-1]) + 1
    #if last_index % 4 != 0:
        #last_index += 4 - (last_index % 4)
    #bitarray = bitstring.BitArray(last_index)

    length = len(chars)
    num = 0
    for i,c in enumerate(char_string[::-1]):
        num += chars.index(c) * 32**i
    return num

def _bitshift(bitarray):
    '''Preforms some sort of shifting of the bits passed in.
        Currently, reverses the bits, though this could be changed to
        something else.
    '''
    if DEBUG: print 'original bits      ',bitarray.bin
    bitarray.reverse()
    if DEBUG: print 'reversed bits      ',bitarray.bin
    return bitarray


def main(url):
    #test 1:
    short = create_link(url)
    url_back = return_full_url(short)
    assert url==url_back, 'urls are equal for test 1'

    #test 2:
    short2 = create_link_2(url)
    url_back2 = return_full_url_2(short2)
    assert url==url_back2, 'urls are equal for test2'
    print 'passed!'

if __name__ == "__main__":
    main('www.google.com')
