# Data Structures

Now that you can create variables and functions, it's time to learn how to organize collections of data. Python gives you four powerful built-in data structures: **lists**, **dictionaries**, **tuples**, and **sets**. Each one has its strengths, and knowing when to use which is a key skill.

By the end of this lesson, you'll be able to store, search, and transform collections of data with confidence.

---

## Lists — Ordered Collections

A **list** is an ordered, changeable collection of items. Lists are the most commonly used data structure in Python.

```python
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
mixed = ["hello", 42, True, 3.14]
```

Lists use zero-based indexing, and you can also count backwards with negative indices:

```
  fruits = ["apple", "banana", "cherry", "date"]
  Index:      0        1         2         3
  Negative:  -4       -3        -2        -1
```

### Common List Operations

```python
fruits = ["apple", "banana", "cherry"]

# Access by index (starts at 0)
print(fruits[0])       # "apple"
print(fruits[-1])      # "cherry" (last item)

# Add items
fruits.append("date")          # Add to the end
fruits.insert(1, "avocado")   # Insert at position 1

# Remove items
fruits.remove("banana")       # Remove by value
last = fruits.pop()           # Remove and return the last item

# Check membership
print("apple" in fruits)      # True

# Length
print(len(fruits))            # Number of items
```

### List Comprehensions

List comprehensions are a concise way to create new lists by transforming or filtering existing ones. They're one of Python's most beloved features:

```python
# Traditional loop
squares = []
for x in range(5):
    squares.append(x ** 2)

# Same thing as a list comprehension
squares = [x ** 2 for x in range(5)]
# [0, 1, 4, 9, 16]

# With a filter
even_squares = [x ** 2 for x in range(10) if x % 2 == 0]
# [0, 4, 16, 36, 64]
```

Think of list comprehensions as a shorthand: `[expression for item in iterable if condition]`.

---

## Dictionaries — Key-Value Pairs

A **dictionary** (dict) maps unique keys to values. It's perfect for structured data where you look things up by name.

```python
person = {
    "name": "Ada",
    "age": 30,
    "city": "London"
}
```

### Common Dictionary Operations

```python
person = {"name": "Ada", "age": 30, "city": "London"}

# Access by key
print(person["name"])          # "Ada"
print(person.get("email"))     # None (no error if key missing)
print(person.get("email", "N/A"))  # "N/A" (with default)

# Add or update
person["email"] = "ada@example.com"
person["age"] = 31

# Remove
del person["city"]
email = person.pop("email")    # Remove and return

# Check if key exists
print("name" in person)        # True

# Iterate
for key, value in person.items():
    print(f"{key}: {value}")
```

### When to Use Dicts

Use dictionaries whenever you need to look up values by a meaningful name — user profiles, configuration settings, word counts, API responses. If you're reaching for a dict, you're probably on the right track.

---

## Tuples — Immutable Sequences

A **tuple** is like a list, but it cannot be changed after creation. This makes tuples useful for data that should stay constant.

```python
coordinates = (40.7128, -74.0060)
rgb_red = (255, 0, 0)

# Access by index (same as lists)
print(coordinates[0])  # 40.7128

# Unpack into variables
lat, lng = coordinates
print(f"Latitude: {lat}")
```

You can't modify tuples — no `append`, no `remove`, no reassignment. That's the point. When data shouldn't change, use a tuple.

---

## Sets — Unique Collections

A **set** is an unordered collection of unique items. Sets automatically remove duplicates and support mathematical set operations.

```python
colors = {"red", "green", "blue"}
numbers = {1, 2, 3, 2, 1}   # Becomes {1, 2, 3}

# Add and remove
colors.add("yellow")
colors.discard("red")

# Set operations
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a & b)    # Intersection: {3, 4}
print(a | b)    # Union: {1, 2, 3, 4, 5, 6}
print(a - b)    # Difference: {1, 2}
```

Use sets when you need to track unique items, remove duplicates, or perform membership checks quickly.

---

## Choosing the Right Structure

| Need | Use |
|------|-----|
| Ordered collection, may have duplicates | `list` |
| Look up values by a key | `dict` |
| Fixed data that shouldn't change | `tuple` |
| Unique items, fast membership checks | `set` |

Here's a quick reference to keep these straight:

```
  List [...]        Ordered, mutable, duplicates OK     → sequences
  Tuple (...)       Ordered, immutable, duplicates OK   → fixed data
  Dict {...: ...}   Key-value pairs, keys unique        → lookups
  Set {...}         Unordered, unique elements only     → membership
```

Here's a practical rule of thumb: start with a list. If you need key-based lookup, switch to a dict. If the data should never change, use a tuple. If you need uniqueness, use a set.

---

## Nested Structures

Real-world data often combines these structures. A common pattern is a list of dictionaries:

```python
contacts = [
    {"name": "Ada", "email": "ada@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Cat", "email": "cat@example.com"},
]

# Find a contact
for contact in contacts:
    if contact["name"] == "Bob":
        print(contact["email"])  # bob@example.com
```

This pattern shows up everywhere — API responses, database results, configuration files. Getting comfortable with nested structures will serve you well.

---

## Your Turn

In the exercise that follows, you'll build a contact book using lists and dictionaries. You'll implement functions to add, find, list, and remove contacts — a mini CRUD (Create, Read, Update, Delete) application. This is the kind of data manipulation you'll do constantly in AI projects.

Let's build it!
