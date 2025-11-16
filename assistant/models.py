"""
Core data models for the Personal Assistant application.

Includes classes for AddressBook, Contacts (Record), Notes, and all related fields.
Also defines custom exceptions for the application.
"""
from collections import UserDict
import re
from typing import List, Optional
from datetime import datetime, date, timedelta


# --- Custom Exceptions ---

class AssistantBotError(Exception):
    """Base exception for all custom errors in the Personal Assistant Bot."""
    pass


class DataValidationError(AssistantBotError):
    """Base exception for validation errors in data fields (e.g., Phone, Email)."""
    pass


class InvalidNameFormatError(DataValidationError):
    """Raised for invalid contact names."""
    pass


class InvalidPhoneFormatError(DataValidationError):
    """Raised for invalid phone number formats."""
    pass


class InvalidEmailFormatError(DataValidationError):
    """Raised for invalid email formats."""
    pass


class InvalidBirthdayFormatError(DataValidationError):
    """Raised for invalid birthday formats or dates."""
    pass


class InvalidAddressFormatError(DataValidationError):
    """Placeholder for specific Address validation."""
    pass


class InvalidTagFormatError(DataValidationError):
    """Raised when a tag is empty or contains invalid characters."""
    pass


class ContactNotFoundError(AssistantBotError):
    """Raised when a contact is not found in the address book."""
    pass


class PhoneNotFoundError(AssistantBotError):
    """Raised when a phone number is not found on a contact record."""
    pass


class NoteNotFoundError(AssistantBotError):
    """Raised when a note is not found in the notebook."""
    pass


# --- Core Field Classes ---

class Field:
    """Base class for all record fields."""
    def __init__(self, value):
        self._value = self._validate(value)

    def __str__(self):
        return str(self._value)

    @property
    def value(self):
        """Getter for the field's value."""
        return self._value

    @value.setter
    def value(self, new_value):
        """Setter for the field's value, with validation."""
        self._value = self._validate(new_value)

    def _validate(self, value):
        """
        Validation logic for the field. Subclasses should override this.
        By default, it performs no validation.
        """
        return value


class Name(Field):
    """A field for storing and validating a contact's name."""
    def _validate(self, value):
        if not isinstance(value, str) or len(value.strip()) <= 2:
            raise InvalidNameFormatError("Name must contain more than 2 characters.")
        return value.strip()


class Phone(Field):
    """A field for storing and validating a 10-digit phone number."""
    def _validate(self, value):
        if not (isinstance(value, str) and value.isdigit() and len(value) == 10):
            raise InvalidPhoneFormatError("Phone must be a 10-digit number.")
        return value


class Email(Field):
    """A field for storing and validating an email address."""
    def _validate(self, value):
        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(pattern, value):
            raise InvalidEmailFormatError("Invalid email format.")
        return value


class Address(Field):
    """A field for storing a physical address."""
    pass


class Birthday(Field):
    """A field for storing and validating a birthday."""
    value: date

    def _validate(self, value):
        if value is None or value == "":
            return None

        try:
            parsed_date = datetime.strptime(value.strip(), "%d.%m.%Y").date()
        except ValueError:
            raise InvalidBirthdayFormatError("Invalid date format. Use DD.MM.YYYY")

        if parsed_date > date.today():
            raise InvalidBirthdayFormatError("Birthday cannot be in the future.")

        return parsed_date

    def __str__(self):
        return self.value.strftime("%d.%m.%Y") if self.value else ""


