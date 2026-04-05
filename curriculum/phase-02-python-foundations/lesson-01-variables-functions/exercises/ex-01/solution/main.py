"""
Exercise: Variables, Types & Functions — Solution
===================================================
"""


# TODO 1: Write a function called `celsius_to_fahrenheit`
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit.

    Args:
        celsius: Temperature in degrees Celsius.

    Returns:
        Temperature in degrees Fahrenheit.
    """
    return celsius * 9 / 5 + 32


# TODO 2: Write a function called `is_palindrome`
def is_palindrome(text: str) -> bool:
    """Check whether a string is a palindrome (case-insensitive, ignoring spaces).

    Args:
        text: The string to check.

    Returns:
        True if the text is a palindrome, False otherwise.
    """
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]


# TODO 3: Write a function called `calculate_bmi`
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


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"0°C = {celsius_to_fahrenheit(0)}°F")
    print(f"100°C = {celsius_to_fahrenheit(100)}°F")
    print(f"Is 'racecar' a palindrome? {is_palindrome('racecar')}")
    print(f"Is 'hello' a palindrome? {is_palindrome('hello')}")
    print(f"BMI for 70kg, 1.75m: {calculate_bmi(70, 1.75)}")
