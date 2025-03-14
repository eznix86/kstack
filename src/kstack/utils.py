from typing import List, Dict
import yaml


def load_stack(stack: str) -> dict:
    with open(stack, "r") as file:
        return yaml.safe_load(file)


def remove_none(data: dict) -> dict:
    """
    Recursively remove keys with `None` values in a dictionary.
    This works for nested dictionaries and lists.
    """
    # Create a new dictionary so we don't modify the original data in place
    if isinstance(data, dict):
        # Go through each item in the dictionary
        cleaned_data = {}
        for key, value in data.items():
            # Only add to the cleaned_data if the value is not None
            if value is not None:
                # If the value is a dictionary, clean it recursively
                if isinstance(value, dict):
                    cleaned_data[key] = remove_none(value)
                # If the value is a list, clean it recursively for dictionaries inside it
                elif isinstance(value, list):
                    cleaned_data[key] = [
                        remove_none(item) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    cleaned_data[key] = value
        return cleaned_data
    else:
        return data
