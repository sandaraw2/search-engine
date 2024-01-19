
import os
from indexer import read_file
import indexer
import csv
import string
import psutil
import helper
'''
End goal of index partitioning will be a partitioned full index of each alphabet in disk
This is kind of like having a B-tree
So it'll look like :
A-B {Ardvark:{D1: ([p1, p2, p3],tf), D2: ([p2, p3,...],tf), ...}, Asian: ...}
B-C [...]
C-D [...]
...
'''

'''
Main function: 
    1. Generate an index file for each letter of the alphabet
    2. Generate an index file for numbers
    3. Create file batches and pass to indexing
        Every time a batch is created:
        a. A partial index is created using the current batch
        b. The partial index is then merged into alphabet index

'''

# total_batch_num = 0
output_files = {}

memory = psutil.virtual_memory()
initial_available = memory.available

skipped_count = 0
not_skipped_count = 0


def main(directory_path):
    # 1: -------------------------------------------------
    # Specify the directory where you want to create CSV files
    output_directory = 'target'

    # Iterate through each letter in the alphabet
    for letter in string.ascii_uppercase:
        # Create a CSV file for the current letter
        csv_file_path = os.path.join(output_directory, f'{letter}.csv')
        output_files[letter] = csv_file_path
        # Create an empty CSV file
        with open(csv_file_path, 'w', newline='') as csv_file:
            fieldnames = ['word', 'data']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            # writer.writeheader()

    # 2: ----------------------------------------------------------
    # Create number csv file
    csv_file_path = os.path.join(output_directory, f'number.csv')
    # Create an empty CSV file
    with open(csv_file_path, 'w', newline=''):
        pass

    # 3: ----------------------------------------------------------
    # Keep count of total number of files in corpus through iteration
    file_amount = 0
    for root, dirs, files in os.walk(directory_path):
        file_amount += len(files)
    print("file_amount: ", file_amount)

    max_batch_size = file_amount//100
    # keep track of batch and batch size
    current_batch_size = 0
    current_batch = {}  # current_batch is a list file data
    # keep track of which file we are processing
    current_file_num = 0
    for root, dirs, files in os.walk(directory_path):
        dirs.sort()  # this is needed to make sure the directory is access alphabetically
        # print("We are in directory: ", dirs)
        for file_name in files:
            file_path = os.path.join(root, file_name)
            print(f"Scanning file: {file_path}")
            current_file_num += 1
            # add file into current_batch
            current_batch_size += 1
            # only add .json files
            if file_name.endswith('.json'):
                file_path = os.path.join(root, file_name)
                # data contains dictionary with ...
                data = read_file(file_path)
                # adds whole dictionary from json file into current_batch
                current_batch[file_path] = data

            # If current_batch_size > max_batch_size or there are no more files left
            if (current_batch_size > max_batch_size) or current_file_num == file_amount:
                print("batch created")
                print(f'batch_size: {current_batch_size}')
                create_partial_index(current_batch)
                merge_partial_index()
                # reset current_batch_size back to 0
                current_batch_size = 0
                # clear batch
                current_batch = {}


'''
Create_partial_index function:
Index structure:
{W1:{D1: ([pos1, pos2, pos3...],TF), D2: ([pos1, pos2...],TF), ...]), W2:{...}}}

1. If file has content
    a. Get clean words list from file content
    b. For word in words:
        a. If word not in index 
        b. else (word exists in index)
2. else (file has no content)

'''


def create_partial_index(batch_files):
    global skipped_count
    global not_skipped_count

    current_batch_index = {}
    for file_path, data in batch_files.items():
        # Skip further processing if read_file returns None
        if data is None or data['content'] is None:
            skipped_count += 1
            print("skipped")
            continue
        else:
            not_skipped_count += 1
        # get words list from file data
        words = indexer.get_text_list(data)
        if len(words) != 0:
            # clean words
            doc_id = indexer.get_id(file_path, data)
            words = indexer.clean_punctuation(words)
            words = indexer.clean_empty_strings(words)
            words = indexer.normalize_word(words)
            print(f'processing file: {doc_id}\n')

            for word in words:
                # Write word to word.csv file
                helper.write_content_to_disk(word, "target/words.csv")
                # Find all positions of word in words list
                pos_list = helper.find_all_pos(word, words)

                if word not in current_batch_index:
                    # print("Index: ", index)
                    current_batch_index[word] = {
                        doc_id: (pos_list, helper.calculate_tf(len(pos_list), len(words)))}
                else:
                    # NOTE: We only need to do to create a posting for each word per file ONCE
                    # Therefore, if the doc_id already exists for that word,
                    # We do not need to create another posting for that doc_id
                    if doc_id not in current_batch_index[word]:
                        current_batch_index[word][doc_id] = (
                            pos_list, helper.calculate_tf(len(pos_list), len(words)))

    # sort index alphabetically to make merging easier
    index = dict(sorted(current_batch_index.items()))
    # write current_batch_index to disk
    helper.write_index_to_disk(index, "target/disk.csv")
    # clear current_batch_index
    del current_batch_index


