from neuroextractor.models import Article,Sentence,Acronym
from django.db.models import Count
from django.db.models import Q
import re

def get_statistics(start_year_val,end_year_val,fields,reg_ex_list):

    return len(search_by_regex__get_articles(start_year_val,end_year_val,fields,reg_ex_list)[1])

def search_by_regex(start_year_val,end_year_val,fields,reg_ex_list):

    [counts,article_list] = search_by_regex__get_articles(start_year_val,end_year_val,fields,reg_ex_list)
    sentence_list = search_by_regex__get_sentences(start_year_val,end_year_val,fields,reg_ex_list,article_list)

    article_list = article_list.order_by('-year')
    sentence_list=sentence_list.order_by('-article__year','id')

    return [sentence_list,counts,article_list]

def search_by_regex__get_articles(start_year_val,end_year_val,fields,reg_ex_list):

    article_list = Article.objects.all()
    counts = []
    if start_year_val != "" and end_year_val != "":
        article_list = article_list.filter(year__lte=end_year_val).filter(year__gte=start_year_val)
    elif start_year_val != "" and end_year_val == "":
        article_list = article_list.filter(year__gte=start_year_val)
    elif start_year_val == "" and end_year_val != "":
        article_list = article_list.filter(year__lte=end_year_val)

    if (fields == "allfields"):
        for reg_ex in reg_ex_list:
            article_list = article_list.filter(Q(abstract__iregex=reg_ex) | Q(title__iregex=reg_ex))
            counts.append(len(article_list.values("pubmed_id").order_by("pubmed_id").annotate(Count("pubmed_id"))))
        # search_result = search_result.filter(Q(type="title") | Q(type="abstract"))
        pass
    elif (fields == "title"):
        for reg_ex in reg_ex_list:
            article_list = article_list.filter(Q(title__iregex=reg_ex))
            counts.append(len(article_list.values("pubmed_id").order_by("pubmed_id").annotate(Count("pubmed_id"))))
    elif (fields == "abstract"):
        for reg_ex in reg_ex_list:
            article_list = article_list.filter(Q(abstract__iregex=reg_ex))
            counts.append(len(article_list.values("pubmed_id").order_by("pubmed_id").annotate(Count("pubmed_id"))))

    return [counts, article_list]

def search_by_regex__get_sentences(start_year_val,end_year_val,fields,reg_ex_list,article_list):
    search_result = Sentence.objects.all()

    search_result = search_result.filter(article__in=article_list)

    ORed_reg_ex = ('|').join(reg_ex_list)
    search_result = search_result.filter(Q(sentence__iregex=ORed_reg_ex) | Q(type='title'))

    return search_result

def color_up(search_result_object,reg_ex_list):
    color_list=["purple","blue","green"]
    color_len=len(color_list)
    reg_ex_list.reverse()
    reg_ex_len=len(reg_ex_list)
    search_result_list = list(search_result_object)

    for sentence_x in search_result_list:
        positions_list=[]
        for reg_ex_index in range(0,reg_ex_len):
            positions_list = positions_list+[(m.span(),reg_ex_index) for m in re.finditer(r''+reg_ex_list[reg_ex_index],sentence_x.sentence,flags=re.IGNORECASE)]

        # positions_list[positions_index][0][0]) element is ((a,b),c) and this returns (a)
        # a is start index and b is end index
        # c is reg_ex_index which is interpreted as priority and also be used for selecting color
        positions_len=len(positions_list)
        for positions_index in range(0,positions_len):
            a_current=positions_list[positions_index][0][0]
            b_current=positions_list[positions_index][0][1]
            c_current=positions_list[positions_index][1]
            # if priority is 0 pass
            if(c_current == 0):
                continue
            for positions_privileged_index in range(0,positions_index):

                a_priv=positions_list[positions_privileged_index][0][0]
                b_priv=positions_list[positions_privileged_index][0][1]
                c_priv=positions_list[positions_privileged_index][1]

                #if(c_priv == c_current): continue

                if(b_current<=a_priv):
                    continue
                if(b_priv<=a_current):
                    continue

                if((b_current>=a_priv) and (b_current<=b_priv) and (a_current<=a_priv)):
                    positions_list[positions_index]=((a_current,a_priv),c_current)
                    b_current=a_priv
                elif((a_current>=a_priv) and (a_current<=b_priv) and (b_current>=b_priv)):
                    positions_list[positions_index]=((b_priv,b_current),c_current)
                    a_current=b_priv
                elif((b_current>=b_priv) and (a_current<=a_priv)):
                    positions_list[positions_index]=((a_current,a_current),c_current) # ignore previous ones
                    b_current=a_current
                elif((a_current>=a_priv) and (b_current<=b_priv)):
                    positions_list[positions_index]=((a_current,a_current),c_current) # ignore previous ones
                    b_current=a_current

        positions_list.sort(key=lambda x:x[0],reverse=True) # sorted based on (x1,x2) pair
        # update sentence
        for positions in positions_list:

            pos_start = positions[0][0]
            pos_end = positions[0][1]
            pos_priority = positions[1]
            temp=sentence_x.sentence

            if(pos_start==pos_end):
                continue

            if(pos_priority<color_len):
                color=color_list[pos_priority]
            else:
                color=color_list[-1]

            sentence_x.sentence=temp[:pos_start]+ '<b><font color="'+color+'">'+temp[pos_start:pos_end]+'</font></b>'+temp[pos_end:]

    return search_result_list
