from typing import Dict, List, Callable, Tuple
from models import (
    AddressBook, Record, InvalidPhoneFormatError, ContactNotFoundError, 
    PhoneNotFoundError, InvalidEmailFormatError, InvalidAddressFormatError
)
from serialization_utils import save_data, load_data

def input_error(func: Callable) -> Callable:
    """A decorator to handle common user input errors gracefully."""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, TypeError) as e:
            # Catch errors related to missing arguments or bad format
            if "not enough values to unpack" in str(e) or "Invalid format" in str(e) or "missing a required argument" in str(e):
                return "Invalid command format. Please provide necessary arguments."
            return f"Error with input data: {e}"
        except KeyError:
            return "Contact not found."
        except ContactNotFoundError as e:
            return str(e)
        except PhoneNotFoundError as e:
            return str(e)
        except (InvalidPhoneFormatError, InvalidEmailFormatError, InvalidAddressFormatError) as e:
            # Catch all specific validation errors from models.py
            return str(e)
        except Exception as e:
            # Catch any other unexpected errors
            return f"An unexpected error occurred: {e}"
    return inner

def parse_input(user_input: str) -> Tuple[str, List[str]]:
    """Parses the user input into a command and arguments."""
    parts = user_input.split()
    if not parts:
        return "", []

    cmd = parts[0].strip().lower()
    args = parts[1:]
    
    # Handle multi-word commands (e.g., "show all")
    if cmd == "show" and args and args[0].lower() == "all":
        return "all", []
        
    # Placeholder for birthday commands from Task 3
    if cmd == "add" and args and args[0].lower() == "birthday":
        return "add-birthday", args[1:]
    if cmd == "show" and args and args[0].lower() == "birthday":
        return "show-birthday", args[1:]
        
    return cmd, args

# --- CRUD commands will be added here ---

def hello_command() -> str:
    """Displays a welcome message and a command manual."""
    return """
Hello! Welcome to the Personal Assistant bot. Enter 'hello' to see commands.
"""

def main():
    book = load_data() # Loads AddressBook (using Task 5 placeholder)
    
    print("Welcome to the Personal Assistant bot! Enter 'hello' to see commands.")
    
    commands_map = {
        "hello": hello_command,
        # CRUD commands to be added in subsequent commits
    }

    while True:
        try:
            user_input = input("Enter a command: ").strip()
        except EOFError:
            print("\nGood bye!")
            save_data(book)
            break
            
        if not user_input:
            continue
            
        command, args = parse_input(user_input)
        
        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break
            
        handler = commands_map.get(command)
        
        if handler:
            # Call logic will be updated in the final commit
            if command == "hello":
                print(handler())
            else:
                print("Command not yet implemented.")
        else:
            print("Invalid command. Enter 'hello' to see available commands.")

if __name__ == "__main__":
    main()