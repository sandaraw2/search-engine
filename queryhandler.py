

import helper

'''
Query function:
 1. Tokenizes query string
 3. For each word in tokenized_query_string 
    a. load relevant word_dict
    b. append word_dict into temp_dictionary {word: word_dict}
 4. Sort temp_dict by word_dict length (most restictive term to least)
 5. Perform conjunction (AND) on the doc_ids of word_dicts
 6. Calculate relevancy of remaining doc_ids that satisfy constraints 
    a. calculate tf-idf 
    b. calculate positional score 
    c. cosine similarity
 7. Returns the pages with highest relevancy score
'''


# def query(query_string):
#     # Tokenize query_string
#     temp_dict = {}
#     tokenized_query_string = query_string.split()
#     for token in tokenized_query_string:
#         # Load relevant information from alphabet index
#         first_char = token[0].upper()
#         character_index = load_character_index(first_char)
#         temp_dict[token] = character_index[token]
#     # Sort by length of postings list
#     temp_dict = dict(sorted(temp_dict.items(), key=lambda item: len(item[1])))
#     # Perform ANDing

common_document_ids_from_handler = set()

index_cache = {}
helper.preload_indexes(index_cache)


def query(index_cache, query_string):
    global common_document_ids_from_handler

    # Tokenize query_string
    temp_dict = {}
    tokenized_query_string = query_string.split()
    print("tokenized: ", tokenized_query_string)
    for token in tokenized_query_string:
        # Load relevant information from alphabet index
        first_char = token[0].upper()
        # check cache for necessary alphabet index
        if first_char.isalpha() and first_char in index_cache:
            character_index = index_cache[first_char]
        elif (not first_char.isalpha()) and "number" in index_cache:
            character_index = index_cache["number"]
        else:
            character_index = helper.load_character_index(first_char)
            helper.update_index_cache(index_cache, character_index)
        temp_dict[token] = character_index[token]
    # Sort by length of postings list
    temp_dict = dict(sorted(temp_dict.items(), key=lambda item: len(item[1])))

    # Perform ANDing
    # master of software engineering <- master AND of, of AND software, software AND engineering
    # master of software AND engineering

    # this gives us the common document ID
    # conjunction_doc_ids = set()
    conjunction_doc_ids = []
    positions_list = []
    filtered_set = set()

    for i in range(len(tokenized_query_string)):
        # take tokenized_query_string[i] as key in tempt_dict
        # compare the i and i+1 tempt_dict values and see if they have the same docId (which is the keys)
        # grabs the intersection between two tokens docID
        if (i == 0):
            filtered_set.update(
                set(temp_dict[tokenized_query_string[i]].keys()))
        else:
            filtered_set = filtered_set & set(  # returns {2567, 2452, 2453}
                temp_dict[tokenized_query_string[i]].keys())

    common_doc = filtered_set
    common_document_ids_from_handler = common_doc
    # common_document_ids_from_handler.update(common_doc)
    print("common docs: ", common_doc)

    for doc in common_doc:  # doc is an docID
        for i in range(len(tokenized_query_string)):
            # {aiken: {2560: ([154], 0.0027472527472527475)}}
            # print("doc: ", doc)
            try:
                positions_list.append(
                    temp_dict[tokenized_query_string[i]][doc][0])
                # print("positions_list: ", positions_list)
            except KeyError:
                # doc id didn't exist for this word
                continue
        # must stay outside to not append more than once per doc
        doc_entry = {doc: positions_list}
        conjunction_doc_ids.append(doc_entry)

    # be used to compare words that are close together
    # conjunction_doc_ids: [{2558:[[915],[586]]}, {2569:[[0, 6, 7, 9], [1]}]

    print("conjunc: ", conjunction_doc_ids)

    return conjunction_doc_ids


# optionally to run calculate position difference to get higher match - run this
def run_calculate_pos_diff(docs_id):
    calculate_pos_diff(docs_id)

# function to find the pair of positions with the smallest absolute difference


def find_min_difference(first_positions, second_positions):
    min_diff = float('inf')
    for first_pos in first_positions:
        for second_pos in second_positions:
            diff = abs(first_pos - second_pos)
            if diff < min_diff:
                min_diff = diff
    return min_diff


# dictionary to store minimum differences for each docID
min_diffs = {}


def calculate_pos_diff(list_of_common_docs):
    # calculate minimum difference for each document
    for document in list_of_common_docs:
        doc_id = list(document.keys())[0]  # returns dict_keys([2558])
        # [{2558: [[915], [586]]}] - [915]
        first_positions = document[doc_id][0]
        # [{2558: [[915], [586]]}] - [586]
        second_positions = document[doc_id][1]
        min_diff = find_min_difference(first_positions, second_positions)
        min_diffs[doc_id] = min_diff

    # find the docID with the smallest minimum difference
    min_min_diff_docID = min(min_diffs, key=min_diffs.get)

    # print the results
    for doc_id, min_diff in min_diffs.items():
        print(f"DocID: {doc_id}, Minimum Difference: {min_diff}")

    print("\nDocID with the smallest minimum difference:", min_min_diff_docID)
    print("Minimum Difference:", min_diffs[min_min_diff_docID])

    return min_diffs[min_min_diff_docID]
