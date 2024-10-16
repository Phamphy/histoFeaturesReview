### This script removes duplicates from the obtained articles
### This is done by removing articles with duplicate titles and dois.

import pandas as pd
import glob

#############################################################################################################
queriedPaths = glob.glob('queriedArticles/*.csv')

acm = pd.read_csv(queriedPaths[0])
ieee = pd.read_csv(queriedPaths[1])
pubmed = pd.read_csv(queriedPaths[2])
#############################################################################################################

print(f'PubMed (n = {len(pubmed)}), IEEE Xplore (n = {len(ieee)}), ACM (n = {len(acm)})')

allArticles = pd.concat([acm, ieee, pubmed])[['title', 'year', 'doi']]
allArticles['title'] = allArticles['title'].str.lower()

#Filtering duplicate titles
uniqueTitles = allArticles.drop_duplicates(subset=['title'])
#Filtering duplicate dois
uniqueArticles = uniqueTitles[~(uniqueTitles.duplicated(subset=['doi'])) | (uniqueTitles['doi'].isnull())]

print(f'{len(uniqueArticles)}')
uniqueArticles.to_csv('uniqueArticles.csv')