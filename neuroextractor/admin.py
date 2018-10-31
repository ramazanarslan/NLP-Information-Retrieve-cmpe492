from django.contrib import admin
from neuroextractor.models import Article,NeuroscienceTerm,Sentence,Acronym

class AdminModels(admin.ModelAdmin):
    admin.site.register(Article)
    admin.site.register(Sentence)
    admin.site.register(NeuroscienceTerm)
    admin.site.register(Acronym)