class Record:
    """Represents a contact record, containing a name and other fields."""
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.birthday: Optional[Birthday] = None
        self.email: Optional[Email] = None
        self.address: Optional[Address] = None

    def __str__(self):
        phones_str = '; '.join(str(p) for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        email_str = f", email: {self.email}" if self.email else ""
        address_str = f", address: {self.address}" if self.address else ""
        return f"Contact name: {self.name}, phones: {phones_str}{birthday_str}{email_str}{address_str}"

    def add_phone(self, phone_number: str) -> None:
        """Adds a phone number to the contact, avoiding duplicates."""
        if not self.find_phone(phone_number):
            self.phones.append(Phone(phone_number))

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Edits an existing phone number."""
        phone = self.find_phone(old_phone)
        if phone:
            phone.value = new_phone
        else:
            raise PhoneNotFoundError(f"Phone {old_phone} not found.")

    def find_phone(self, phone_number: str) -> Optional[Phone]:
        """Finds a Phone object by its number string."""
        return next((p for p in self.phones if p.value == phone_number), None)
    
    def delete_phone(self, phone_number: str):
        """Deletes a phone number from the contact."""
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)
        else:
            raise PhoneNotFoundError(f"Phone {phone_number} not found.")
        
    def add_email(self, email_str: str) -> None:
        """Adds or updates the contact's email."""
        self.email = Email(email_str)

    def add_address(self, address_str: str) -> None:
        """Adds or updates the contact's address."""
        self.address = Address(address_str)
        
    def add_birthday(self, date_str: str):
        """Adds or updates the contact's birthday."""
        self.birthday = Birthday(date_str)

    def show_birthday(self) -> str:
        """Returns the birthday as a formatted string or a 'not set' message."""
        if not self.birthday or not self.birthday.value:
            return f"No birthday set for {self.name}."
        return f"{self.name}'s birthday: {self.birthday}"


class AddressBook(UserDict[str, Record]):
    """A collection of contact records."""
    def add_record(self, record: Record):
        """Adds a record to the address book."""
        self.data[self._key(str(record.name))] = record

    def find(self, name: str) -> Optional[Record]:
        """Finds a record by name (case-insensitive)."""
        return self.data.get(self._key(name))

    def delete(self, name: str):
        """Deletes a record by name."""
        standardized_name = self._key(name)
        if standardized_name in self.data:
            del self.data[standardized_name]
        else:
            raise ContactNotFoundError(f"Contact {name} not found.")
        
    def _key(self, name: str) -> str:
        """Standardizes a name for use as a dictionary key."""
        return name.strip().casefold()
            
    def get_upcoming_birthdays(self, days: int = 7) -> str:
        """Returns a formatted string of contacts with birthdays within the given days."""
        today = date.today()
        upcoming = []

        for record in self.data.values():
            if not record.birthday or not record.birthday.value:
                continue

            bday = record.birthday.value.replace(year=today.year)
            if bday < today:
                bday = bday.replace(year=today.year + 1)

            delta = (bday - today).days
            if 0 <= delta <= days:
                # Weekend rollover: move Sat/Sun to Monday
                if bday.weekday() == 5:  # Saturday
                    bday += timedelta(days=2)
                elif bday.weekday() == 6:  # Sunday
                    bday += timedelta(days=1)
                upcoming.append((record.name.value, bday.strftime("%d.%m.%Y")))

        if not upcoming:
            return "No upcoming birthdays."

        result = "Upcoming birthdays:\n"
        for name, bday_str in sorted(upcoming, key=lambda x: datetime.strptime(x[1], "%d.%m.%Y")):
            result += f"{name}: {bday_str}\n"
        return result.strip()

    def search_contacts(self, query: str) -> List[Record]:
        """Finds contacts by matching a query against all text fields."""
        query_lower = query.lower()
        results = []

        for record in self.data.values():
            fields_to_check = [record.name.value.lower()]
            fields_to_check.extend(p.value.lower() for p in record.phones)

            if record.email and record.email.value:
                fields_to_check.append(str(record.email.value).lower())
            if record.address and record.address.value:
                fields_to_check.append(str(record.address.value).lower())

            if any(query_lower in field for field in fields_to_check):
                results.append(record)

        return results


class Note:
    """Represents a note with a title, content, and a set of tags."""
    def __init__(self, title: str, content: str, tags: list[str] | set[str] = None):
        if not title:
            raise ValueError("Note title cannot be empty")
        self.__title = title
        self.content = content
        self.tags = set()
        if tags:
            for tag in tags:
                self.add_tag(tag)

    def __str__(self):
        preview = (self.content[:50] + "...") if len(self.content) > 50 else self.content
        tags_str = ", ".join(f"#{t}" for t in sorted(self.tags)) if self.tags else "No tags"
        return f"Note: '{self.title}'\nContent: {preview}\nTags: {tags_str}"

    
    
    @property
    def title(self):
        """Getter for the note's title (which is its unique ID)."""
        return self.__title
    
    def add_tag(self, tag:str):
        """Adds a tag to the note, ensuring it's valid."""
        cleaned_tag = tag.strip().lower().lstrip('#')
        if not cleaned_tag or " " in cleaned_tag:
            raise InvalidTagFormatError(f"Invalid tag: '{tag}'. Tags cannot be empty or contain spaces.")
        self.tags.add(cleaned_tag)

    def remove_tag(self, tag:str):
        """Removes a tag from the note."""
        cleaned_tag = tag.strip().lower().lstrip('#')
        self.tags.discard(cleaned_tag)  # Use discard to avoid error if tag not found

    

class NoteBook(UserDict):
    """A collection of notes."""
    data: dict[str, Note]

    def _key(self, title: str) -> str:
        """Standardizes a title for use as a dictionary key."""
        return title.strip().casefold()

    def add_note(self, note: Note):
        """Adds a note to the notebook."""
        self.data[self._key(note.title)] = note

    def find_note_by_id(self, title: str) -> Optional[Note]:
        """Finds a note by its title (case-insensitive)."""
        return self.data.get(self._key(title))

    def edit_note_text(self, title: str, new_text:str):
        """Updates the content of an existing note."""
        note = self.find_note_by_id(title)
        if note:
            note.content = new_text
        else:
            raise NoteNotFoundError(f"Note '{title}' not found.")

    def delete_note(self, title: str):
        """Deletes a note by its title."""
        key = self._key(title)
        if key in self.data:
            del self.data[key]
        else:
            raise NoteNotFoundError(f"Note '{title}' not found.")
        
    def add_tag_to_note(self, title: str, tags: list[str] | set[str]):
        """Adds one or more tags to an existing note."""
        note = self.find_note_by_id(title)
        if not note:
            raise NoteNotFoundError(f"Note '{title}' not found.")
        
        for tag in tags:
            note.add_tag(tag)

    def remove_tag_from_note(self, title: str, tag: str):
        """Removes a single tag from an existing note."""
        note = self.find_note_by_id(title)
        if not note:
            raise NoteNotFoundError(f"Note '{title}' not found.")
        
        note.remove_tag(tag)

    def find_notes_by_tag(self, tag: str) -> list[Note]:
        """Finds all notes containing a specific tag."""
        cleaned_tag = tag.strip().lower().lstrip('#')
        if not cleaned_tag or " " in cleaned_tag:
            raise InvalidTagFormatError(f"Invalid tag: '{tag}'.")
        
        return  [note for note in self.data.values() if cleaned_tag in note.tags]
    
    def sort_notes_by_title(self) -> list[Note]:
        """Returns all notes sorted alphabetically by title."""
        return sorted(self.data.values(), key=lambda note: note.title.lower())
    
    def sort_notes_by_tag_count(self) -> list[Note]:
        """Returns all notes sorted by tag count (descending), then title."""
        return sorted(self.data.values(), key=lambda note: (-len(note.tags), note.title.lower()))