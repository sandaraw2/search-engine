
import json
import string
import ast
import csv
import indexer
from indexer import read_file
import os

'''
End goal of index partitioning will be a partitioned full index of each alphabet in disk
So it'll look like :
A-B {Ardvark:{D1: ([p1, p2, p3],tf), D2: ([p2, p3,...],tf), ...}, Asian: ...}
B-C [...]
C-D [...]
...
'''

total_batch_num = 0
output_files = {}


def main(directory_path):
    print("load_character_index A: ", load_character_index('A'))
    print("load_character_index number: ", load_character_index('number'))
    # Create output files for each letter
    # Specify the directory where you want to create CSV files
    output_directory = 'target'

    # # Iterate through each letter in the alphabet
    # for letter in string.ascii_uppercase:
    #     # Create a CSV file for the current letter
    #     csv_file_path = os.path.join(output_directory, f'{letter}.csv')
    #     output_files[letter] = csv_file_path
    #     # Create an empty CSV file
    #     with open(csv_file_path, 'w', newline=''):
    #         fieldnames = ['word', 'data']
    #         writer = csv.DictWriter(csv_file_path, fieldnames=fieldnames)

    #         writer.writeheader()

    #         # write data
    #         # writer.writerow({'word': "", 'data': ""})

    #         pass

    # Create number csv file
    csv_file_path = os.path.join(output_directory, f'number.csv')
    # Create an empty CSV file
    with open(csv_file_path, 'w', newline=''):
        pass

    file_amount = 0
    for root, dirs, files in os.walk(directory_path):
        file_amount += len(files)

    print("file_amount: ",  file_amount)

    max_batch_size = file_amount

    print("max_batch_size: ", max_batch_size)

    current_batch = []
    num_of_files_in_batch = 0
    global total_batch_num
    for root, dirs, files in os.walk(directory_path):
        dirs.sort()  # this is needed to make sure the directory is access alphabetically
        for file_name in files:
            if file_name.endswith('.json'):
                file_path = os.path.join(root, file_name)
                data = read_file(file_path)
                current_batch.append(data)
    create_partial_index(current_batch)

    # batch_files if a list of file data

    # update batch values - move on to next set
    # begining_index = split_index


'''
After processing this step, we will be left with multiple partial indexes in disk for each batch of
documents processed 
'''

'''
Index structure:
{W1:{D1: ([pos1, pos2, pos3...],TF), D2: ([pos1, pos2...],TF), ...]), W2:{...}}}
'''


def create_partial_index(batch_files):
    index = {}

    for file in batch_files:
        # print("file: ", file['content'], " \n")
        # Skip further processing if read_file returns None
        if file is None or file['content']:
            continue
        words = indexer.get_text_list(file)
        if words != []:
            doc_id = indexer.get_id(file)
            words = indexer.clean_punctuation(words)
            words = indexer.clean_empty_strings(words)
            words = indexer.normalize_word(words)

        for word in words:
            # print("word: ", word)
            write_content_to_disk(word, "target/words.csv")
            pos_list = find_all_pos(words, word)
            if word not in index:
                # print("Index: ", index)
                index[word] = {
                    doc_id: (pos_list, calculate_tf(len(pos_list), len(words)))}
            else:
                # list_info = index[word]
                # index[word] = list_info.append(
                #     (doc_id, pos_list, calculate_tf(len(pos_list), len(words))))
                index[word][doc_id] = (
                    pos_list, calculate_tf(len(pos_list), len(words)))
    # sort index alphabetically
    index = dict(sorted(index.items()))
    # write to disk
    write_index_to_disk(index, "target/disk.csv")

#  DONE


