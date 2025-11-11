from collections import UserDict
from typing import List, Optional
from datetime import datetime, date, timedelta

# --- Custom Exceptions (Required by main.py @input_error) ---
class InvalidPhoneFormatError(Exception):
    pass
class ContactNotFoundError(Exception):
    pass
class PhoneNotFoundError(Exception):
    pass
class InvalidEmailFormatError(Exception):
    pass
# Placeholder for fields not yet implemented
class InvalidAddressFormatError(Exception):
    pass
class NoteNotFoundError(Exception):
    pass

# --- Core Field Classes (Minimal working placeholders) ---
class Field:
    def __init__(self, value):
        self._value = value
    def __str__(self):
        return str(self._value)
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, new_value):
        self._value = new_value

class Name(Field):
    pass
class Phone(Field):
    # Minimal setter to avoid errors, Task 1 will add validation
    @Field.value.setter
    def value(self, new_value: str):
        self._value = new_value
class Email(Field):
    # Minimal setter to avoid errors, Task 1 will add validation
    def add_email(self, new_value):
        self._value = new_value
class Birthday(Field):
    def __init__(self, value=None):
        if value:
            try:
                self.value = datetime.strptime(value, "%d.%m.%Y").date()
            except ValueError:
                raise ValueError("Invalid date format. Use DD.MM.YYYY")
        else:
            self._value = None
    def __str__(self):
        return self.value.strftime("%d.%m.%Y") if self.value else ""

# --- Record Class (Minimal working placeholders) ---
class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.birthday: Optional[Birthday] = None
        self.email = None  # Placeholder
        self.address = None # Placeholder

    def __str__(self):
        phones_str = '; '.join(str(p) for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones_str}{birthday_str}"

    def add_phone(self, phone_number: str):
        # Placeholder: Assume validation in Phone class
        self.phones.append(Phone(phone_number))

    def edit_phone(self, old_phone: str, new_phone: str):
        # Placeholder: Minimal functionality (assumes find_phone exists)
        for i, phone in enumerate(self.phones):
            if str(phone) == old_phone:
                self.phones[i].value = new_phone
                return
        raise PhoneNotFoundError(f"Phone {old_phone} not found.")

    # Placeholder methods required by main.py
    def add_email(self, email_str: str):
        self.email = Email(email_str)
    def add_address(self, address_str: str):
        self.address = Field(address_str)
        
    def add_birthday(self, date_str: str):
        """Adds or updates a contact's birthday."""
        self.birthday = Birthday(date_str)

    def show_birthday(self) -> str:
        """Returns the birthday as a string or message if not set."""
        if not self.birthday or not self.birthday.value:
            return f"No birthday set for {self.name}."
        return f"{self.name}'s birthday: {self.birthday}"


# --- AddressBook Class (Minimal working placeholders) ---
class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[str(record.name).lower()] = record

    def find(self, name: str) -> Optional[Record]:
        return self.data.get(name.lower())

    def delete(self, name: str):
        standardized_name = name.lower()
        if standardized_name in self.data:
            del self.data[standardized_name]
        else:
            raise ContactNotFoundError(f"Contact {name} not found.")
            
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
    def __init__(self, title: str, content: str ):
        if not title:
            raise ValueError("Note title cannot be empty")
        self.__title = title # store the title (ID)
        self.content = content.lower()

    def __str__(self):
        return f"Note: '{self.title}'\nContent: {self.content}..."
    
    @property
    def title(self):
        return self.__title
    

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

