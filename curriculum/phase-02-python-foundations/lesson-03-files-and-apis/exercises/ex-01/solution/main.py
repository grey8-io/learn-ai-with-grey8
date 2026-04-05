"""
Exercise: Fetch and Save JSON — Solution
==========================================
"""
import json
import httpx


def fetch_and_save(url: str, filepath: str) -> dict:
    """Fetch JSON data from a URL and save it to a file.

    Args:
        url: The URL to fetch JSON from.
        filepath: The local file path to save the JSON data.

    Returns:
        The parsed JSON data as a dictionary.
    """
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    return data


def load_json(filepath: str) -> dict | None:
    """Load JSON data from a file.

    Args:
        filepath: The path to the JSON file.

    Returns:
        The parsed JSON data, or None if the file doesn't exist.
    """
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


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
