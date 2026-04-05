"""
Exercise: Variables, Types & Functions
=======================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py
"""


# TODO 1: Write a function called `celsius_to_fahrenheit` that:
#          - Takes one parameter `celsius` (float)
#          - Returns the temperature converted to Fahrenheit
#          - Formula: F = C * 9/5 + 32
#          - Add a type hint for the parameter and return value


# TODO 2: Write a function called `is_palindrome` that:
#          - Takes one parameter `text` (str)
#          - Returns True if the text reads the same forwards and backwards
#          - Should be case-insensitive (e.g., "Racecar" is a palindrome)
#          - Should ignore spaces (e.g., "taco cat" is a palindrome)
#          - Hint: use .lower() and .replace(" ", "")


# TODO 3: Write a function called `calculate_bmi` that:
#          - Takes two parameters: `weight_kg` (float) and `height_m` (float)
#          - Returns the BMI rounded to 1 decimal place
#          - Formula: BMI = weight_kg / (height_m ** 2)
#          - Use the built-in round() function


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"0°C = {celsius_to_fahrenheit(0)}°F")
    print(f"100°C = {celsius_to_fahrenheit(100)}°F")
    print(f"Is 'racecar' a palindrome? {is_palindrome('racecar')}")
    print(f"Is 'hello' a palindrome? {is_palindrome('hello')}")
    print(f"BMI for 70kg, 1.75m: {calculate_bmi(70, 1.75)}")
