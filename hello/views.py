import requests
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import Greeting
#~~~ new stuff below ~~~
import nltk
from textblob import TextBlob
import time
import sys
import boto3
from boto3.dynamodb.conditions import Key, Attr
import urllib2
import re 
import newspaper 
from nltk.tokenize import sent_tokenize, word_tokenize
from newspaper import Article
nltk.data.path.append('./nltk_data/')
global articles
import itertools

def index(request):
    return redirect('https://github.com/daphneweinstein/critical-news-plugin')

def query(request):

    a = Article(url = request.get_full_path()[1:], language = 'en')
    a.download()
    a.parse()
    titletext = a.title + a.text
    entities = extract_entities(titletext)

    dynamodb = boto3.resource('dynamodb', region_name = 'us-west-2')
    global articles
    articles = dynamodb.Table('News_fulltext_deleteold')

    entitynum = len(entities)
    done = False
    articles_toret = []
    while entitynum > 0 and not done:
        for subset in itertools.combinations(entities, entitynum):
            if entitynum == 4:
                filter1 = four(*subset)
            elif entitynum == 3: 
                filter1 = three(*subset)
            elif entitynum == 2: 
                filter1 = two(*subset)
            else:
                filter1 = one(*subset)
            articles_toret = fetch_articles(filter1)
            if len(articles_toret) > 0:
                done = True
                break
        entitynum = entitynum - 1


    if (articles_toret == []):
        redirect_to = "http://google.com"
        return redirect(redirect_to)

    linkreturn = ''
    for i in range (0, len(articles_toret)):
        linkreturn = linkreturn + '\n<a href=' + articles_toret[i]['link'] + '>' + articles_toret[i]['title'] + '</a>'
    return HttpResponse('<pre>' + linkreturn + '\n</pre>')    

    #return redirect(redirect_to)

def fetch_articles(filter1):
    LinksToReturn = articles.scan(FilterExpression = filter1)
    #why is this cloned?
    ret = []
    for link in LinksToReturn['Items']:
        ret.append(link)
    return ret 

def one(s):
    return (Attr('title').contains(s1) | Attr('text').contains(s1)) 

def two(s1, s2):
    return (Attr('title').contains(s1) or Attr('text').contains(s1)) and (Attr('title').contains(s2) or Attr('text').contains(s2))

def three(s1,s2,s3):
    return (Attr('title').contains(s1) | Attr('text').contains(s1)) & (Attr('title').contains(s2) | Attr('text').contains(s2)) & (Attr('title').contains(s3) | Attr('text').contains(s3))

def four(s1,s2,s3, s4):
    return (Attr('title').contains(s1) | Attr('text').contains(s1)) & (Attr('title').contains(s2) | Attr('text').contains(s2)) & (Attr('title').contains(s3) | Attr('text').contains(s3)) & (Attr('title').contains(s4) | Attr('text').contains(s4))

def extract_entities(text):
    ret = []
    for sentence in sent_tokenize(text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sentence)), binary=True):
            if hasattr(chunk, 'label') and chunk.label:
                #need to detect tags of PERSON, GPE, ORGANIZATIOON
                if chunk.label() == 'NE': 
                    ret.append(str(chunk[0][0]))
                    if len(chunk) > 1:
                        ret.append(str(chunk[1][0]))
    
    if len(ret) > 4: 
        ret = ret[:4]
    return ret           
    


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})