'''
merge_partial_index function:
1. Load necessary alphabet index
2. Iterate through partial index
3. Update alphabet index 
    a. If word exists in alphabet index 
        a. If doc_id exists in term posting
        b. else (doc_id does not exist in term posting) 
    b. else (word does not exist in alphabet index)
4. Write alphabet index back to csv file 
'''


# This function merges current partial index to the alphabet partial indexes
def merge_partial_index():
    # Load Index from disk
    # Read Index[term] place in corresponding [CHARACtER].csv file
    # current_character = 'A'
    # current_character_index = load_character_index(current_character)
    # print(f"Loading character index for: {current_character}")

    # try:
    #     current_character_index = helper.load_character_index(
    #         current_character)
    # except Exception as e:
    #     print(f"Error loading character index: {e}")
    #     return
    #
    # if not isinstance(current_character_index, dict):
    #     print(f"Loaded character index is invalid: {current_character_index}")
    #     return

    partial_index = helper.load_partial_index()
    total_terms = len(partial_index)

    first_word_of_partial_index = True
    # Read input CSV and write to corresponding output file
    for word in partial_index:
        if first_word_of_partial_index:
            current_character = word[0].upper()
            first_word_of_partial_index = False
            current_character_index = helper.load_character_index(
                current_character)

        print(f'{word}')
        if word == "" or current_character_index is None:
            continue
        else:
            first_character = word[0].upper()
            if first_character != current_character:
                # WRITE BACK TO CHARACTER CSV FILES
                # write to previous character
                if current_character.isalpha():
                    helper.write_index_to_disk(current_character_index,
                                               f'target/{current_character}.csv')
                else:
                    helper.write_index_to_disk(current_character_index,
                                               f'target/number.csv')

                # LOAD NEEDED CHARACTER FILE INDEX INTO CURRENT_CHARACTER_INDEX
                current_character_index = helper.load_character_index(
                    first_character)
                # UPDATE CURRENT_CHARACTER TO NEW CHARACTER (FIRST_CHARACTER)
                current_character = first_character

            if len(current_character_index) == 0 or word not in current_character_index:
                # create entry current_character_index
                current_character_index[word] = partial_index[word]
            else:
                # word_dict = {doc_id: (...), doc_id:(...)}
                # append word_dict of partial index to target_word_dict: word_dict --> target_word_dict
                word_dict = partial_index[word]
                # print("word_dict is: ", word_dict)
                target_word_dict = current_character_index[word]
                for doc_id, doc_data in word_dict.items():
                    if doc_id in target_word_dict:
                        # update positons
                        positions = doc_data[0]
                        target_positions = target_word_dict[doc_id][0]
                        for position in positions:
                            target_positions.append(position)
                        # recalculate tf
                        new_tf = helper.calculate_tf(
                            len(target_positions), total_terms)
                        # replace tuple for doc_id
                        target_word_dict[doc_id] = (target_positions, new_tf)
                    else:
                        # add doc_id into target_word_dict
                        positions = doc_data[0]
                        tf = doc_data[1]
                        target_word_dict[doc_id] = (positions, tf)

            # # WRITE BACK TO CHARACTER CSV FILES
            # if first_character.isalpha():
            #     helper.write_index_to_disk(current_character_index,
            #                         f'target/{first_character}.csv')
            # else:
            #     helper.write_index_to_disk(current_character_index,
            #                         f'target/number.csv')


'''
After running merge_index() it should result in full indexes for EACH letter in the alphabet
This will make things easier when we query and search because we simply load the index 
corresponding to the letter of the query terms.
'''

'''
Preloading : 
For the sake of speed, we will preload a portion of alphabet indexes into a cache to reduce some
I/O read during querying. This will be implemented as a priority queue where it will be 
ordered by least to most used. If the required index is not in the index_cache, then we will read 
the index from disk and replace it into cache. 
'''

'''
Query function:
 1. Tokenizes query string
 3. For each word in tokenized_query_string 
    a. load relevant word_dict
        1. update index_cache (if necessary)
    b. append word_dict into temp_dictionary {word: word_dict}
 4. Sort temp_dict by word_dict length (most restrictive term to least)
 5. Perform conjunction (AND) on the doc_ids of word_dicts
 6. Calculate relevancy of remaining doc_ids that satisfy constraints 
    a. calculate tf-idf 
    b. calculate positional score 
    c. cosine similarity
 7. Returns the pages with highest relevancy score
'''

if __name__ == "__main__":
    directory_path = 'DEV/'
    # directory_path = 'DEV'
    main(directory_path)
    print("Files Not Skipped:", not_skipped_count)
    print("Files Skipped:", skipped_count)
