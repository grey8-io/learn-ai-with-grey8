"""
Exercise: Python Hello World with Functions — Solution
======================================================
"""

# TODO 1: Create a variable called `bootcamp_name` and set it to "Learn AI With Grey8"
bootcamp_name = "Learn AI With Grey8"

# TODO 2: Create a variable called `version` and set it to the integer 1
version = 1

# TODO 3: Create a variable called `welcome_message` using an f-string that says:
#          "Welcome to Learn AI With Grey8 v1!"
welcome_message = f"Welcome to {bootcamp_name} v{version}!"

# TODO 4: Write a function called `greet` that:
#          - Takes one parameter called `name`
#          - Returns the string "Hello, {name}! Let's build something amazing."
def greet(name):
    return f"Hello, {name}! Let's build something amazing."


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(welcome_message)
    print(greet("World"))
