
import pickle
from typing import Dict, List

# Function to load face encodings from a file (if they exist)
def loadEncodings(filePath: str) -> Dict[str, List]:
    try:
        with open(filePath, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        print(f"Encodings file not found. Creating a new one at {filePath}.")
        return {}
    except Exception as e:
        print(f"An error occurred while loading encodings: {e}")
        return {}

# Function to save face encodings to a file
def saveEncodings(filePath: str, encodings: Dict[str, List]):
    try:
        with open(filePath, 'wb') as file:
            pickle.dump(encodings, file)
    except Exception as e:
        print(f"An error occurred while saving encodings: {e}")