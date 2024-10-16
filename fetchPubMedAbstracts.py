### This script scraps the PubMed database using PubMed IDs of articles obtained via the request detailed in the article
### Useful information is then saved in csv format

from Bio import Entrez, Medline
import pandas as pd

#############################################################################################################
#CSV obtained from querying PubMed with the query specified in the article
pubDb = pd.read_csv("PubMedCsv/PubMedQuery.csv", sep=",")
### Enter your email address here
Entrez.email = 'your.email@address'
#############################################################################################################

def checkDoi(doi_list):
    #The AID from the record contains a list with pii and doi entries
    #This function outputs True for doi entries and false otherwise
    for string in doi_list:
        if "doi" in string:
            return True
    return False

def getDoi(AIDList):
    #The aid list contains piis and dois
    #dois are formatted as '<doi> [doi]'
    #This removes the last part and keeps only the doi
    for string in AIDList:
        if "doi" in string:
            return string[:-6]

def fixDoi(AIDs):
    #Removes pii entries and the ' [doi]' from the obtained 
    newDois = []
    for AIDList in AIDs:
        if not(checkDoi(AIDList)):
            newDois.append(None)
        else:
            newDois.append(getDoi(AIDList))
    return newDois
    
def getAbstracts(records):
    #Returns titles, abstacts and dois from the records queried using the PubMed ID
    abstracts = []
    for record in records:   
        try:
            abstracts.append(record["AB"])
        except KeyError:
            abstracts.append(None)
    return abstracts

def queryPubMed(pubIds, retmax=1000):    
    # Scraps the PubMed database with PubMed ids and outputs corresponding article titles, abstracts and dois
    # We can only request 1000 articles at a time so we make several queries
    #df = pd.DataFrame({"PMID":[], "title":[], "abstract":[], "doi":[]})
    abstracts = []
    for i in range(0, len(pubIds), retmax):
        j = i + retmax
        if j >= len(pubIds):
            j = len(pubIds)

        print(f"Fetching abstracts from {i} to {j}.")
        handle = Entrez.efetch(db="pubmed", id=','.join(pubIds[i:j]),
                        rettype="medline", retmode="text", retmax=retmax)    
        records = Medline.parse(handle)
        abstracts.extend(getAbstracts(records)) 
        #dois = fixDoi(dois)
        #df = pd.concat((df, pd.DataFrame({"PMID":pubIds[i:j], "title":titles,"abstract":abstracts, "doi":dois})))

    return abstracts
    

if __name__ == '__main__':
    pubIds = pubDb["PMID"].astype(str).to_list()
    abstracts = queryPubMed(pubIds)
    pubDb['abstract'] = abstracts
    #Renaming columns to deal with duplicates in other script
    pubDb = pubDb.rename(columns={'Title': 'title', 'Publication Year': 'year', 'DOI': 'doi'})
    pubDb.to_csv('queriedArticles/PubMedQueriedArticles.csv', index=False)