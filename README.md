# histoFeaturesReview
This repository contains the code that was used in the literature review: "Biological object feature-based approaches in histopathological images to address medical questions: a systematic review". 

Bib files in the cases of ACM and IEEE Xplore and a csv file for PubMed were downloaded after querying the databases with the keywords described in the Supplementary Materials of the article.
The articles were extracted from the different bib files and converted to a csv using the readCleanBib script. In the case of IEEE Xplore, a change in the database design during the writing of the article made it harder to apply our original query, so we included some code to filter the articles as we first did. The bib files from IEEE are obtained by not using the part of the query containing NOTs.

The csv obtained from PubMed does not originately contain abstracts, so the fetchPubMed abstract script scraps the PubMed database and adds the missing abstracts which are then used for the screening.

Finally, duplicates are removed using the removeDuplicates script.

The code to parse the bib files may not work on bib files downloaded from other databases.
