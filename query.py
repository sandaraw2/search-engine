# take a query

# split the query and stem it

# open the report.csv file and search for the tokens
# this is how it looks like in .csv for every entry where there is a list with the frequency of the word and dictionary of document ids: worri,"[3, {1, 2, 3}]"

# find and create a list of documents that are common document IDs between the token words

# go into url_id.csv and find the urls and print it
# this is what the .csv file looks like for each entry where it is the url and the documentID http://alderis.ics.uci.edu/amba2.html,8

import ast
import csv
from nltk.stem import PorterStemmer


def stem_query(query):
    """
    Stems the query using the Porter stemming algorithm.
    """
    stemmer = PorterStemmer()
    return [stemmer.stem(word) for word in query.split()]


def search_csv_for_tokens(csv_path, tokens):
    """
    Searches a CSV file for entries containing the specified tokens.
    Returns a list of common document IDs for matching entries.
    """
    document_ids_list = []

    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            word, entry = row
            word = word.strip('"')

            # assuming the format is as mentioned in your description
            frequency, document_ids = ast.literal_eval(entry)
            document_ids = set(document_ids)

            # check if any token in the query is present in the word
            if any(token.lower() in word.lower() for token in tokens):
                document_ids_list.append(document_ids)

    # flatten the list of sets to get all document IDs
    all_document_ids = [
        doc_id for doc_ids in document_ids_list for doc_id in doc_ids]

    return list(set(all_document_ids))


def retrieve_urls(csv_path, document_ids):
    """
    Retrieves URLs from a CSV file based on the given document IDs.
    """

    print("document_ids: ", document_ids)
    urls = []

    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            document_id = int(row[1])
            if document_id in document_ids:
                urls.append(row[0])

    return urls
