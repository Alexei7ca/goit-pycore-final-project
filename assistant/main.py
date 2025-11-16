"""Main module for the Personal Assistant CLI.

Handles command parsing, execution, and user interaction."""
from typing import Dict, List, Callable, Tuple

from assistant.models import (
    AddressBook, Record, AssistantBotError, ContactNotFoundError,
    InvalidPhoneFormatError, Note, NoteBook
)
from assistant.serialization_utils import save_data, load_data


def input_error(func: Callable) -> Callable:
    """A decorator to handle common user input errors gracefully."""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, TypeError) as e:
            # Catch errors related to missing arguments or bad format
            if "not enough values to unpack" in str(e) or \
               "Invalid format" in str(e) or \
               "missing a required argument" in str(e):
                return "Invalid command format. Please provide necessary arguments."
            return f"Error with input data: {e}"
        except AssistantBotError as e:
            # This catches all custom exceptions
            return str(e)
        except Exception as e:
            # Catch any other unexpected errors
            return f"An unexpected error occurred: {e}"
    return inner


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    """
    Parses the user input into a command and its arguments.
    Handles special multi-word commands.
    """
    parts = user_input.split()
    if not parts:
        return "", []

    cmd = parts[0].strip().lower()
    args = parts[1:]

    # Handle multi-word commands (e.g., "show all")
    if cmd == "show" and args and args[0].lower() == "all":
        return "all", []
    if cmd == "add" and args and args[0].lower() == "birthday":
        return "add-birthday", args[1:]
    if cmd == "show" and args and args[0].lower() == "birthday":
        return "show-birthday", args[1:]

    return cmd, args

# --- Contact Management Commands ---


@input_error
def add_contact(args: List[str], book: AddressBook) -> str:
    """
    Adds a new contact or adds a new phone to an existing contact.

    Args:
        args (List[str]): Expected format: [<name>, <phone>, [email], [address]]
        book (AddressBook): The address book instance.

    Returns:
        str: A confirmation message.
    """
    if len(args) < 2:
        raise ValueError("Invalid format. Command requires at least a name and phone number.")

    name, phone, *optional_fields = args
    existing_record = book.find(name)
    is_new = existing_record is None
    message = ""

    record = existing_record if not is_new else Record(name)

    try:
        record.add_phone(phone)
    except InvalidPhoneFormatError as e:
        if is_new:
            return f"Contact '{name}' NOT created. Phone number format error: {e}"
        return f"Phone NOT added to '{name}'. Format error: {e}"

    if is_new:
        book.add_record(record)
        message = f"Contact '{name}' added."
    else:
        message = f"Phone {phone} added to existing contact '{name}'."

    if optional_fields:
        email = optional_fields[0]
        record.add_email(email)
        message += f" Email: {email} added."

    if len(optional_fields) > 1:
        address_parts = " ".join(optional_fields[1:])
        record.add_address(address_parts)
        message += f" Address: {address_parts} added."

    return message


@input_error
def change_contact(args: List[str], book: AddressBook) -> str:
    """
    Changes an existing contact's old phone number to a new one.

    Args:
        args (List[str]): Expected format: [<name>, <old_phone>, <new_phone>]
        book (AddressBook): The address book instance.

    Returns:
        str: A confirmation message.
    """
    if len(args) < 3:
        raise ValueError("Invalid format. Command requires a name, old phone, and new phone.")

    name, old_phone, new_phone, *_ = args
    record = book.find(name)

    if record is None:
        raise ContactNotFoundError(f"Contact '{name}' not found.")

    record.edit_phone(old_phone, new_phone)

    return f"Phone number for '{name}' successfully changed from {old_phone} to {new_phone}."


@input_error
def show_contact_detail(args: List[str], book: AddressBook) -> str:
    """
    Shows the full details for a specific contact.

    Args:
        args (List[str]): Expected format: [<name>]
        book (AddressBook): The address book instance.

    Returns:
        str: The contact's details.
    """
    if len(args) < 1:
        raise ValueError("Invalid format. Command requires a name.")

    name = args[0]
    record = book.find(name)

    if record is None:
        raise ContactNotFoundError(f"Contact '{name}' not found.")

    return str(record)


