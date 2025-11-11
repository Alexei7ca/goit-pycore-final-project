from collections import UserDict
from typing import List, Optional
from datetime import datetime, date

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
            
    # Minimal placeholder for Task 3 dependency
    def get_upcoming_birthdays(self):
        return "Upcoming birthdays feature pending Task 3 completion."