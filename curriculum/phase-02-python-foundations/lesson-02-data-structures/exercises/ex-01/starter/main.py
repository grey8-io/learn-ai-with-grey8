"""
Exercise: Contact Book
=======================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

The contact book is a list of dictionaries. Each contact dict has
two keys: "name" (str) and "email" (str).
"""


# TODO 1: Write a function called `add_contact` that:
#          - Takes three parameters: contacts (list), name (str), email (str)
#          - Appends a new dict {"name": name, "email": email} to the list
#          - Returns the updated contacts list


# TODO 2: Write a function called `find_contact` that:
#          - Takes two parameters: contacts (list), name (str)
#          - Searches the list for a contact with the matching name (case-insensitive)
#          - Returns the contact dict if found, or None if not found


# TODO 3: Write a function called `list_contacts` that:
#          - Takes one parameter: contacts (list)
#          - Returns a list of strings formatted as "Name <email>"
#          - Example: ["Ada <ada@example.com>", "Bob <bob@example.com>"]
#          - If contacts is empty, return an empty list


# TODO 4: Write a function called `remove_contact` that:
#          - Takes two parameters: contacts (list), name (str)
#          - Removes the contact with the matching name (case-insensitive)
#          - Returns True if a contact was removed, False if not found


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    book = []
    add_contact(book, "Ada", "ada@example.com")
    add_contact(book, "Bob", "bob@example.com")
    print("All contacts:", list_contacts(book))
    print("Find Ada:", find_contact(book, "Ada"))
    print("Remove Bob:", remove_contact(book, "Bob"))
    print("After removal:", list_contacts(book))
