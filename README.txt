

Project: Assignment 3: M3
Team: Sandra Wang, Jin Hyuk Myung, Vickie Do

How to Run Code that Builds the Index:
- Run batching.py to build the inverted index, create partial indexes and merge.
    - python3 batching.py

How to Start the Search Interface:
- Create a virtual environment, activate the virtual environment, and install dependencies.
    - python -m venv .venv
    - source .venv/bin/activate
    - pip install -r requirements.txt

- Launch the Streamlit App and the app will start in localhost.
    - streamlit run streamlit_app.py

How to Perform a Simple Query:
    - Enter a query string in the input text field.
    - Click the search button.
    - The search results will appear along with the elapsed time. 