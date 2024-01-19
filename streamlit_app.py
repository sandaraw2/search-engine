from query import retrieve_urls, search_csv_for_tokens, stem_query
import nltk
from queryhandler import query, calculate_pos_diff
import streamlit as st
import time
import timeit
import helper

search_query = ""
results = ""
# csv_file_path = "report.csv"
url_csv_file_path = "url_id.csv"


def main():
    index_cache = {}
    helper.preload_indexes(index_cache)

    st.title("IR23F-A3-G8 Search Engine:")

    # text input field
    search_query = st.text_input("Enter text here:")
    search_query = search_query.lower()

    # button
    button_clicked = st.button("Search")

    # check if the button is clicked

    if button_clicked:
        # search_query = user_input.split()
        # print the entered text below the input field
        st.write("Searching for: ", search_query)
        generate_results(index_cache, search_query)


def generate_results(index_cache, search_query):
    print("generating...")
    print("search query: ", search_query)
    start_time = time.time()
    results_of_query = query(index_cache, search_query)
    # print(results_of_query)

    common_document_ids = []

    # incorporating 2-gram
    # try:
    #     add_top = pick_two_gram(results_of_query)
    #     common_document_ids.append(add_top)
    # except ValueError:
    #     print("Caught ValueError")
    #     pass

    for dictionary in results_of_query:
        common_document_ids.append(list(dictionary.keys())[0])
    print("common_document_ids: ", common_document_ids)
    matching_urls = retrieve_urls(url_csv_file_path, common_document_ids)
    end_time = time.time()
    elapsed_time_secs = round(end_time - start_time, 2)
    print("matching urls: ", matching_urls)
    st.write(f"Elapsed Time: {elapsed_time_secs} seconds")
    st.write("Search Results: ")
    st.markdown("\n".join([f"- {url}" for url in matching_urls]))


def pick_two_gram(position_list):
    top_rank = calculate_pos_diff(position_list)
    # will return the docId with minimum differences (may need to not limit to 1)
    return top_rank


# def generate_results(search_query):
#     print("generating...")
#     print("search query: ", search_query)
#     # run the boolean query retrieval
#     # stemmed_query = stem_query(search_query)
#     # print("from: ", stemmed_query)
#     common_document_ids = search_csv_for_tokens(csv_file_path, search_query)
#     print("common ids: ", common_document_ids)
#     matching_urls = retrieve_urls(url_csv_file_path, common_document_ids)
#     print("matching urls: ", matching_urls)
#     st.write("Search Results: ")

#     st.markdown("\n".join([f"- {url}" for url in matching_urls]))


if __name__ == "__main__":
    main()
