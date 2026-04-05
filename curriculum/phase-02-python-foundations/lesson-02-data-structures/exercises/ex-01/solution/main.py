"""
Exercise: Contact Book — Solution
===================================
"""


def add_contact(contacts: list, name: str, email: str) -> list:
    """Add a new contact to the contact book.

    Args:
        contacts: The list of contact dictionaries.
        name: The contact's name.
        email: The contact's email address.

    Returns:
        The updated contacts list.
    """
    contacts.append({"name": name, "email": email})
    return contacts


def find_contact(contacts: list, name: str) -> dict | None:
    """Find a contact by name (case-insensitive).

    Args:
        contacts: The list of contact dictionaries.
        name: The name to search for.

    Returns:
        The contact dict if found, or None.
    """
    for contact in contacts:
        if contact["name"].lower() == name.lower():
            return contact
    return None


def list_contacts(contacts: list) -> list:
    """Format all contacts as a list of strings.

    Args:
        contacts: The list of contact dictionaries.

    Returns:
        A list of strings formatted as "Name <email>".
    """
    return [f'{c["name"]} <{c["email"]}>' for c in contacts]


def remove_contact(contacts: list, name: str) -> bool:
    """Remove a contact by name (case-insensitive).

    Args:
        contacts: The list of contact dictionaries.
        name: The name of the contact to remove.

    Returns:
        True if a contact was removed, False if not found.
    """
    for i, contact in enumerate(contacts):
        if contact["name"].lower() == name.lower():
            contacts.pop(i)
            return True
    return False


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
