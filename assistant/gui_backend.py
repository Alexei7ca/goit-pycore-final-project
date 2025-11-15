from typing import List
from .models import AddressBook, NoteBook, Record, Note, DataValidationError

# This file contains backend logic specifically for the GUI.
# These functions are not decorated with @input_error, so they will
# raise exceptions that the GUI can catch and display in a message box.

def add_contact_gui(name: str, phones_str: str, email: str, address: str, birthday: str, book: AddressBook):
    """
    Adds a contact. Handles multiple comma-separated phones. Raises DataValidationError on failure.
    """
    if book.find(name):
        raise DataValidationError(f"Contact '{name}' already exists. Use Edit instead.")

    record = Record(name)
    
    # Add multiple phones
    phone_numbers = [p.strip() for p in phones_str.split(',')]
    if not phone_numbers or not phone_numbers[0]:
        raise DataValidationError("At least one phone number is required.")
    for p_num in phone_numbers:
        record.add_phone(p_num)

    if email:
        record.add_email(email)
    if address:
        record.add_address(address)
    if birthday:
        record.add_birthday(birthday)
        
    book.add_record(record)

def add_note_gui(title: str, content: str, tags: List[str], notes: NoteBook):
    """
    Adds a note. Raises DataValidationError on failure.
    """
    if notes.find_note_by_id(title):
        raise DataValidationError(f"Note with title '{title}' already exists. Use Edit instead.")
    
    note = Note(title, content, tags)
    notes.add_note(note)

def edit_contact_gui(record: Record, new_phones_str: str, new_email: str, new_address: str, new_birthday: str):
    """
    Safely edits a contact's fields in place. Raises DataValidationError on failure.
    """
    # For simplicity, we clear old phones and add the new ones.
    new_phone_numbers = [p.strip() for p in new_phones_str.split(',')]
    if not new_phone_numbers or not new_phone_numbers[0]:
        raise DataValidationError("At least one phone number is required.")

    record.phones.clear()
    for p_num in new_phone_numbers:
        record.add_phone(p_num)

    if new_email != (record.email.value if record.email else ""):
        record.add_email(new_email)

    if new_address != (record.address.value if record.address else ""):
        record.add_address(new_address)
        
    if new_birthday != (str(record.birthday) if record.birthday else ""):
        record.add_birthday(new_birthday)


def edit_note_gui(note: Note, new_content: str, new_tags: List[str]):
    """
    Edits a note's content and tags. Raises DataValidationError on failure.
    """
    note.content = new_content
    
    note.tags.clear()
    for tag in new_tags:
        note.add_tag(tag)

def search_notes_by_multiple_tags_gui(query_str: str, notes: NoteBook) -> List[Note]:
    """
    Finds notes that match ALL of the comma-separated partial tags.
    e.g., "work, ur" will match a note with tags {#work, #urgent}.
    """
    query_tags = [tag.strip().lower().lstrip('#') for tag in query_str.split(',') if tag.strip()]
    if not query_tags:
        return []
    
    results = []
    for note in notes.data.values():
        # Check if for every query_tag, at least one of the note's tags starts with it.
        if all(any(note_tag.startswith(query_tag) for note_tag in note.tags) for query_tag in query_tags):
            results.append(note)
    return results

def get_birthdays_gui(days: int, book: AddressBook) -> str:
    """
    Returns a formatted string of upcoming birthdays.
    """
    return book.get_upcoming_birthdays(days)

def delete_contact_gui(name: str, book: AddressBook):
    """Deletes a contact, raising ContactNotFoundError on failure."""
    book.delete(name)

def delete_note_gui(title: str, notes: NoteBook):
    """Deletes a note, raising NoteNotFoundError on failure."""
    notes.delete_note(title)