import re
import requests
from requests.exceptions import Timeout
import time
from bs4 import BeautifulSoup
from bs4.element import Comment
import string
from html.parser import HTMLParser
import pickle
import numpy as np
import pandas as pd
import urllib.robotparser as urobot
import urllib.request
import unicodedata as ud
import math

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords, words

root_url = 'https://en.wikipedia.org/'
path_url = 'wiki/Web_mining'
target_url = root_url + path_url
urls_list = []
urls_list.append(target_url)

def robots(url):
    rp = urobot.RobotFileParser()
    rp.set_url(root_url + "robots.txt")
    rp.read()

    return rp.can_fetch("*", url)

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Start tag:", tag)

    def handle_endtag(self, tag):
        print("End tag :", tag)

    def handle_data(self, data):
        print("Data  :", data)


parser = MyHTMLParser()
parser.feed('<html><head><title>Test</title></head>')

def findLink(numOfLinks, urls_list):
    for url in urls_list:
        try:
            if robots(url):
                res = requests.get(url, timeout=1)
                urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', str(res.content))

                for _url in urls:
                    if len(urls_list) <= numOfLinks:
                        if _url not in urls_list and robots(_url):
                            urls_list.append(_url)
                    else:
                        urls_list.pop()
                        return
        except Exception as e:
            print('>> Error: ', e)

def text_filter(element):
    if element.parent.name in ['style', 'title', 'script', 'head', '[document]', 'class', 'a', 'li']:
        return False
    elif isinstance(element, Comment):
        '''Opinion mining?'''
        return False
    elif re.match(r"[\s\r\n]+", str(element)):
        '''space, return, endline'''
        return False
    return True

def wordList(url):
    r = requests.get(url, timeout=1)
    soup = BeautifulSoup(r.content, "html.parser")
    text = soup.findAll(text=True)
    filtered_text = list(filter(text_filter, text))
    word_list = []

    for line in filtered_text:
        _words = line.split(' ')
        for word in _words:
            word = word.lower()
            tmp_word = ''
            for w in word:
                try:
                    if w not in string.punctuation:
                        tmp_word += w
                except Exception as e:
                    print(">> Error: ", e)
            if tmp_word not in stopwords.words('english'):
                word_list.append(tmp_word)
    return word_list

def tf(url, key, word_list):
    total_words = len(word_list)
    count = 0
    for word in word_list:
        if word == key:
            count += 1
    tf = count / total_words
    return tf

def idf(n, data, key):
    df = len(data[key][0])
    idf = math.log(n / df)
    return idf

def tfidf(urls_list, data, data2):
    for url in urls_list:
        try:
            url_idx = urls_list.index(url)
            word_list = wordList(url)

            for word in word_list:
                if word.isalpha():

                    tf = tf(url, word, word_list)
                    idf = idf(numOfLinks, data2, word)
                    tf_idf = tf * idf

                    if data.get(word) is None:
                        data[word] = {url_idx: tf_idf}
                    else:
                        data[word].update({url_idx: tf_idf})
        except Exception as e:
            pass
        finally:
            time.sleep(1)
    return 1

def read_url(urls_list, data):
    for url in urls_list:
        try:
            url_idx = urls_list.index(url)
            print("URL: ", url_idx, " - ", url)
            word_list = wordList(url)

            for word in word_list:
                if word.isalpha():
                    if data.get(word) is None:
                        data[word] = [[url_idx], 1]
                    else:
                        if url_idx not in data[word][0]:
                            data[word][0].append(url_idx)
                        data[word][1] += 1
        except Exception as e:
            pass
        finally:
            time.sleep(1)
    return 1

data={}
tfidf_data={}
print("URLs...", end='')

numOfLinks = 2
findLink(numOfLinks, urls_list)

read_url(urls_list, data)
tfidf(urls_list, tfidf_data, data)
sorted_keys = sorted(data.keys())
tf_sorted_keys = sorted(tfidf_data.keys())

with open("output.txt", "w",encoding="utf-8") as f:
    output_line = "Word".ljust(50) + "Frequency".ljust(30) + "URL_idx".ljust(20) + "\n"
    f.writelines(output_line)
    f.writelines('---------------------------------------------------------------------\n\n')
    for key in sorted_keys:
        output_string = str(key).ljust(20) + str(data[key][1]).ljust(15) + str(data[key][0]).ljust(15) + "\n"
        f.writelines(output_string)

###

# with open(path, "wb") as f:
#     pickle.dump(data, f)