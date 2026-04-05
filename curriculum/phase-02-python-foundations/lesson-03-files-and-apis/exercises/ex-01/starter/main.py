"""
Exercise: Fetch and Save JSON
===============================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py
"""
import json
import httpx


# TODO 1: Write a function called `fetch_and_save` that:
#          - Takes two parameters: url (str) and filepath (str)
#          - Uses httpx.get() to fetch JSON from the URL (set timeout=10)
#          - Calls response.raise_for_status() to check for HTTP errors
#          - Parses the JSON response with response.json()
#          - Saves the data to filepath using json.dump() with indent=2
#          - Returns the parsed data (a dict)


# TODO 2: Write a function called `load_json` that:
#          - Takes one parameter: filepath (str)
#          - Opens the file and parses its JSON content using json.load()
#          - Returns the parsed data (a dict)
#          - If the file doesn't exist, return None (catch FileNotFoundError)


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    url = "https://jsonplaceholder.typicode.com/todos/1"
    filepath = "todo.json"

    print("Fetching data...")
    data = fetch_and_save(url, filepath)
    print(f"Saved: {data}")

    print("Loading from file...")
    loaded = load_json(filepath)
    print(f"Loaded: {loaded}")
