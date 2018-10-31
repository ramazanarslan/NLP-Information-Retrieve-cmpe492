from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^results$', views.result_page, name='result_page'),
    url(r'^tables$', views.table_page, name='table_page'),
    url(r'^exportBasic$', views.exportBasic, name='exportBasic'),
    url(r'^exportTable$', views.exportTable, name='exportTable'),
    url(r'^$', views.search_page, name='search_page'),
]
