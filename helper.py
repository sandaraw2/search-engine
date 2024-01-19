import csv
import ast
import string
import psutil
import math

'''
    HELPER FUNCTIONS ===============================================================================
    - preload_indexes(index_cache)
    - update_index_cache(index_cache, replacement_index)
    - convert_string_to_dict(input_string)
    - load_character_index(letter)
    - load_partial_index()
    - write_content_to_disk(content , file_path)
    - write_index_to_disk(index, file_path)
    - clear()
    - find_all_pos(word, words)
    - calculate_tf(freq, total_terms)
    ...
'''

# index_cache = {'a' : {a_index}, 'b' : {b_index}, 'number' : {number_index}, ...}


def preload_indexes(index_cache):
    for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
        index_cache[letter] = load_character_index(letter)
    index_cache["number"] = load_character_index(0)
    return index_cache


def update_index_cache(index_cache, replacement_index):
    # replace the least used index with replacement_index
    index_cache[0] = replacement_index


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
            value = ast.literal_eval(value)
            result_dict[key] = value
        except (ValueError, SyntaxError) as e:
            print(f"Error processing line: {line}\nError: {e}")

    return result_dict


def load_character_index(current_letter):
    try:
        if current_letter.isalpha():
            with open('target/' + current_letter + '.csv', 'r') as csvfile:
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
        print(f"File '{'target/' + current_letter + '.csv'}' not found.")
        return {}
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

# This function writes specified string to csv files


def write_content_to_disk(content, file_path):
    with open(file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        # If content is a string then we need to turn content into a list
        if isinstance(content, str):
            content = [content]

        # Write the data to the CSV file
        csv_writer.writerow(content)


# This function writes a index(dictionary) to csv file
def write_index_to_disk(index, file_path):
    clear_file(file_path)
    with open(file_path, 'a', newline='') as csvfile:
        fieldnames = ['word', 'data']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # write data
        for word, values in index.items():
            writer.writerow(
                {'word': word, 'data': values})


def clear_all_files():
    for letter in string.ascii_uppercase:
        clear_file(f'target/{letter}.csv')

    clear_file("target/number.csv")


def clear_file(file_path):
    with open(file_path, 'w') as file:
        file.write("")

# This function finds all word positions in doc and returns list of positions


def find_all_pos(word, words):
    pos_list = []
    for i in range(len(words)):
        if words[i] == word:
            pos_list.append(i)
    return pos_list


def calculate_tf(freq, total_terms):
    tf = freq / total_terms
    return tf

def calculate_idf(num_docs_with_term, all_documents):
    total_docs = len(all_documents)
    idf = math.log(total_docs / (1 + num_docs_with_term))
    return idf

def calculate_tf_idf(tf,num_docs_with_terms):
    idf = calculate_idf(num_docs_with_terms, num_docs_with_terms)
    tf_idf = tf * idf
    return tf_idf



# get_smallest_set(info)
# Boolean method()

# For page in relevant_pages:
# number_of_relavant_docs = len(term_info)
# doc_id = doc_info[0]
# positions = doc_info[1]
# tf= doc_info[2]
# scores[doc_id] = calculate_scores(positions, tf, number_of_relevant_docs)
# return max of scores

# Sort(terms, indexes):
# Sort terms by shortest doc list first longest last


# def calculate_scores(pos, tf, num_docs_with_term):
# position_score = position_score(positions);
# tf_idf = calculate_tf_idf(tf, num_docs_with_term);


# def calculate_tf(freq, total_terms):
#     tf = freq / total_terms
#     return tf

