# Variables, Types & Functions

Welcome to Phase 2! Now that your development environment is set up, it's time to learn the building blocks of Python. In this lesson, you'll master variables, data types, and functions — the foundation of everything you'll build from here on out.

Think of variables as labeled boxes that hold values, and functions as reusable machines that take inputs, do something useful, and give you outputs. Let's dive in.

---

## Variables and Assignment

In Python, creating a variable is as simple as choosing a name and assigning a value with `=`:

```python
name = "Ada"
age = 30
temperature = 98.6
is_student = True
```

No need to declare types up front — Python figures it out from the value you assign. This is called **dynamic typing**.

### Naming Conventions

Python has a few rules and conventions for variable names:

- Use `snake_case` (lowercase with underscores): `user_name`, `total_score`
- Names must start with a letter or underscore, not a number
- Avoid Python reserved words like `class`, `return`, `if`

Good variable names make your code read like a story. Compare `x = 36.5` with `body_temp_celsius = 36.5` — the second one tells you exactly what it represents.

---

## Data Types

Python has four fundamental types you'll use constantly:

| Type | Example | What It Holds |
|------|---------|---------------|
| `int` | `42` | Whole numbers |
| `float` | `3.14` | Decimal numbers |
| `str` | `"hello"` | Text (strings) |
| `bool` | `True` | True or False |

You can check a value's type with `type()`:

```python
print(type(42))        # <class 'int'>
print(type(3.14))      # <class 'float'>
print(type("hello"))   # <class 'str'>
print(type(True))      # <class 'bool'>
```

### Type Conversion

Sometimes you need to convert between types:

```python
age_str = "25"
age_num = int(age_str)    # Convert string to int
price = float("19.99")    # Convert string to float
label = str(42)            # Convert int to string
```

Be careful — `int("hello")` will crash your program because "hello" isn't a number. We'll learn to handle these errors later.

---

## Type Hints

Python lets you add **type hints** to document what types your code expects. They don't enforce anything at runtime, but they make your code much clearer and help editors catch mistakes:

```python
name: str = "Ada"
age: int = 30
gpa: float = 3.8
enrolled: bool = True
```

Think of type hints as helpful labels — they tell other developers (and your future self) what kind of data to expect.

---

## Functions

Functions are the workhorses of programming. They let you write a piece of logic once and reuse it as many times as you need.

### Defining a Function

```python
def greet(name: str) -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}!"
```

Here's the anatomy of that function definition:

```
  def greet(name: str) -> str:
  ─┬─ ──┬── ───┬────  ───┬───
   │    │      │         └── return type hint
   │    │      └── parameter with type hint
   │    └── function name
   └── keyword
```

Let's break this down:

- `def` — keyword that starts a function definition
- `greet` — the function's name
- `(name: str)` — a **parameter** with a type hint
- `-> str` — indicates the function returns a string
- `"""..."""` — a **docstring** that explains what the function does
- `return` — sends a value back to the caller

### Calling a Function

```python
message = greet("Ada")
print(message)  # Hello, Ada!
```

### Multiple Parameters

Functions can take as many parameters as you need:

```python
def calculate_area(width: float, height: float) -> float:
    """Calculate the area of a rectangle."""
    return width * height

area = calculate_area(5.0, 3.0)  # 15.0
```

### Default Arguments

You can give parameters default values so callers can skip them:

```python
def power(base: float, exponent: int = 2) -> float:
    """Raise base to the given exponent (default: squared)."""
    return base ** exponent

print(power(3))      # 9   (uses default exponent=2)
print(power(3, 3))   # 27  (overrides with exponent=3)
```

Default arguments must come after required ones. Think of them as sensible fallbacks.

---

## Docstrings

A **docstring** is a special string at the beginning of a function that documents what it does. It's enclosed in triple quotes and should describe the purpose, parameters, and return value:

```python
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit.

    Args:
        celsius: Temperature in degrees Celsius.

    Returns:
        Temperature in degrees Fahrenheit.
    """
    return celsius * 9 / 5 + 32
```

Docstrings are accessed with `help()`:

```python
help(celsius_to_fahrenheit)
```

Writing good docstrings is a habit that pays off enormously — especially when you come back to code after a few weeks.

---

## Putting It All Together

Here's a small example that combines everything from this lesson:

```python
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate Body Mass Index.

    Args:
        weight_kg: Weight in kilograms.
        height_m: Height in meters.

    Returns:
        BMI value rounded to one decimal place.
    """
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)

# Try it out
result = calculate_bmi(70, 1.75)
print(f"Your BMI is {result}")  # Your BMI is 22.9
```

---

## Your Turn

In the exercise that follows, you'll write three functions from scratch: a temperature converter, a palindrome checker, and a BMI calculator. Each one will test a different aspect of what you've learned — type conversion, string manipulation, and mathematical operations.

You've got all the tools you need. Let's write some Python!
