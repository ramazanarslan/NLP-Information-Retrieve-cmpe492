import datetime
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","neuroboun.settings")
django.setup()

from sys import argv
from Bio import Entrez
from neuroextractor.models import Article
from neuroextractor.models import Sentence

import nltk.data # to parse the abstract into sentences
#nltk.download('punkt')
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

import numpy
import re


def search(query, num_of_articles):
    Entrez.email = 'your.email@example.com'
    handle = Entrez.esearch(db='pubmed',
                            sort='relevance',
                            retmax=str(num_of_articles),
                            retmode='xml',
                            term=query)
    results = Entrez.read(handle)
    #results = Entrez.parse(handle)

    return results

def fetch_details(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'your.email@example.com'
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results

def save_given_articles(articles):
    for article_x in articles:
        title = article_x['MedlineCitation']['Article']['ArticleTitle']
        pubmed_id = article_x['MedlineCitation']['PMID']

        year = "0"
        try:
            year = article_x['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year']
        except:
            try:
                year = article_x['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['MedlineDate']
                year = (re.search(r".*?([0-9]{4}).*",year)).group(1)
                print("Hey MedlineDate is used.")
            except:
                pass
        try:
            year = int(year)
            if(year < 1900 or year > 2100):
                print(article_x['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['MedlineDate'])

        except:
            print(article_x['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['MedlineDate'])
        if(year == "0"):
            print("Hey year is 0")


        ids = article_x['PubmedData']['ArticleIdList']
        doi = [xx for xx in ids if xx.attributes['IdType']=='doi' ]
        doi = doi[0] if len(doi)!=0 else ""

        sentence_list = []
        try:
            abstract_list = article_x['MedlineCitation']['Article']['Abstract']['AbstractText']
            for sentence in abstract_list:
                sentences_x = sent_detector.tokenize((sentence).strip())
                for sentence_x in sentences_x:
                        sentence_list.append(sentence_x)
        except:
            pass
        abstract = (' '.join(sentence_list)).strip()


        keywords =""
        try:
            keyword_list = article_x['MedlineCitation']['KeywordList']
            for keyword in keyword_list[0]:
                keywords += (str(keyword) + "; ")
        except:
            pass



        article = Article(abstract= abstract,title=title, year=int(year), pubmed_id=pubmed_id, doi=doi ,keywords=keywords)
        article.save()

        sentence_x = title
        sentence_x = Sentence(article=article,type='title',sentence=sentence_x)
        sentence_x.save()


        for sentence_x in sentence_list:
            sentence_x = Sentence(article=article,type='abstract',sentence=sentence_x)
            sentence_x.save()


def run(query,num_of_articles,the_fetch_size):
    registered_ids = Article.objects.values_list("pubmed_id",flat=True)
    temp = search(query, num_of_articles)
    temp = temp['IdList']
    article_idlist = numpy.setdiff1d(temp,registered_ids)

    article_count = len(article_idlist)
    fetch_count = int(article_count/the_fetch_size)

    print("\n")
    print("In the local database, there are "+str(len(registered_ids))+" articles.")
    print("\n")
    print("The retrieving limit for number of articles to be downloaded from PubMed is " + str(num_of_articles) + " articles.")
    print("With the given query and the maximum article count limit, "+ str(len(temp))+ " articles are matched from PubMed.")
    print("\n")
    print("In the local database, "+str( len(temp)-article_count )+" of " + str(len(temp)) + " articles already exist.")
    print("There will be "+str(fetch_count)+" iterations and "+str(article_count) + " articles are going to be downloaded.")
    print("\n")

    if(article_count == 0):
        return

    for fetch_index in range(0,fetch_count):
        article_start_index = fetch_index*the_fetch_size
        ids_to_fetch = article_idlist[article_start_index:article_start_index+the_fetch_size]

        print("Now "+str(fetch_index+1) + "th "+str(the_fetch_size)+" articles are getting downloaded in "+str(article_count)+" articles")

        temp2 = fetch_details(ids_to_fetch);
        articles = temp2['PubmedArticle']
        save_given_articles(articles)

    if(article_count % the_fetch_size == 0):
        return

    print("Now last " + str(article_count % the_fetch_size) + " articles are getting downloaded in " + str(article_count) + " articles")
    temp2 = fetch_details(article_idlist[fetch_count*the_fetch_size:article_count]);
    articles = temp2['PubmedArticle']
    save_given_articles(articles)


fetch_size = 1000;
run("amygdala",400000, fetch_size)
