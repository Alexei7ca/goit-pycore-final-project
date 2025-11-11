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

# --- CRUD commands ---

@input_error
def add_contact(args: List[str], book: AddressBook) -> str:
    """
    Adds a new contact with at least a name and a phone number.
    Format: add <name> <phone> [email] [address]
    """
    if len(args) < 2:
        raise ValueError("Invalid format. Command requires at least a name and phone number.")
        
    # Extract arguments: Name, Phone (required), Email, Address (optional)
    name, phone, *optional_fields = args

    record = book.find(name)
    message = f"Phone {phone} added to existing contact {name}."
    
    # If contact does not exist, create it and add the required phone
    if record is None:
        record = Record(name) 
        book.add_record(record)
        message = f"Contact {name} added."
        
    record.add_phone(phone) # Validation happens in Record/Phone class

    # Handle optional fields (Email and Address)
    if optional_fields:
        email = optional_fields[0]
        # Assumes Record has add_email method that handles validation
        record.add_email(email) 
        message += f" Email: {email} added."
        
    if len(optional_fields) > 1:
        address_parts = " ".join(optional_fields[1:])
        # Assumes Record has add_address method
        record.add_address(address_parts) 
        message += f" Address: {address_parts} added."
        
    return message

@input_error
def change_contact(args: List[str], book: AddressBook) -> str:
    """
    Changes an existing contact's old phone number to a new one.
    Format: change <name> <old_phone> <new_phone>
    """
    if len(args) < 3:
        raise ValueError("Invalid format. Command requires a name, old phone, and new phone.")
        
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    
    if record is None:
        raise ContactNotFoundError(f"Contact '{name}' not found.")
        
    # Validation for new_phone happens inside edit_phone (Task 1)
    record.edit_phone(old_phone, new_phone)
    
    return f"Phone number for '{name}' successfully changed from {old_phone} to {new_phone}."


@input_error
def show_phone(args: List[str], book: AddressBook) -> str:
    """
    Shows the full details for a specific contact.
    Format: phone <name>
    """
    if len(args) < 1:
        raise ValueError("Invalid format. Command requires a name.")
        
    name = args[0]
    record = book.find(name)
    
    if record is None:
        raise ContactNotFoundError(f"Contact '{name}' not found.")
        
    # Assumes Record.__str__ provides a detailed view of all fields
    return str(record)

def show_all(book: AddressBook) -> str:
    """
    Shows all contacts in the address book.
    """
    if not book.data:
        return "The address book is empty."
        
    result = "All contacts:\n"
    for record in book.data.values():
        result += f"{record}\n"
        
    return result.strip()

@input_error
def delete_contact(args: List[str], book: AddressBook) -> str:
    """
    Deletes a contact record from the address book.
    Format: delete <name>
    """
    if len(args) < 1:
        raise ValueError("Invalid format. Command requires a name.")
        
    name = args[0]
    book.delete(name)
    
    return f"Contact '{name}' deleted successfully."


def hello_command() -> str:
    """Displays a welcome message and a command manual."""
    manual = """
Hello! Welcome to the Personal Assistant bot. Here are the available commands:
| Command | Arguments                           | Example                       | Description                               |
| :------ | :---------------------------------- | :---------------------------- | :---------------------------------------- |
| hello   |                                     | hello                         | Displays this manual.                     |
| add     | <Name> <Phone> [Email] [Address...] | add John 1234567890 john@mail | Adds a new contact or phone (with optional email/address).|
| change  | <Name> <Old Phone> <New P>          | change John 123.. 098..       | Updates an existing contact's phone.      |
| phone   | <Name>                              | phone John                    | Shows a contact's full details.           |
| all     |                                     | all                           | Lists all saved contacts.                 |
| delete  | <Name>                              | delete John                   | Deletes a contact.                        |
| add-birthday | <Name> <DD.MM.YYYY>            | add-birthday John 01.01.1990  | Adds contact birthday (Task 3).           |
| show-birthday| <Name>                         | show-birthday John            | Shows contact birthday (Task 3).          |
| birthdays|                                    | birthdays                     | Shows upcoming birthdays (Task 3).        |
| close   |                                     | close                         | Exits the bot (data will be saved).       |
| exit    |                                     | exit                          | Exits the bot (data will be saved).       |
"""
    return manual

@input_error
def add_birthday(args: List[str], book: AddressBook) -> str:
    """Adds or updates a birthday for a contact. Format: add-birthday <Name> <DD.MM.YYYY>"""
    if len(args) < 2:
        raise ValueError("Invalid format. Command requires a name and a date (DD.MM.YYYY).")

    name, date_str = args[0], args[1]
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError(f"Contact '{name}' not found.")

    record.add_birthday(date_str)
    return f"Birthday for {name} set to {date_str}."


@input_error
def show_birthday(args: List[str], book: AddressBook) -> str:
    """Shows a contact's birthday. Format: show-birthday <Name>"""
    if len(args) < 1:
        raise ValueError("Invalid format. Command requires a name.")

    name = args[0]
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError(f"Contact '{name}' not found.")

    return record.show_birthday()


@input_error
def birthdays(args: List[str], book: AddressBook) -> str:
    """Shows upcoming birthdays within N days (default 7). Format: birthdays [days]"""
    days = int(args[0]) if args else 7
    return book.get_upcoming_birthdays(days)


@input_error
def search_command(args: List[str], book: AddressBook) -> str:
    """Searches contacts by name, phone, email, or address. Format: search <query>"""
    if len(args) < 1:
        raise ValueError("Invalid format. Command requires a search query.")

    query = " ".join(args)
    results = book.search_contacts(query)
    if not results:
        return "No contacts found."
    return "\n".join(str(r) for r in results)

def main():
    book = load_data() # Loads AddressBook (using Task 5 placeholder)
    
    print("Welcome to the Personal Assistant bot! Enter 'hello' to see commands.")
    
    commands_map = {
        "hello": hello_command,
        "add": add_contact,
        "change": change_contact,
        "phone": show_phone,
        "all": show_all,
        "delete": delete_contact,
        "birthdays": birthdays,  # Updated to real handler
        "add-birthday": add_birthday,
        "show-birthday": show_birthday,
        "search": search_command,
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
            # Logic to call the handler based on the required arguments
            if command == "hello":
                print(handler())
            elif command in ["all", "birthdays"]:
                print(handler(book))
            else:
                # CRUD commands and others that take args and the book
                print(handler(args, book))
        else:
            print("Invalid command. Enter 'hello' to see available commands.")

if __name__ == "__main__":
    main()