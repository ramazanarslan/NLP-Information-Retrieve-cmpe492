from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class Article(models.Model):
    abstract = models.TextField(null=True)
    year = models.IntegerField()
    pubmed_id = models.IntegerField(primary_key=True)
    doi = models.TextField(null=True)
    title = models.TextField()
    keywords = models.TextField()


    def __str__(self):
        return self.pubmed_id

class Sentence(models.Model):
    id = models.AutoField(primary_key=True)
    article = models.ForeignKey(Article,on_delete=models.CASCADE)
    type = models.TextField()
    sentence = models.TextField()

    def __str__(self):
        return self.sentence


class NeuroscienceTerm(models.Model):
    id = models.AutoField(primary_key=True)
    mesh_id = models.TextField(null=True)
    term = models.TextField()

    def __str__(self):
        return self.term

class Acronym(models.Model):
    id = models.AutoField(primary_key=True)
    acronyms = ArrayField(
        models.TextField(null=False),
    )
