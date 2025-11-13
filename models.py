from collections import UserDict
import re
from typing import List, Optional
from datetime import datetime, date, timedelta

# --- Custom Exceptions (Required by main.py @input_error) ---
class AssistantBotError(Exception):
    """Base exception for all custom errors in the Personal Assistant Bot."""
    pass

class DataValidationError(AssistantBotError):
    """Base exception for validation errors in data fields (e.g., Phone, Email)."""
    pass

# Contact/Field Errors (Inheriting from DataValidationError)
class InvalidNameFormatError(DataValidationError):
    pass
class InvalidPhoneFormatError(DataValidationError):
    pass
class InvalidEmailFormatError(DataValidationError):
    pass
class InvalidBirthdayFormatError(DataValidationError):
    pass
class InvalidAddressFormatError(DataValidationError):
    pass # Placeholder for specific Address validation
class InvalidTagFormatError(DataValidationError):
    pass # Raised when a tag is empty or contains invalid characters (e.g., spaces)

# Record/Book Errors (Inheriting from AssistantBotError)
class ContactNotFoundError(AssistantBotError):
    pass
class PhoneNotFoundError(AssistantBotError):
    pass

# Notes Errors (Inheriting from AssistantBotError)
class NoteNotFoundError(AssistantBotError):
    pass

# --- Core Field Classes (Minimal working placeholders) ---
class Field:
    def __init__(self, value):
        self._value = self._validate(value)

    def __str__(self):
        return str(self._value)
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        self._value = self._validate(new_value)
    
    def _validate(self, value):
        """Subclasses can override this."""
        return value


class Name(Field):
    def _validate(self, value):
        if not isinstance(value, str) or len(value.strip()) <= 2:
            raise InvalidNameFormatError("⚠️ Name must contain more than 2 characters.")
        return value.strip()
        

class Phone(Field):
    def _validate(self, value):
        if not (isinstance(value, str) and value.isdigit() and len(value) == 10):
            raise InvalidPhoneFormatError("⚠️ Phone must be a 10-digit number.")
        return value


class Email(Field):
    def _validate(self, value):
        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(pattern, value):
            raise InvalidEmailFormatError("⚠️ Invalid email format.")
        return value


class Address(Field):
    pass


class Birthday(Field):
    value: date

    def _validate(self, value):
        if value is None or value == "":
            return None
        
        try:
            parsed_date = datetime.strptime(value.strip(), "%d.%m.%Y").date()
        except ValueError:
            raise InvalidBirthdayFormatError("⚠️ Invalid date format. Use DD.MM.YYYY")
        
        if parsed_date > date.today():
                raise InvalidBirthdayFormatError("⚠️ Birthday cannot be in the future.")
        
        return parsed_date

    def __str__(self):
        return self.value.strftime("%d.%m.%Y") if self.value else ""
    

class Record:
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
        if not self.find_phone(phone_number):
            self.phones.append(Phone(phone_number))

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        phone = self.find_phone(old_phone)
        if phone:
            phone.value = new_phone
        else:
            raise PhoneNotFoundError(f"Phone {old_phone} not found.")
    
    def find_phone(self, phone_number: str) -> Optional[Phone]:
        return next((p for p in self.phones if p.value == phone_number), None)
    
    def delete_phone(self, phone_number: str):
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)
        else:
            raise PhoneNotFoundError(f"⚠️ Phone {phone_number} not found.")
        
    def add_birthday(self, birthday_str: str) -> None:
        self.birthday = Birthday(birthday_str)

    def add_email(self, email_str: str) -> None:
        self.email = Email(email_str)

    def add_address(self, address_str: str) -> None:
        self.address = Address(address_str)
        
    def add_birthday(self, date_str: str):
        """Adds or updates a contact's birthday."""
        self.birthday = Birthday(date_str)

    def show_birthday(self) -> str:
        """Returns the birthday as a string or message if not set."""
        if not self.birthday or not self.birthday.value:
            return f"No birthday set for {self.name}."
        return f"{self.name}'s birthday: {self.birthday}"

class AddressBook(UserDict[str, Record]):
    def add_record(self, record: Record):
        self.data[self._key(str(record.name))] = record

    def find(self, name: str) -> Optional[Record]:
        return self.data.get(self._key(name))

    def delete(self, name: str):
        standardized_name = self._key(name)
        if standardized_name in self.data:
            del self.data[standardized_name]
        else:
            raise ContactNotFoundError(f"Contact {name} not found.")
        
    def _key(self, name: str) -> str:
        return name.strip().casefold()
            
    def get_upcoming_birthdays(self, days: int = 7) -> str:
        """Returns list of contacts with birthdays within given days, handling weekend rollovers."""
        today = date.today()
        upcoming = []

        for record in self.data.values():
            if not record.birthday or not record.birthday.value:
                continue

            bday = record.birthday.value.replace(year=today.year)
            # If birthday already passed this year, take next year's
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
        """Finds contacts by matching query against all fields."""
        query_lower = query.lower()
        results = []

        for record in self.data.values():
            fields = [
                record.name.value.lower(),
                " ".join(p.value for p in record.phones).lower(),
            ]

            if record.email and record.email.value:
                fields.append(str(record.email.value).lower())
            if record.address and record.address.value:
                fields.append(str(record.address.value).lower())

            if any(query_lower in field for field in fields):
                results.append(record)

        return results

    

class Note:
    """Stores the content and has a unique title for identification"""
    def __init__(self, title: str, content: str, tags: list[str] | set[str] = None ):
        if not title:
            raise ValueError("Note title cannot be empty")
        self.__title = title.lower() # store the title (ID)
        self.content = content.lower()
        # Store tags as a set to avoid duplicates
        self.tags = set()
        if tags:
            for tag in tags:
                cleaned_tag = tag.strip().lower()
                if not cleaned_tag or " " in cleaned_tag:
                    raise InvalidTagFormatError(f"Invalid tag: '{tag}'. Tags cannot be empty or contain spaces.")
                self.tags.add(cleaned_tag)


    def __str__(self):
        tags_str = ",".join(sorted(self.tags)) if self.tags else "No tags"
        return f"Note: '{self.title}'\nContent: {self.content}...\nTags: {tags_str}"
    
    @property
    def title(self):
        return self.__title
    
    def add_tag(self, tag:str):
        cleaned_tag = tag.strip().lower()
        if not cleaned_tag or " " in cleaned_tag:
            raise InvalidTagFormatError(f"Invalid tag: '{tag}'. Tags cannot be empty or contain spaces.")
        self.tags.add(cleaned_tag)

    def remove_tag(self, tag:str):
        cleaned_tag = tag.strip().lower()
        if cleaned_tag in self.tags:
            self.tags.remove(cleaned_tag)

    

class NoteBook(UserDict):
    def add_note(self, note: Note):
        self.data[str(note.title).lower()] = note

    def find_note_by_id(self, title: str):
        return self.data.get(title.lower())

    def edit_note_text(self, title: str, new_text:str):
        standardized_title = title.lower()
        note = self.data.get(standardized_title)
        if note:
            note.content = new_text.lower()
        else:
            raise NoteNotFoundError(f"Note {title} not found.")

    def delete_note(self, title: str):
        standardized_title = title.lower()
        if standardized_title in self.data:
            del self.data[standardized_title]
        else:
            raise NoteNotFoundError(f"Note {title} not found.")