def show_all(book: AddressBook) -> str:
    """Shows all contacts in the address book."""
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

    Args:
        args (List[str]): Expected format: [<name>]
        book (AddressBook): The address book instance.

    Returns:
        str: A confirmation message.
    """
    if len(args) < 1:
        raise ValueError("Invalid format. Command requires a name.")

    name = args[0]
    book.delete(name)

    return f"Contact '{name}' deleted successfully."


@input_error
def add_birthday(args: List[str], book: AddressBook) -> str:
    """
    Adds or updates a birthday for a contact.

    Args:
        args (List[str]): Expected format: [<name>, <DD.MM.YYYY>]
        book (AddressBook): The address book instance.

    Returns:
        str: A confirmation message.
    """
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
    """
    Shows a contact's birthday.

    Args:
        args (List[str]): Expected format: [<name>]
        book (AddressBook): The address book instance.

    Returns:
        str: The contact's birthday information.
    """
    if len(args) < 1:
        raise ValueError("Invalid format. Command requires a name.")

    name = args[0]
    record = book.find(name)
    if record is None:
        raise ContactNotFoundError(f"Contact '{name}' not found.")

    return record.show_birthday()


@input_error
def birthdays(args: List[str], book: AddressBook) -> str:
    """
    Shows upcoming birthdays within N days. Defaults to 7 days.

    Args:
        args (List[str]): Expected format: [[days]]
        book (AddressBook): The address book instance.

    Returns:
        str: A list of upcoming birthdays.
    """
    days = 7
    if args:
        try:
            days = int(args[0])
        except ValueError:
            raise ValueError("The 'days' argument must be an integer.")

    return book.get_upcoming_birthdays(days)


@input_error
def search_command(args: List[str], book: AddressBook) -> str:
    """
    Searches contacts by name, phone, email, or address.

    Args:
        args (List[str]): The search query.
        book (AddressBook): The address book instance.

    Returns:
        str: A list of matching contacts.
    """
    if len(args) < 1:
        raise ValueError("Invalid format. Command requires a search query.")

    query = " ".join(args)
    results = book.search_contacts(query)
    if not results:
        return "No contacts found."
    return "\n".join(str(r) for r in results)

# --- Note Management Commands ---


@input_error
def add_note(args: List[str], notes: NoteBook) -> str:
    """
    Adds a new note or overwrites an existing one.

    Args:
        args (List[str]): Expected format: [<title>, <content>, [#tags...]]
        notes (NoteBook): The notebook instance.

    Returns:
        str: A confirmation message.
    """
    if len(args) < 2:
        raise ValueError("Invalid format. Command requires a title and content.")

    title = args[0]
    note_exists = notes.find_note_by_id(title) is not None

    rest = " ".join(args[1:])
    hash_index = rest.find('#')

    if hash_index != -1:
        content = rest[:hash_index].strip()
        tags_part = rest[hash_index:]
        tags = [tag for tag in tags_part.split() if tag.startswith('#')]
    else:
        content = rest.strip()
        tags = []

    note = Note(title, content, tags)
    notes.add_note(note)

    if note_exists:
        return f"Note '{title}' updated successfully."
    return f"Note '{title}' added successfully."


@input_error
def edit_note(args: List[str], notes: NoteBook) -> str:
    """
    Edits a note's content.

    Args:
        args (List[str]): Expected format: [<title>, <new_content>]
        notes (NoteBook): The notebook instance.

    Returns:
        str: A confirmation message.
    """
    if len(args) < 2:
        raise ValueError("Invalid format. Command requires a title and a new content.")

    title = args[0]
    new_content = " ".join(args[1:])

    notes.edit_note_text(title, new_content)
    return f"Note '{title}' updated successfully."


@input_error
def delete_note(args: List[str], notes: NoteBook) -> str:
    """
    Deletes a note by title.

    Args:
        args (List[str]): Expected format: [<title>]
        notes (NoteBook): The notebook instance.

    Returns:
        str: A confirmation message.
    """
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
    """
    Adds tags to a note.

    Args:
        args (List[str]): Expected format: [<title>, #tag1, #tag2, ...]
        notes (NoteBook): The notebook instance.

    Returns:
        str: A confirmation message.
    """
    if len(args) < 2:
        raise ValueError("Invalid format. Command requires a title and at least one tag.")

    title = args[0]
    tags = args[1:]

    notes.add_tag_to_note(title, tags)
    return f"Note '{title}' updated successfully."


@input_error
def remove_note_tag(args: List[str], notes: NoteBook) -> str:
    """
    Removes a tag from a note.

    Args:
        args (List[str]): Expected format: [<title>, #tag1]
        notes (NoteBook): The notebook instance.

    Returns:
        str: A confirmation message.
    """
    if len(args) < 2:
        raise ValueError("Invalid format. Command requires a title and a tag.")

    title = args[0]
    tag = args[1].lstrip('#')

    notes.remove_tag_from_note(title, tag)
    return f"Note '{title}' updated successfully."


@input_error
def find_notes_by_tag(args: List[str], notes: NoteBook) -> str:
    """
    Displays notes filtered by tag.

    Args:
        args (List[str]): Expected format: [#tag]
        notes (NoteBook): The notebook instance.

    Returns:
        str: A formatted table of matching notes.
    """
    if len(args) < 1:
        raise ValueError("Invalid format. Command requires a tag.")

    tag_query = " ".join(args)

    filtered = notes.find_notes_by_tag(tag_query)
    if not filtered:
        return f"No notes with tag {tag_query} found."

    return show_notes_table(f"Notes with tag {tag_query}", filtered)


@input_error
def show_notes_sorted(args: List[str], notes: NoteBook) -> str:
    """
    Displays all notes sorted by a key.

    Args:
        args (List[str]): Expected format: [[sort_key]], where sort_key is 'title' or 'tags'.
        notes (NoteBook): The notebook instance.

    Returns:
        str: A formatted table of sorted notes.
    """
    sort_key = args[0].lower() if args else "title"

    if sort_key == 'tags':
        sorted_notes = notes.sort_notes_by_tag_count()
    else:
        sorted_notes = notes.sort_notes_by_title()

    return show_notes_table("Sorted notes", sorted_notes)


def show_notes_table(table_title: str, notes_list: list[Note]) -> str:
    """
    Formats a list of notes into a string table.

    Args:
        table_title (str): The title for the table.
        notes_list (list[Note]): The list of notes to format.

    Returns:
        str: The formatted string.
    """
    result = f"{table_title}:\n"
    for note in notes_list:
        result += f"{note}\n"
        result += f"{'-' * 40}\n"
    return result.strip()


def hello_command() -> str:
    """Displays a welcome message and a command manual."""
    return """
Hello! Welcome to the Personal Assistant bot. Here are the available commands:
| Command             | Arguments                         | Example                               |
| :------------------ | :-------------------------------- | :------------------------------------ |
| hello               |                                   | hello                                 |
| add                 | <Name> <Phone> [Email] [Address]  | add John 1234567890 john@mail.com     |
| change              | <Name> <Old Phone> <New Phone>    | change John 123... 098...             |
| show                | <Name>                            | show John                             |
| all                 |                                   | all                                   |
| delete              | <Name>                            | delete John                           |
| add-birthday        | <Name> <DD.MM.YYYY>               | add-birthday John 01.01.1990          |
| show-birthday       | <Name>                            | show-birthday John                    |
| birthdays           | [days]                            | birthdays 14                          |
| search              | <query>                           | search John                           |
| add-note            | <title> <content> [#tags...]      | add-note Shopping Eggs Milk #urgent   |
| edit-note           | <title> <new_content>             | edit-note Shopping Milk, Tea          |
| delete-note         | <title>                           | delete-note Shopping                  |
| add-tag             | <title> [#tag1] [#tag2]           | add-tag Shopping #urgent #home        |
| remove-tag          | <title> <#tag>                    | remove-tag Shopping #urgent           |
| find-notes-by-tag   | <#tag>                            | find-notes-by-tag #urgent             |
| show-notes-sorted   | [title/tags]                      | show-notes-sorted tags                |
| show-all-notes      |                                   | show-all-notes                        |
| close / exit        |                                   | close                                 |
"""


def main():
    """Main function to run the CLI assistant."""
    book, notes = load_data()

    print("Welcome to the Personal Assistant bot! Enter 'hello' to see commands.")

    commands_map = {
        "hello": hello_command,
        "add": add_contact,
        "change": change_contact,
        "show": show_contact_detail,
        "all": show_all,
        "delete": delete_contact,
        "birthdays": birthdays,
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

    try:
        while True:
            try:
                user_input = input("Enter a command: ").strip()
            except EOFError:  # Handles Ctrl+D
                print("\nGood bye!")
                break

            if not user_input:
                continue

            command, args = parse_input(user_input)

            if command in ["close", "exit"]:
                print("Good bye!")
                break  # Exit loop, triggering the final save

            handler = commands_map.get(command)

            if handler:
                # Call the handler based on its argument requirements
                if command == "hello":
                    print(handler())
                elif command == "all":
                    print(handler(book))
                elif command == "show-all-notes":
                    print(handler(notes))
                elif command in [
                    "birthdays", "add-birthday", "show-birthday", "search",
                    "add", "change", "show", "delete"
                ]:
                    print(handler(args, book))
                elif command in [
                    "add-note", "edit-note", "delete-note", "add-tag",
                    "remove-tag", "find-notes-by-tag", "show-notes-sorted"
                ]:
                    print(handler(args, notes))
                else:
                    print("Unknown internal command logic.")
            else:
                print("Invalid command. Enter 'hello' to see available commands.")

    except KeyboardInterrupt:  # Handles Ctrl+C
        print("\nInterruption detected. Saving data...")
        # Fall through to final save

    # Final save point for all exit modes
    save_data(book, notes)


if __name__ == "__main__":
    main()