from django.shortcuts import render
from .models import Article,Sentence,Acronym
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from . import search
from .forms import Search_Form
from django.shortcuts import redirect
from django.db.models import Count
from django.db.models import Q
from copy import deepcopy
from itertools import product
import numpy
import re
import os
import shutil

from wsgiref.util import FileWrapper
from django.http import HttpResponse
from django.conf import settings
import datetime

from itertools import chain, combinations

from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required

def table_page(request):

    if 'main' in request.GET and request.GET['main'] != "":
        requestFilters = getTableRequestFilters(request)

        _fields = requestFilters[0]
        _yearStart = requestFilters[1]
        _yearEnd = requestFilters[2]
        _main = requestFilters[3]
        _preceding = requestFilters[4]
        _succeeding = requestFilters[5]
        _constraints = requestFilters[6]
        query_list = requestFilters[7]
        column_names = requestFilters[8]
        row_names = requestFilters[9]

        query_results = []
        for query_x in query_list:
            query_results.append(search.get_statistics(_yearStart,_yearEnd, _fields,processInputQueryComponentList(query_x)))

        main_query_size = len(_main)
        main_query_combination_size = len(_preceding)*len(_succeeding) # capacity of column
        constraint_combination_size = numpy.prod(list(map(len,_constraints))) if _constraints else 1 # capacity of row

        return render(request, "tables.html",{"nonqueryFilters": "fields=" + _fields + "&sYear=" + _yearStart + "&eYear=" + _yearEnd,
                                              "tablerequest": request.get_full_path(),
                                              "row_names": row_names, "col_names": column_names,
                                              "query_results": query_results,
                                              "capacity_of_column": constraint_combination_size, "capacity_of_row": main_query_combination_size,"capacity_of_table":constraint_combination_size*main_query_combination_size ,
                                              "range_table_size":range(main_query_size),  "range_table_column": range(main_query_combination_size), "range_table_row": range(constraint_combination_size)})

    else:
        print("redirect search")
        return redirect("search_page")

@login_required
def result_page(request):

    if 'query' in request.GET:

        requestFilters = getBasicRequestFilters(request)
        fields = requestFilters[0]
        start_year_val = requestFilters[1]
        end_year_val = requestFilters[2]
        input_query_list = requestFilters[3]

        processed_query_list = processInputQueryComponentList(input_query_list)

        search_result=search.search_by_regex(start_year_val,end_year_val,fields,processed_query_list)
        matched_sentences =search_result[0]
        matched_articles = search_result[2]

        stats ={}
        level_percents = []
        paginator = Paginator(matched_articles.order_by('-year','-pubmed_id'), 12)

        # intersect = Article.objects.all()
        # intersect = list(intersect.values_list("pubmed_id",flat=True))
        #
        # for i in range(1,4) :
        #     print("Page =" +  str(i))
        #     page_i = paginator.page(i)
        #     the_count = page_i.object_list.count()
        #     print(the_count)
        #     the_count= len(intersect)
        #     print(the_count)
        #     intersect =  set(intersect).intersection(list(page_i.object_list.values_list("pubmed_id",flat=True)))
        #     print("after intersect")
        #     print(len(intersect))
        #
        #     #intersect.intersection( page_i.object_list,intersect )
        #     #intersect = (paginator.page(1).object_list) & (paginator.page(2).object_list)
        # print("intersect...")
        # print(intersect)
        # print("intersect count...")
        # all_count = len(intersect)
        # print(all_count)

        page = request.GET.get('page', 0)

        if (int(page) != 0):
            try:
                paginated_articles = paginator.page(int(page))
                paginated_sentences = matched_sentences.filter(article__in=paginated_articles)
                search.color_up(paginated_sentences, processed_query_list)
            except PageNotAnInteger:
                [stats, level_percents] = result_stats(matched_sentences,search_result[1])
                paginated_articles = paginator.page(1)
                paginated_sentences = matched_sentences.filter(article__in=paginated_articles)
                search.color_up(paginated_sentences, processed_query_list)

            except EmptyPage:
                paginated_sentences = paginator.page(paginator.num_pages)

            paginated_sentences_grouped = [];temp2 = [];temp3 = []
            for sentence_x in paginated_sentences:
                if(sentence_x.type == 'title'):
                    if(len(temp3) != 0):
                        temp3.append(temp2)
                        paginated_sentences_grouped.append(temp3)
                        temp2 = []; temp3 = [];
                    temp3.append(sentence_x)
                elif(sentence_x.type == 'abstract'):
                    temp2.append(sentence_x)
            temp3.append(temp2)
            paginated_sentences_grouped.append(temp3)

        else:
            [stats, level_percents] = result_stats(matched_sentences, search_result[1])
            paginated_articles = paginator.page(1)
            paginated_sentences_grouped = [] # This line could be deleted after the implmentation is finished.

        return render(request,"result_list.html",
        {"page_number":int(page), "page_count":paginator.count,
        "paginated_sentences_grouped": paginated_sentences_grouped, "paginated_articles": paginated_articles,
        "fields":fields, "sYear":start_year_val,
        "eYear": end_year_val ,"filters": input_query_list ,
        "query":request.GET['query'] ,
        "stats":{"general_stats":stats, "levels": zip(input_query_list,search_result[1],level_percents)} })

    else:
        print("redirect search")
        return redirect("search_page")


