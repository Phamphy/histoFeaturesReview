### This script reads the information from the bib files downloaded from the ACM and IEEE, stored in an input folder
### Filters are applied to the IEEE files
### Useful information is saved in csv format

import glob
import re
import pandas as pd
import string


#############################################################################################################
### Path to bib files and dataset from which they were downloaded
bibPaths = glob.glob('IEEEBibFiles/*.bib')
#bibPaths = glob.glob('ACMBibFiles/*.bib')
database = 'IEEE'

### Filters
filtersTitle = ['deep' , 'cnn' , 'network' , 'networks' , 'transformer*' ,
                'radio*' , 'mri' , '3d' , 'three-dimension*' ,
                'magnetic' , 'tomograph*' , 'tomodensi*' , 'ultraso*' , 
                'ct' , 'mr' , 'pet','electro*','review'] #negative filter

filtersAbstract = ['video', 'endoscop*', 'cytolog*'] #negative filter

filtersKeywords = ['medical image processing', 'optical microscopy', 'feature extraction', 'image segmentation',
                    'cancer', 'image classification', 'biomedical optical imaging', 'biological tissues',
                    'learning (artificial intelligence)', 'diseases', 'tumours'] #positive filter
#############################################################################################################


def readBib(bibPath):
    print(f"Reading {bibPath}")
    file  = open(bibPath, 'r', encoding='utf8', errors = 'ignore') 
    fileContent = file.read()
    file.close()
    return fileContent

def splitBib(fileContent, databaseName):
    #splits the bib file content into a list of articles
    #removes all line breaks and @ symbols
    #IEEE and ACM format their bibfiles differently
    if databaseName == "IEEE":
        articleList = fileContent.replace("\n", "").split('}@')
        
    elif databaseName == "ACM":
        articleList = fileContent.split('\n\n@')
        #Removing extra line breaks
        articleList = list(map(lambda k: k.replace('\n', ''), articleList))
    #First character of the bib file is an @ symbol and has not been removed yet
    articleList[0] = articleList[0].replace('@', '')
    return articleList

def getArticlesInfo(articleList, databaseName):
    #fetches the article data using a regex
    #returns it in as a list of dictionaries
    infoList = []
    if databaseName == 'IEEE':
        for article in articleList:
            articleDict = regexSearchIEEE(article)
            infoList.append(articleDict)
    elif databaseName == 'ACM':
        for article in articleList:
            try:
                articleDict = regexSearchACM(article)
                infoList.append(articleDict)
            except KeyError:
                continue
    return infoList

def regexSearchIEEE(article):
    #In IEEE, all articles have a type, a title, an abstract, a year and some keywords
    #There are no spaces before and after the '=' sign
    regexSearch = re.search('(.+?){.*title={(.+?)}.*year={(.+?)}.*abstract={(.+?)}.*keywords={(.+?)}', article)
    articleType = regexSearch.group(1)
    title = regexSearch.group(2)
    year = regexSearch.group(3)
    abstract = regexSearch.group(4)
    keywords = regexSearch.group(5)
    try:
        #Not all articles have a doi
        #The doi is useful for finding duplicates
        regexSearchDoi = re.search('.*doi={(.+?)}', article) 
        doi = regexSearchDoi.group(1)
        if 'ISSN' in doi:
            #Deals with the edge case doi={} in which the next item is included in the regex result
            doi = None 
    except AttributeError:
        doi = None
    if articleType.lower() == 'inproceedings':
        journal = article.split('booktitle={')[1].split('}')[0]
    elif articleType.lower() == 'article':
        journal = article.split('journal={')[1].split('}')[0]
    articleDict = {'title': title, 'abstract': abstract, 'keywords': keywords, 
                'type': articleType, 'year': year, 'journal': journal, 'doi': doi}
    return articleDict


def regexSearchACM(article):
    #In ACM, some articles do not have an abstract nor keywords
    #There are spaces before and after the '=' sign
    regexSearch = re.search('(.+?){.*title = {(.+?)}.*year = {(.+?)}', article)
    articleType = regexSearch.group(1)
    title = regexSearch.group(2)
    year = regexSearch.group(3)
    try:
        regexSearchDoi = re.search('.*doi = {(.+?)}', article) 
        doi = regexSearchDoi.group(1) 
    except AttributeError:
        doi = None
    try:
        regexSearchAbstract = re.search('.*abstract = {(.+?)}', article) 
        abstract = regexSearchAbstract.group(1) 
    except AttributeError:
        abstract = None
    try:
        regexSearchKeywords = re.search('.*keywords = {(.+?)}', article) 
        keywords = regexSearchKeywords.group(1) 
    except AttributeError:
        keywords = None
    if articleType.lower() == 'inproceedings':
        journal = article.split('booktitle = {')[1].split('}')[0]
    elif articleType.lower() == 'article':
        journal = article.split('journal = {')[1].split('}')[0]
    else:
        raise KeyError(f'{title} is of type {articleType} and not journal or inproceedings')
    #print(articleType)
    articleDict = {'title': title, 'abstract': abstract, 'keywords': keywords, 
                'type': articleType, 'year': year, 'journal': journal, 'doi': doi}
    return articleDict
    
    
def positiveFilter(infoList, filters, infoDictKey):
    #keeps articles with a word in common with the filters
    passFilter = []
    for articleDict in infoList:
        keywordsSet = set(articleDict[infoDictKey].lower().split(';'))
        filtersSet = set(filters)
        intersections = keywordsSet.intersection(filtersSet)
        if len(intersections) > 0:
            passFilter.append(articleDict)
    return passFilter

def negativeFilter(infoList, filters, infoDictKey):
    #rejects articles with a word in common with the filters
    passFilter = []
    for articleDict in infoList:
        addArticle = True
        textToFilter = articleDict[infoDictKey].lower()
        for filteredWord in filters:
            wordsToFilter = textToFilter.split()
            for word in wordsToFilter:
                if re.match(filteredWord, word): #using re.match to take wildcards (*) into account
                    addArticle = False
        if addArticle:
            passFilter.append(articleDict)
    return passFilter

def list2Dict(infoList):
    #Reformats the obtained list of dictionaries into a dictionary of lists
    if len(infoList) == 0:
        return {}
    else:
        passFiltersDict = {}
        articleDict = infoList[0]
        for key in articleDict.keys():
            passFiltersDict[key] = []
        for articleDict in infoList:
            for key in articleDict.keys():
                passFiltersDict[key].append(articleDict[key])
    return passFiltersDict
        
    
if __name__ == '__main__':
    selectedArticles = []
    
    for bibPath in bibPaths:
        # Loading and cleaning data
        bibFile = readBib(bibPath)
        articleList = splitBib(bibFile, database)
        infoList = getArticlesInfo(articleList, database)
        # Filtering
        if database == 'IEEE':
            infoList = positiveFilter(infoList, filtersKeywords, 'keywords')
            infoList = negativeFilter(infoList, filtersTitle, 'title')
            infoList = negativeFilter(infoList, filtersAbstract, 'abstract')

        selectedArticles.extend(infoList)
    
    # Saving
    selectedArticlesDict = list2Dict(selectedArticles)
    df = pd.DataFrame(selectedArticlesDict)
    print(len(df))
    df.to_csv(f'queriedArticles/{database}QueriedArticles.csv', index=False)