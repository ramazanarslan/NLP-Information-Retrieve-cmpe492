import re
from django import template
register = template.Library()

@register.simple_tag
def lookup(inputList, i, j, k, capacity1, capacity2):
    index = k * capacity2 + i * capacity1 + j
    return inputList[index]

@register.simple_tag
def divide_x_by_y(x,y):
    return x/y


@register.simple_tag
def tableCellLink(list1, list2, i, j, k, capacity1, capacity2, string1):
    result = "results?"+string1+"&query="
    result += list2[k * capacity1 + i]

    constraintList = list(map(str.strip, list1[j].strip().split(',')))

    for constraint in constraintList:
        if(constraint):
            result+="!!"+constraint

    return result


@register.simple_tag
def relatedList( nameList, baseIndex):
    result = ""
    nameListLength = len(nameList)
    baseName = nameList[baseIndex]

    for i in range(nameListLength):

        if(i != baseIndex):
            if(nameList[i] in baseName or baseName in nameList[i]):
                result += ","+str(i)

    if(result != ""):
        if (result[0] == ','):
            result = result[1:len(result)]

    return result


@register.simple_tag
def tabletitle(request,k):
    result = request
    result = re.sub(r'.*?tables\?','',result)

    part1 = re.split('%2C|,',re.sub(r'.*?preceding=(.*?)&main.*',r'\g<1>',result))
    part2 = re.split('%2C|,',re.sub(r'.*?main=(.*?)&succeeding.*',r'\g<1>',result))[k]
    part3 = re.split('%2C|,',re.sub(r'.*?succeeding=(.*?)&.*',r'\g<1>',result))

    part4 = re.sub(r'.*?succeeding=.*?&(.*?)&fields.*',r'\g<1>',result)
    nonquery1 = re.sub(r'.*&fields=(.*?)',r'\g<1>',result)
    startYear = ""
    endYear = ""
    try:
        startYear = re.match(r'.*&yearStart=(\d*?)&.*',result).group(1)
    except:
        pass

    try:
        endYear = re.match(r'.*&yearEnd=(\d*?)&.*',result).group(1)
    except:
        pass


    result2 = part2+" in: "+nonquery1

    if not startYear == "":
        result2 += "<br>Starting from:" + startYear

    if not endYear == "":
        result2 += " Until:" + endYear
    return result2