def result_stats(result_data,level_counts):
    article_count_by_year = list(result_data.values("article__year").order_by("article__year").annotate(Count("article__pubmed_id",distinct=True)))

    article_count = len(result_data.values("article__pubmed_id").order_by("article__pubmed_id").annotate(Count("article__pubmed_id")))
    sentence_count= result_data.filter(Q(type="abstract") | Q(type="title")).count()
    title_count= result_data.filter(type="title").count()

    sentence_count = sentence_count - article_count # sentence count correction.

    article_count = '{:,}'.format(article_count)
    sentence_count = '{:,}'.format(sentence_count)
    title_count = '{:,}'.format(title_count)


    level_percents = ["-"]
    counts = list(level_counts)
    current_count = counts.pop(0)
    for the_count in counts:
        try:
            restriction = the_count*1.0/current_count *100
        except:
            restriction = 100.0
        level_percents.append('{:.2f}'.format(restriction))
        current_count = the_count

    statistics = {"article_count_by_year":str(article_count_by_year), "article_count":article_count, "sentence_count":sentence_count, "title_count":title_count}


    return [statistics,level_percents]

@login_required
def search_page(request):
    form = Search_Form()
    return render(request,"search.html",{})


def exportBasic(request):
    rootpath = "tmp/"

    exportBasicFileName = createfile_singlequery(getBasicRequestFilters(request), rootpath)
    exportBasicFilePath = rootpath + exportBasicFileName

    os.makedirs(exportBasicFilePath[:-4])
    shutil.move(exportBasicFilePath, exportBasicFilePath[:-4])

    shutil.make_archive(exportBasicFilePath[:-4], 'zip', exportBasicFilePath[:-4])

    f = open(settings.BASE_DIR+"/"+exportBasicFilePath[:-4]+".zip", "rb")
    wrapper = FileWrapper(f)

    shutil.rmtree(exportBasicFilePath[:-4])
    os.remove(exportBasicFilePath[:-4] + ".zip")

    response = HttpResponse(wrapper,content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="'+exportBasicFileName[:-4]+'.zip'+'"'
    return response

def exportTable(request):
    requestFilters = getTableRequestFilters(request)

    _fields = requestFilters[0]
    _yearStart = requestFilters[1]
    _yearEnd = requestFilters[2]
    _main = requestFilters[3]
    _preceding = requestFilters[4]
    _succeeding = requestFilters[5]
    _constraints = requestFilters[6]
    query_list = requestFilters[7]
    column_names = requestFilters[8]
    row_names = requestFilters[9]

    _yearStart = "none" if _yearStart == "" else _yearStart
    _yearEnd = "none" if _yearEnd == "" else _yearEnd

    exportFolderName = "Neuroboun_ExportTable__main_" + '_'.join(_main)+ "__preceding_"+ '_'.join(_preceding) + "__succeeding_"+ '_'.join(_succeeding)

    for constraints_x in _constraints:
        exportFolderName += "__constraint"+'_'.join(constraints_x)

    exportFolderName += "__fields_" + _fields + "__startyear_" + _yearStart + "__endyear_" + _yearEnd + "__downloaddate_" + datetime.datetime.now().strftime('%Y-%m-%d__%H-%M-%S')
    exportFolderName= re.sub(' ', '',exportFolderName)

    _yearStart = "" if _yearStart == "none" else _yearStart
    _yearEnd = "" if _yearEnd == "none" else _yearEnd


    rootpath = "tmp/"
    exportFolderPathTrick = rootpath + "downloaddate_" + datetime.datetime.now().strftime('%Y-%m-%d__%H-%M-%S')+"/"
    os.makedirs(exportFolderPathTrick)

    for query_x in query_list:
        createfile_singlequery([_fields, _yearStart,_yearEnd, query_x],exportFolderPathTrick)


    exportFolderPath = rootpath + exportFolderName
    shutil.make_archive(exportFolderPath, 'zip', exportFolderPathTrick)

    shutil.rmtree(exportFolderPathTrick)

    f = open(settings.BASE_DIR + "/"+ exportFolderPath+".zip", "rb")
    wrapper = FileWrapper(f)

    os.remove(exportFolderPath+".zip")

    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="'+exportFolderName+'.zip'+'"'
    return response

def createfile_singlequery(filters,rootpath):

    fields = filters[0]
    start_year_val = filters[1]
    end_year_val = filters[2]
    input_query_list = filters[3]
    processed_query_list = processInputQueryComponentList(input_query_list)

    search_result = search.search_by_regex(start_year_val, end_year_val, fields, processed_query_list)
    sentences = search_result[0]

    exportBasicFileName = createexportfilename(input_query_list,fields,start_year_val,end_year_val)
    exportBasicFilePath = rootpath + exportBasicFileName

    with open(exportBasicFilePath, "w+") as f:
        f.write("query\t" + ','.join(input_query_list))
        f.write("\n")
        f.write("fields\t" + fields)
        f.write("\n")
        if start_year_val == "":
            start_year_val = "undefined"
        f.write("start year\t" + start_year_val)
        f.write("\n")
        if end_year_val == "":
            end_year_val = "undefined"
        f.write("end year\t" + end_year_val)
        f.write("\n")
        f.write("download date=" + str(datetime.datetime.now()))
        f.write("\n")
        f.write("\n")

        f.write("field\tsentence\tPMID\tDate")
        for sentence in sentences:
            f.write("\n")
            f.write(str(sentence.type) + "\t")
            f.write(str(sentence.sentence) + "\t")
            f.write(str(sentence.article_id) + "\t")
            f.write(str(sentence.article.year))
    return exportBasicFileName

def createexportfilename(input_query_list,fields,start_year_val,end_year_val):

    start_year_val = "none" if start_year_val == "" else start_year_val
    end_year_val = "none" if end_year_val == "" else end_year_val

    exportfilename =  "Neuroboun_ExportBasic"+\
                          "__query_" + '_'.join(input_query_list) + \
                          "__fields_" + fields + "__startyear_" + start_year_val + "__endyear_" + end_year_val + \
                          "__downloaddate_" + datetime.datetime.now().strftime('%Y-%m-%d__%H-%M-%S') + ".csv"
    exportfilename= re.sub(' ', '',exportfilename)
    return exportfilename

def getBasicRequestFilters(request):

    fields = request.GET['fields']
    start_year_val = request.GET['sYear'] if 'sYear' in request.GET else  ""
    end_year_val = request.GET['eYear'] if 'eYear' in request.GET else ""
    input_query_list = request.GET['query'].split("!!")

    return [fields,start_year_val,end_year_val,input_query_list]

def getTableRequestFilters(request):
    _url = request.GET

    # -------------------------------------------------------------------

    _fields = _url['fields']  # if 'fields' in _url else ""
    _yearStart = _url['yearStart'] if 'yearStart' in _url else ""
    _yearEnd = _url['yearEnd'] if 'yearEnd' in _url else ""

    # -------------------------------------------------------------------

    _preceding = ([] if _url['preceding'] == "" else list(map(str.strip, _url['preceding'].strip().split(','))))
    _succeeding = ([] if _url['succeeding'] == "" else list(map(str.strip, _url['succeeding'].strip().split(','))))
    _main = list(map(str.strip, _url['main'].strip().split(',')))

    _preceding = [y for y in _preceding if y]
    _succeeding = [y for y in _succeeding if y]
    _main = [y for y in _main if y]

    _preceding.insert(0, "")
    _succeeding.insert(0, "")

    column_names = [(a, b, c) for b in _main for c in _succeeding for a in _preceding]
    column_names = [tuple(y for y in x if y) for x in column_names]
    column_names = list(map(" ".join, column_names))
    html_column_names = column_names

    # -------------------------------------------------------------------

    _raw_constraints = [x[1] for x in _url.lists() if x[0] == 'constraint'][0] if 'constraint' in _url else []
    _raw_constraints.reverse()

    _constraints = []
    for raw_constraint in _raw_constraints:
        if raw_constraint != "":
            _constraints.append(list(map(str.strip, raw_constraint.strip().split(','))))

    for constraint in _constraints:
        constraint.insert(0, "")

    row_names = list(product(*_constraints))
    row_names = [tuple(y for y in x if y) for x in row_names]
    html_row_names = list(map(",".join, row_names))

    # -------------------------------------------------------------------

    query_list = [(a, *b) for a in column_names for b in row_names]
    query_list = [tuple(y for y in x if y) for x in query_list]

    return [_fields,_yearStart,_yearEnd, _main, _preceding, _succeeding, _constraints, query_list, html_column_names, html_row_names ]

def processInputQueryComponentList(input_query_component_list):

    processed_query_list = []
    for input_query_component in input_query_component_list:

        processedInputQueryComponent = processInputQueryComponent(input_query_component)
        processed_query_list.append(processedInputQueryComponent)

    return processed_query_list

def processInputQueryComponent(input_query_component):

    input_query_component_parts = input_query_component.split(" ")
    component_parts_length = len(input_query_component_parts)

    indexed_constructions = []
    component_consecutive_indexpowerset = powerset_ofindexvalues_filterconsecutive(component_parts_length)

    get_indexed_component_constructions(component_consecutive_indexpowerset, component_parts_length,  [], 0, indexed_constructions)


    text_constructions = get_text_component_constructions(input_query_component_parts,indexed_constructions)

    processedQueryComponent_task1 = expand_text_constructions_with_acronymterms(text_constructions)
    processedQueryComponent_task2 = "((" + ")|(".join(processedQueryComponent_task1) + "))"
    processedQueryComponent_task3 = expand_extrawords(processedQueryComponent_task2.split(" "))
    processedQueryComponent_task4 = restrict_wordboundaries(processedQueryComponent_task3)

    result = processedQueryComponent_task4
    return result

def expand_text_constructions_with_acronymterms(text_constructions):
    acronymexpanded_text_constructions = []
    for construction in text_constructions:
        acronymexpanded_text_component_parts_subset_string = ""
        for text_component_parts_subset_string in construction:
            acronymexpanded_text_component_parts_subset_string += " " + expand_acroynmterms(text_component_parts_subset_string)[0]
        acronymexpanded_text_component_parts_subset_string = acronymexpanded_text_component_parts_subset_string[1:]
        acronymexpanded_text_constructions.append(acronymexpanded_text_component_parts_subset_string)
    acronymexpanded_text_constructions = set(acronymexpanded_text_constructions)

    return acronymexpanded_text_constructions

def get_text_component_constructions(input_query_component_parts,indexed_constructions):

    text_constructions = []
    for index_construction in indexed_constructions:
        text_construction = []
        for indexed_component_parts_subset in index_construction:
            text_component_parts_subset = input_query_component_parts[indexed_component_parts_subset[0]:indexed_component_parts_subset[len(indexed_component_parts_subset) - 1] + 1]
            text_component_parts_subset_string = " ".join(text_component_parts_subset)
            text_construction.append(text_component_parts_subset_string)
        text_constructions.append(text_construction)

    return text_constructions

def get_indexed_component_constructions( component_consecutive_indexpowerset, component_parts_length, currentconstruction, next_component_part_index,constructions ):

    for component_parts_subset in component_consecutive_indexpowerset:
        component_parts_subset_firstpart_index = component_parts_subset[0]

        if(component_parts_subset_firstpart_index == next_component_part_index):
            next_depth_currentconstruction = deepcopy(currentconstruction)
            next_depth_currentconstruction.append(component_parts_subset)
            next_depth_next_component_part_index = component_parts_subset[len(component_parts_subset)-1]+1
            get_indexed_component_constructions(component_consecutive_indexpowerset, component_parts_length, next_depth_currentconstruction,next_depth_next_component_part_index ,constructions)

    if(currentconstruction != []):
        currentconstruction_lastpart = currentconstruction[ len(currentconstruction)-1 ]
        currentconstruction_lastpart_index = currentconstruction_lastpart[len(currentconstruction_lastpart)-1]
        if(currentconstruction_lastpart_index == component_parts_length-1):
            constructions.append(currentconstruction)

def restrict_wordboundaries(query_component):
    result = "\W" + query_component + "\W"
    return result

def expand_extrawords(query_component_parts):
    result = " ((\w)* ){0,6}".join(query_component_parts)
    return result

def expand_acroynmterms(inputtext): # acronym table contains equivalent terms, acronyms and synonyms
    try:
        acronymentries = Acronym.objects.filter(acronyms__contains=[inputtext.lower()])
        if len(acronymentries) == 0:
            raise
        acronymslist = []
        for acronymentry in acronymentries:
            for acronym in acronymentry.acronyms:
                acronymslist.append(acronym)
        acronymslist = list(set(acronymslist))
        processed_input_query = "(" + "|".join(acronymslist) + ")"
        return [processed_input_query,True]

    except Exception as e1:
        return [inputtext,False]

def powerset_ofindexvalues_filterconsecutive(indexlength):
    result = []

    indices = range(indexlength)
    indices_powerset = list(powerset(indices))
    indices_powerset.remove(())

    for subset in indices_powerset:
        subset_consecutive = True

        prevelement = subset[0]
        for currentelement in subset[1:]:
            if( currentelement-prevelement == 1):
                pass
            else:
                subset_consecutive = False
            prevelement = currentelement
        if(subset_consecutive):
            result.append(subset)

    return result

def powerset(iterable):
    """
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    xs = list(iterable)
    # note we return an iterator rather than a list
    return chain.from_iterable(combinations(xs, n) for n in range(len(xs) + 1))
