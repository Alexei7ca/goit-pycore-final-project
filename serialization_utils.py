import pickle
from typing import Tuple
from models import AddressBook, NoteBook

# filename for persistence
FILENAME = "assistant_data.pkl"

def save_data(book: AddressBook, notes: NoteBook):
    """Saves both AddressBook and NoteBook objects to a file using pickle."""
    try:
        data = (book, notes)
        with open(FILENAME, "wb") as f:
            pickle.dump(data, f)
        print("\nAll data successfully saved.")
    except Exception as e:
        print(f"\nError saving data: {e}")

def load_data() -> Tuple[AddressBook, NoteBook]:
    """
    Loads both AddressBook and NoteBook objects from a file.
    Returns new instances if the file is not found or corrupted.
    """
    try:
        with open(FILENAME, "rb") as f:
            book, notes = pickle.load(f)
        print(f"Data successfully loaded from {FILENAME}")
        return book, notes
    except FileNotFoundError:
        print(f"File {FILENAME} not found. Starting with empty AddressBook and NoteBook.")
        return AddressBook(), NoteBook()
    except Exception as e:
        print(f"Error loading data: {e}. Starting with empty AddressBook and NoteBook.")
        return AddressBook(), NoteBook()