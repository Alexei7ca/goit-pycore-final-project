from typing import List
from .models import AddressBook, NoteBook, Record, Note, DataValidationError

# This file contains backend logic specifically for the GUI.
# These functions are not decorated with @input_error, so they will
# raise exceptions that the GUI can catch and display in a message box.

def add_contact_gui(name: str, phone: str, email: str, address: str, book: AddressBook):
    """
    Adds a contact. Raises DataValidationError on failure.
    """
    if book.find(name):
        # For GUI, adding to an existing contact is better handled by "Edit"
        raise DataValidationError(f"Contact '{name}' already exists. Use Edit instead.")

    record = Record(name)
    record.add_phone(phone) # This can raise InvalidPhoneFormatError
    if email:
        record.add_email(email) # This can raise InvalidEmailFormatError
    if address:
        record.add_address(address)
    book.add_record(record)

def add_note_gui(title: str, content: str, tags: List[str], notes: NoteBook):
    """
    Adds a note. Raises DataValidationError on failure.
    """
    if notes.find_note_by_id(title):
        raise DataValidationError(f"Note with title '{title}' already exists. Use Edit instead.")
    
    note = Note(title, content, tags) # This can raise InvalidTagFormatError
    notes.add_note(note)

def edit_contact_gui(record: Record, new_phone: str, new_email: str, new_address: str):
    """
    Safely edits a contact's fields in place. Raises DataValidationError on failure.
    """
    # Validate and update phone
    if new_phone and new_phone != (record.phones[0].value if record.phones else ""):
        # For simplicity, we assume editing the first phone.
        # A more complex UI would handle multiple phones.
        original_phone = record.phones[0].value if record.phones else None
        if original_phone:
            record.edit_phone(original_phone, new_phone)
        else:
            record.add_phone(new_phone)

    # Validate and update email
    if new_email != (record.email.value if record.email else ""):
        record.add_email(new_email)

    # Update address (no validation in model)
    if new_address != (record.address.value if record.address else ""):
        record.add_address(new_address)

def edit_note_gui(note: Note, new_content: str, new_tags: List[str]):
    """
    Edits a note's content and tags. Raises DataValidationError on failure.
    """
    note.content = new_content
    
    # Re-create tags from scratch
    note.tags.clear()
    for tag in new_tags:
        note.add_tag(tag) # This can raise InvalidTagFormatError

def search_notes_by_tag_gui(query: str, notes: NoteBook) -> List[Note]:
    """
    Finds notes where any tag starts with the query string (partial match).
    """
    cleaned_query = query.strip().lower().lstrip('#')
    if not cleaned_query:
        return []
    
    results = []
    for note in notes.data.values():
        if any(tag.startswith(cleaned_query) for tag in note.tags):
            results.append(note)
    return results

def delete_contact_gui(name: str, book: AddressBook):
    """Deletes a contact, raising ContactNotFoundError on failure."""
    book.delete(name)

def delete_note_gui(title: str, notes: NoteBook):
    """Deletes a note, raising NoteNotFoundError on failure."""
    notes.delete_note(title)
