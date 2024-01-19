import os
import json
import nltk
import csv
import ast
from nltk.corpus import stopwords, LazyCorpusLoader
from nltk.stem import PorterStemmer
import string
from bs4 import BeautifulSoup
from urllib.parse import urldefrag


# nltk.download('punkt')
# nltk.download('stopwords')

directory_path = 'DEV'
# initialize the URL and ID mapping dictionary
url_id_mapping = {}
url_id_file = 'url_id.csv'

# load existing data from the CSV file if it exists
if os.path.exists(url_id_file):
    with open(url_id_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        url_id_mapping = {row[0]: int(row[1]) for row in reader}


# def main(directory_path):
#     try:
#         # try to open the CSV file for reading
#         with open("report.csv", 'r') as reportcsv:
#             # read existing data from the CSV file
#             existing_data = dict(csv.reader(reportcsv))
#     except FileNotFoundError:
#         # if the file doesn't exist, create an empty dictionary
#         existing_data = {}
#
#     # file_count = 0
#     for root, dirs, files in os.walk(directory_path):
#         dirs.sort()  # this is needed to make sure the directory is access alphabetically
#         for file_name in files:
#             if file_name.endswith('.json'):
#                 file_path = os.path.join(root, file_name)
#                 data = read_file(file_path)
#
#                 # Skip further processing if read_file returns None
#                 if data is None:
#                     continue
#
#                 # Clean the words!
#                 words = get_text_list(data)
#                 if words != []:
#                     id = get_id(data)
#                     # words = stop_words(words)
#                     words = clean_punctuation(words)
#                     words = normalize_word(words)
#                     # words = stemming(words)
#                     index(words, id, existing_data)
#
#                 # file_count += 1
#                 # if file_count >= max_files:
#                 # return


def read_all_files(directory_path, max_files):
    file_count = 0
    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            if file_name.endswith('.json'):
                file_path = os.path.join(root, file_name)
                data = read_file(file_path)
                # Do something with the data (e.g., print it)
                print(data)

                file_count += 1
                if file_count >= max_files:
                    return


# open and read files
# will return data and we can use  read_file()['content']
def read_file(file_path):
    # testing opening one file
    with open(file_path, 'r') as file:
        # loads
        data = json.load(file)
    # check if 'url' ends with '.txt', if so, skip this file since there is no valid html document and just plain text
    if 'url' in data and data['url'].lower().endswith('.txt'):
        """
        print(f"Skipping file with URL ending in '.txt': {data['url']}")
        UNCOMMENT THIS
        """
        return None

    return data

# parse text from html
# will return list of raw parsed words


def get_text_list(data):
    # verify if 'content' key exists in data
    if 'content' not in data:
        print("Error: 'content' key is missing in the provided data.")
        return []

    # get content from file if 'content' is a file path
    if os.path.isfile(data['content']):
        with open(data['content'], 'r') as file:
            content = file.read()
    else:
        url = data['url']
        content = data['content']

    # cerify if 'content' is a valid HTML or XML markup
    # check if 'content' appears to be HTML markup
    if content.lstrip().startswith("<"):
        try:
            # handles parsing html
            soup = BeautifulSoup(data['content'], 'html.parser')
        except Exception as e:
            # print(f"Error: Failed to parse content as HTML. {e}")
            return []
    else:
        return []

    # verify if 'content' is a string
    if not isinstance(data['content'], str):
        return []

    # gets text for specified tags
    words_list = get_text_tags(soup)

    # check if the content has less than 100 words
    if len(words_list) < 10:
        return []
    return words_list

def get_text_tags(soup):
    text = []
    tagsList = ["b", "strong", "h1", "h2", "h3", "h4", "h5", "h6", "head", "title", "big", "i"]
    for tag in tagsList:
        for content in soup.find_all(tag):
            text.extend(nltk.word_tokenize(content.get_text()))
    return text

def get_id(file_path, data):
    url = data['url']

    # remove fragments from the URL
    url, fragment = urldefrag(url)

    if url in url_id_mapping:
        return url_id_mapping[url]
    else:
        # Assign a new doc_id
        new_doc_id = len(url_id_mapping) + 1
        url_id_mapping[url] = new_doc_id

        # Update the CSV file
        with open(url_id_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([url, new_doc_id])

        return new_doc_id


def normalize_word(words):
    # Convert to lowercase
    normalized_words = [word.lower() for word in words]

    # Remove punctuation
    normalized_words = [word.translate(str.maketrans(
        '', '', string.punctuation)) for word in normalized_words]

    return normalized_words


# stemming - Stemming: use stemming for better textual matches. Suggestion: Porter stemming, but it is up to you to choose.
# for every word given in words, find similar words, add to word list, and return
def stemming(words):
    # stemmer = PorterStemmer()
    # stemmed_words = [stemmer.stem(word) for word in words]
    # for word in stemmed_words:
    #     # may be slowing because we are adding all stemed words
    #     words.append(word)
    # return words
    stemmer = PorterStemmer()
    return {stemmer.stem(word) for word in words}


def clean_punctuation(words):
    return [word for word in words if word not in string.punctuation]


def clean_empty_strings(words):
    return [word for word in words if word != ""]


def index(wordlist, currentDocId, existing_data):
    # write the updated data to the CSV file
    with open("report.csv", 'w', newline='') as reportcsv:
        csv_writer = csv.writer(reportcsv)
        # iterate through the wordlist
        for word in wordlist:
            # check if the word is already a key in the CSV data
            if word in existing_data:
                # word found, add currentDocId to its set
                if type(existing_data[word]) == str:
                    existing_data[word] = ast.literal_eval(
                        existing_data[word])

                    existing_data[word][0] += 1
                    existing_data[word][1].add(currentDocId)
                else:
                    existing_data[word][0] += 1
                    existing_data[word][1].add(currentDocId)
            else:
                # word not found, create a new key-value pair with a set
                # [Frequency count, {Document IDs}]
                existing_data[word] = [1, {currentDocId}]

        csv_writer.writerows(existing_data.items())

#
# if __name__ == "__main__":
#     main(directory_path)
#
# main('/DEV')