def write_content_to_disk(content, file_path):
    with open(file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        # we need to turn content into a list
        if isinstance(content, str):
            content = [content]

        # Write the data to the CSV file
        csv_writer.writerow(content)


# index->dictionary. this function should write to the csv file
def write_index_to_disk(index, file_path):
    with open(file_path, 'a', newline='') as csvfile:
        fieldnames = ['word', 'data']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        # write data
        for word, values in index.items():
            writer.writerow(
                {'word': word, 'data': values})


def clear(file_path):
    with open(file_path, 'w') as file:
        file.write("")


def find_all_pos(words, word):
    # Finds all word positions in doc and returns list of positions
    pos_list = []
    for i in range(len(words)):
        if words[i] == word:
            pos_list.append(i)
    return pos_list


def calculate_tf(freq, total_terms):
    tf = freq / total_terms
    return tf


def merge_partial_index():
    # Load Index from disk
    # Read Index[term] place in corresponding [CHARACtER].csv file
    current_character = 'A'
    current_character_index = load_character_index(current_character)
    partial_index = load_partial_index()
    total_terms = len(partial_index)
    # Read input CSV and write to corresponding output file
    for word in partial_index:
        if word == "":
            continue
        first_character = word[0].upper()
        if first_character != current_character:
            # LOAD NEEDED CHARACTER FILE INDEX INTO CURRENT_CHARACTER_INDEX
            current_character_index = load_character_index(first_character)
            # UPDATE CURRENT_CHARACTER TO NEW CHARACTER (FIRST_CHARACTER)
            current_character = first_character

        if len(current_character_index) == 0 or word not in current_character_index:
            # create entry current_character_index
            current_character_index[word] = partial_index[word]
        else:
            # append word_dict of partial index to target_word_dict: word_dict --> target_word_dict
            word_dict = partial_index[word]
            target_word_dict = current_character_index[word]
            for doc_id, doc_data in word_dict.items():
                if doc_id in target_word_dict:
                    # update positons
                    positions = doc_data[0]
                    target_positions = target_word_dict[doc_id][0]
                    for position in positions:
                        target_positions.append(position)
                    # recalculate tf
                    new_tf = calculate_tf(len(target_positions), total_terms)
                    # replace tuple for doc_id
                    target_word_dict[doc_id] = (target_positions, new_tf)
                else:
                    # add doc_id into target_word_dict
                    positions = doc_data[0]
                    tf = doc_data[1]
                    target_word_dict[doc_id] = (positions, tf)

        # WRITE BACK TO CHARACTER CSV FILES
        if first_character.isalpha():
            write_index_to_disk(current_character_index,
                                f'{first_character}.csv')
        else:
            write_index_to_disk(current_character_index, f'number.csv')


def convert_string_to_dict(input_string):
    if len(input_string) == 0:
        return {}

    result_dict = {}
    lines = input_string.strip().split('\n')

    for line in lines:
        try:
            # Split each line into key and value at the first comma
            key, value = line.split(',', 1)
            key = key.strip('"')  # Remove surrounding quotes from the key
            # Evaluate the string representation of the dictionary
            value = ast.literal_eval(value.strip())
            result_dict[key] = value
        except (ValueError, SyntaxError) as e:
            print(f"Error processing line: {line}\nError: {e}")

    return result_dict


def load_character_index(current_letter):
    try:
        if current_letter.isalpha():
            with open('target/'+current_letter+'.csv', 'r') as csvfile:
                string_content = csvfile.read()
                # print("content:" + string_content)
                lines = string_content.split('\n')
                new_string = '\n'.join(lines[1:])
                character_index = convert_string_to_dict(new_string)
                # print("load character index: ", character_index)
                return character_index
        else:
            with open('target/number.csv', 'r') as csvfile:
                string_content = csvfile.read()
                # print("content:" + string_content)
                lines = string_content.split('\n')
                new_string = '\n'.join(lines[1:])
                character_index = convert_string_to_dict(new_string)
                return character_index
    except FileNotFoundError:
        print(f"File '{'target/'+current_letter+'.csv'}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def load_partial_index():
    try:
        with open('target/disk.csv', 'r') as csvfile:
            string_content = csvfile.read()
            # print("content:" + string_content)
            lines = string_content.split('\n')
            new_string = '\n'.join(lines[1:])
            character_index = convert_string_to_dict(new_string)

            return character_index
    except FileNotFoundError:
        print(f"File '{'target/disk.csv'}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    directory_path = 'DEV'
    main(directory_path)
