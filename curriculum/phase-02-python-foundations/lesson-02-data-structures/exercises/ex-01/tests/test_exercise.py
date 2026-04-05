"""Tests for Exercise 1 — Contact Book."""

import importlib.util
import os
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SOLUTION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "solution", "main.py"
)


def _load_module(path: str):
    """Import main.py as a module from the given path."""
    spec = importlib.util.spec_from_file_location("student_main", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mod():
    return _load_module(SOLUTION_PATH)


@pytest.fixture
def empty_contacts():
    return []


@pytest.fixture
def sample_contacts():
    return [
        {"name": "Ada", "email": "ada@example.com"},
        {"name": "Bob", "email": "bob@example.com"},
    ]


# ---------------------------------------------------------------------------
# Tests — add_contact
# ---------------------------------------------------------------------------

def test_add_contact_to_empty(mod, empty_contacts):
    """Adding a contact to an empty list should create one entry."""
    result = mod.add_contact(empty_contacts, "Ada", "ada@example.com")
    assert len(result) == 1
    assert result[0]["name"] == "Ada"
    assert result[0]["email"] == "ada@example.com"


def test_add_contact_to_existing(mod, sample_contacts):
    """Adding a contact should append to the existing list."""
    result = mod.add_contact(sample_contacts, "Cat", "cat@example.com")
    assert len(result) == 3
    assert result[-1]["name"] == "Cat"


# ---------------------------------------------------------------------------
# Tests — find_contact
# ---------------------------------------------------------------------------

def test_find_contact_exists(mod, sample_contacts):
    """Finding an existing contact should return the dict."""
    result = mod.find_contact(sample_contacts, "Ada")
    assert result is not None
    assert result["email"] == "ada@example.com"


def test_find_contact_case_insensitive(mod, sample_contacts):
    """Search should be case-insensitive."""
    result = mod.find_contact(sample_contacts, "ada")
    assert result is not None
    assert result["name"] == "Ada"


def test_find_contact_not_found(mod, sample_contacts):
    """Searching for a non-existent contact should return None."""
    result = mod.find_contact(sample_contacts, "Zoe")
    assert result is None


# ---------------------------------------------------------------------------
# Tests — list_contacts
# ---------------------------------------------------------------------------

def test_list_contacts_formatted(mod, sample_contacts):
    """Should return formatted strings."""
    result = mod.list_contacts(sample_contacts)
    assert result == ["Ada <ada@example.com>", "Bob <bob@example.com>"]


def test_list_contacts_empty(mod, empty_contacts):
    """Empty contact list should return empty list."""
    result = mod.list_contacts(empty_contacts)
    assert result == []


# ---------------------------------------------------------------------------
# Tests — remove_contact
# ---------------------------------------------------------------------------

def test_remove_contact_exists(mod, sample_contacts):
    """Removing an existing contact should return True and shrink the list."""
    result = mod.remove_contact(sample_contacts, "Bob")
    assert result is True
    assert len(sample_contacts) == 1


def test_remove_contact_case_insensitive(mod):
    """Removal should be case-insensitive."""
    contacts = [{"name": "Ada", "email": "ada@example.com"}]
    result = mod.remove_contact(contacts, "ada")
    assert result is True
    assert len(contacts) == 0


def test_remove_contact_not_found(mod, sample_contacts):
    """Removing a non-existent contact should return False."""
    result = mod.remove_contact(sample_contacts, "Zoe")
    assert result is False
    assert len(sample_contacts) == 2
