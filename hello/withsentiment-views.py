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
# Create your views here.






def index(request):
    a = Article(url = "http://www.foxnews.com/politics/2016/06/12/sanders-to-meet-tuesday-with-clinton-still-vows-to-run-campaign-until-convention.html", language = 'en')
    a.download()
    a.parse()
    time.sleep(1)

    title = a.title
    titletext = title
    #add text
    text = a.text

    ##################################################################################

    titletext = titletext + text
    entities = extract_entities(titletext)

    ##########################################################################

    sentiment_of_titleandtext = TextBlob(titletext).sentiment.polarity

    thelist = []
    for x in entities:
       thelist.append(str(x))

    dynamodb = boto3.resource('dynamodb', region_name = 'us-west-2')
    global articles
    articles = dynamodb.Table('News')

    number = len(thelist)
    towrite = [] 

    if(number == 0):
        towrite = [] 

    elif (number == 1):
        towrite = one(thelist[0])


    elif (number == 2):
        towrite = two(thelist[0], thelist[1])

        if(towrite == []):
            towrite = one(thelist[0])

        if(towrite == []):
            towrite = one(thelist[1])

    #number is three
    else:
        towrite = three(thelist[0], thelist[1], thelist[2])

        if(towrite == []):
            towrite = two(thelist[0], thelist[1])

        if(towrite == []):
            towrite = two(thelist[1], thelist[2])

        if(towrite == []):
            towrite = two(thelist[0], thelist[2])

        if(towrite == []):
            towrite = one(thelist[0])

        if(towrite == []):
            towrite = one(thelist[1])

        if(towrite == []):
            towrite = one(thelist[2])


    if (towrite == []):
        redirect_to = "http://google.com"


    else:
        numarticles = len(towrite)
        
        if numarticles > 3:
            numarticles = 3 

        lista = []

        for i in range (0, numarticles):
            url = towrite[i]['link']
            current = Article(url, language = 'en')
            current.download()
            current.parse()
            time.sleep(1)
            tit = current.title
            texta = tit 
            #add text
            textb = current.text
            tit = texta + textb
            senti = TextBlob(tit).sentiment.polarity
            lista.append(senti)

        champ = 0 
        champscore = 0 
        for i in range (0, numarticles):
            score = abs(lista[i] - sentiment_of_titleandtext)
            if score > champscore:
                champ = i
                champscore = score

        redirect_to = towrite[champ]['link']

        

    #return redirect(redirect_to)
    linkreturn = ''
    for i in range (0, numarticles):
        #print(towrite[i]['link'])
        linkreturn = linkreturn + towrite[i]['link'] + '\n'
    return HttpResponse('<pre>' + linkreturn + '</pre>')

def query(request):

    #thething"http://www.foxnews.com/politics/2016/06/12/sanders-to-meet-tuesday-with-clinton-still-vows-to-run-campaign-until-convention.html"
    a = Article(url = request.get_full_path()[1:], language = 'en')
    a.download()
    a.parse()
    time.sleep(1)

    title = a.title
    #print "title: ", title
    titletext = title

    #add text
    text = a.text

    #print "text: ", text 

    ##################################################################################

    titletext = titletext + text
    entities = extract_entities(titletext)
    #driver.close()

    ##########################################################################

    sentiment_of_titleandtext = TextBlob(titletext).sentiment.polarity
    #reftext =ref.text

    # text = Text(reftitle)
    # entities = text.entities
    #print "entities: ", entities

    thelist = []
    for x in entities:
       thelist.append(str(x))

    dynamodb = boto3.resource('dynamodb', region_name = 'us-west-2')
    global articles
    articles = dynamodb.Table('News')

    number = len(thelist)
    towrite = [] 

    if(number == 0):
        towrite = [] 

    elif (number == 1):
        towrite = one(thelist[0])


    elif (number == 2):
        towrite = two(thelist[0], thelist[1])

        if(towrite == []):
            towrite = one(thelist[0])

        if(towrite == []):
            towrite = one(thelist[1])

    #number is three
    else:
        towrite = three(thelist[0], thelist[1], thelist[2])

        if(towrite == []):
            towrite = two(thelist[0], thelist[1])
        if(towrite == []):
            towrite = two(thelist[1], thelist[2])
        if(towrite == []):
            towrite = two(thelist[0], thelist[2])

        if(towrite == []):
            towrite = one(thelist[0])
        if(towrite == []):
            towrite = one(thelist[1])
        if(towrite == []):
            towrite = one(thelist[2])


    if (towrite == []):
        redirect_to = "http://google.com"

    else:
        numarticles = len(towrite)
        
        if numarticles > 3:
            numarticles = 3 

        lista = []

        for i in range (0, numarticles):
            url = towrite[i]['link']
            current = Article(url, language = 'en')
            current.download()
            current.parse()
            time.sleep(1)
            tit = current.title
            texta = tit 
            #add text
            textb = current.text
            tit = texta + textb
            senti = TextBlob(tit).sentiment.polarity
            lista.append(senti)

        champ = 0 
        champscore = 0 
        for i in range (0, numarticles):
            score = abs(lista[i] - sentiment_of_titleandtext)
            if score > champscore:
                champ = i
                champscore = score

        redirect_to = towrite[champ]['link']

        

    return redirect(redirect_to)

def one(s):
    ret = []
    filter1 = Attr('description').contains(s)
    Weneed = articles.scan(FilterExpression = filter1)
    n = Weneed['Count']
    if(n == 0):
        return ret 
    else:
        for thing in Weneed['Items']:
            ret.append(thing)
        return ret 

def two(s1, s2):
    ret = [] 
    filter2 = Attr('description').contains(s1) & Attr('description').contains(s2)
    Weneed = articles.scan(FilterExpression = filter2)
    n = Weneed['Count']
    if(n == 0):
        return ret
    else:
        for thing in Weneed['Items']:
            ret.append(thing)
        return ret 


def three(s1,s2,s3):
    ret = []
    filter3 = Attr('description').contains(s1) & Attr('description').contains(s2) & Attr('description').contains(s3)
    Weneed = articles.scan(FilterExpression = filter3)
    n = Weneed['Count']

    if(n == 0):
        return ret

    else:
        for thing in Weneed['Items']:
            ret.append(thing)
        return ret 

def extract_entities(text):
    ret = []
    for sentence in sent_tokenize(text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sentence)), binary=True):
            #print chunk
            #traverseTree(chunk)
            if hasattr(chunk, 'label') and chunk.label:
                #need to detect tags of PERSON, GPE, ORGANIZATIOON
                if chunk.label() == 'NE': 
                    ret.append(chunk[0][0])
                    if len(chunk) > 1:
                        ret.append(chunk[1][0])
    
    if len(ret) > 3: 
        ret = ret[:3]
    return ret           
    


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})




