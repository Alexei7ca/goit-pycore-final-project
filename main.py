from typing import Dict, List, Callable, Tuple
from models import (
    AddressBook, Record, AssistantBotError, ContactNotFoundError,
    Note, NoteBook
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
        # Catch specific custom errors from models.py
        except AssistantBotError as e:
            # This catches all custom exceptions (ContactNotFoundError, NoteNotFoundError, etc.)
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
| Command        | Arguments                    | Example                       | Description                               |
| :------------- | :--------------------------- | :---------------------------- | :---------------------------------------- |
| hello          |                              | hello                         | Displays this manual.                     |
| add     | <Name> <Phone> [Email] [Address...] | add John 1234567890 john@mail | Adds a new contact or phone (with optional email/address).|
| change         | <Name> <Old Phone> <New P>   | change John 123.. 098..       | Updates an existing contact's phone.      |
| phone          | <Name>                       | phone John                    | Shows a contact's full details.           |
| all            |                              | all                           | Lists all saved contacts.                 |
| delete         | <Name>                       | delete John                   | Deletes a contact.                        |
| add-birthday   | <Name> <DD.MM.YYYY>          | add-birthday John 01.01.1990  | Adds contact birthday (Task 3).           |
| show-birthday  | <Name>                       | show-birthday John            | Shows contact birthday (Task 3).          |
| birthdays      |                              | birthdays                     | Shows upcoming birthdays (Task 3).        |
| close          |                              | close                         | Exits the bot (data will be saved).       |
| exit           |                              | exit                          | Exits the bot (data will be saved).       |
| add-note       | <title> <content> #tag1 #tag2| add-note Shopping Eggs Milk   | Adds a new note.                          |
| edit-note      | <title> <new_content>        | edit-note Shopping, Milk, Tea | Edits an existing note.                   |
| delete-note    | <title>                      | delete-note Shopping          | Deletes a note.                           |
| add-tag        | <title> #tag1 #tag2 ...      | add-tag shopping #urgent #home| Adds tags to existing note.               |
| remove-tag     | <title> #tag1                | remove-tag shopping #urgent   | Remove tag from existing note.            |
| find-notes-by-tag | #tag1                     | find-notes-by-tag #urgent     | Shows notes filtered by tag               |
| show-notes-sorted | [sort_key]                | show-notes-sorted tags        | shows a list of all notes sorted based on sort_key |
| show-all-notes |                              | show-all-notes                | Lists all notes.                          |
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

@input_error
def add_note(args: List[str], notes: NoteBook) -> str:
    """Adds a new note. Format: add-note <title> <content> #tag1 #tag2"""
    if len(args) < 2:
        raise ValueError("Invalid format. Command requires a title and content.")
    
    title = args[0]
    rest = " ".join(args[1:])
    hash_index = rest.find('#')
    
    if hash_index != -1:
        content = rest[:hash_index].strip()
        tags_part = rest[hash_index:]
        tags = [tag.lstrip('#') for tag in tags_part.split()] # if tag.startswith('#') -  add-note amynote4 bla-bla #tag1 tag2 - do we want tag2 aplied or not?
    else:
        content = rest.strip()
        tags = []

    note = Note(title, content, tags)
    notes.add_note(note)
    return f"Note '{title}' added successfully."

@input_error
def edit_note(args: List[str], notes: NoteBook) -> str:
    """Edits a note's content. Format: edit-note <title> <new_content>"""
    if len(args) < 2:
       raise ValueError("Invalid format. Command requires a title and a new content.") 
    
    title = args[0]
    new_content = " ".join(args[1:])

    notes.edit_note_text(title, new_content)
    return f"Note '{title}' updated successfully."

@input_error
def delete_note(args: List[str], notes: NoteBook) -> str:
    """Deletes a note by title. Format: delete-note <title>"""
    if len(args) < 1:
        raise ValueError("Invalid format. Command requires a title.")
    
    title = args[0]
    notes.delete_note(title)
    return f"Note '{title}' deleted successfully."

@input_error
def show_all_notes(notes: NoteBook) -> str:
    """Displays all notes."""
    if not notes.data:
        return "No notes found."
    
    result = "All notes:\n"
    for note in notes.data.values():
        result += f"{note}\n"
    return result.strip()

@input_error
def add_note_tag(args: List[str], notes: NoteBook) -> str:
    """Adds tags to a note. Format: add-tag <title> #tag1 #tag2 ..."""
    if len(args) < 2:
       raise ValueError("Invalid format. Command requires a title and at least one tag.") 
    
    title = args[0]
    tags = args[1:]

    notes.add_tag_to_note(title, tags)
    return f"Note '{title}' updated successfully."

@input_error
def remove_note_tag(args: List[str], notes: NoteBook) -> str:
    """Removes tag from a note. Format: remove-tag <title> #tag1"""
    if len(args) < 2:
       raise ValueError("Invalid format. Command requires a title and a tag.") 
    
    title = args[0]
    tag = args[1]

    notes.remove_tag_from_note(title, tag)
    return f"Note '{title}' updated successfully."

@input_error
def find_notes_by_tag(args: List[str], notes: NoteBook) -> str:
    """Displays notes filtered by tag. Format: find-by-tag #tag1"""
    if len(args) < 1:
       raise ValueError("Invalid format. Command requires a tag.")
    
    tag = args[0]

    filtered = notes.find_notes_by_tag(tag)
    if not filtered:
        return F"No notes with tag {tag} found."
    
    return show_notes_table(f"Notes with tag {tag}", filtered)
   

@input_error
def show_notes_sorted(args: List[str], notes: NoteBook) -> str:
    """Displays all notes sorted based on sort_key. Format: show_notes_sorted [sort_key]"""
    sort_key = args[0].lower() if args else "title"

    if sort_key == 'tags':
        sorted = notes.sort_notes_by_tag_count()
    else:
        sorted = notes.sort_notes_by_title()

    return show_notes_table("Sorted notes", sorted)
    

def show_notes_table(tableTitle: str, notes: list[Note]):
    result = f"{tableTitle}:\n"
    for note in notes:
        result += f"{note}\n"
        result += f"{'*' * 10}\n"
    return result.strip()


def main():
# --- Load both objects from the utility function ---
    book, notes = load_data()
    
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
        "add-note": add_note,
        "edit-note": edit_note,
        "delete-note": delete_note,
        "show-all-notes": show_all_notes,
        "add-tag": add_note_tag,
        "remove-tag": remove_note_tag,
        "find-notes-by-tag": find_notes_by_tag,
        "show-notes-sorted": show_notes_sorted
    }

    while True:
        try:
            user_input = input("Enter a command: ").strip()
        except EOFError:
            print("\nGood bye!")
            save_data(book, notes)
            break
            
        if not user_input:
            continue
            
        command, args = parse_input(user_input)
        
        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book, notes)
            break
            
        handler = commands_map.get(command)
        
        if handler:
            # Logic to call the handler based on the required arguments
            if command == "hello":
                print(handler())
            elif command == "all":
                print(handler(book))
            elif command == "show-all-notes":
                print(handler(notes))
            elif command in ["birthdays", "add-birthday", "show-birthday", "search"]:
                print(handler(args, book))
            elif command in ["add-note", "edit-note", "delete-note", "add-tag", "remove-tag", "find-notes-by-tag", "show-notes-sorted"]:
                print(handler(args, notes))
            else:
            # Should be unreachable with current commands
                print("Unknown internal command logic.")

        else:
            print("Invalid command. Enter 'hello' to see available commands.")

if __name__ == "__main__":
    main()
    