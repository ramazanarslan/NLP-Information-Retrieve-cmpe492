# imports needed and set up logging
import gensim 
import logging
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","neuroboun.settings")
django.setup()
from neuroextractor.models import Article
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
articles=Article.objects.all()

def read_input(articles):

    """This method reads the input file which is in gzip format"""
    
    logging.info("reading NeuroBoun ...this may take a while")
    
    
    for i, line in enumerate (articles): 
        if (i%1000==0):
            logging.info ("read {0} reviews".format (i))

        # do some pre-processing and return a list of words for each review text        
        yield gensim.utils.simple_preprocess (line.title)

# read the tokenized reviews into a list
# each review item becomes a serries of words
# so this becomes a list of lists
documents = list (read_input (articles))
#print(documents)
logging.info ("Done reading data file")    



model = gensim.models.Word2Vec (documents, size=150, window=5, min_count=2, workers=10)
model.train(documents,total_examples=len(documents),epochs=10)


w1 = "amygdala"
print( model.wv.most_similar (positive=w1))


