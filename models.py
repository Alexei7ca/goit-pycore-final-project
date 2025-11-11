from collections import UserDict
import re
from typing import List, Optional
from datetime import datetime, date

# --- Custom Exceptions (Required by main.py @input_error) ---
class InvalidPhoneFormatError(Exception):
    pass
class InvalidNameFormatError(Exception):
    pass
class ContactNotFoundError(Exception):
    pass
class PhoneNotFoundError(Exception):
    pass
class InvalidEmailFormatError(Exception):
    pass
class InvalidBirthdayFormatError(Exception):
    pass
# Placeholder for fields not yet implemented
class InvalidAddressFormatError(Exception):
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
                raise ValueError("⚠️ Birthday cannot be in the future.")
        
        return parsed_date

    def __str__(self):
        return self.value.strftime("%d.%m.%Y") if self.value else ""
    

class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.birthday: Optional[Birthday] = None
        self.email: Optional[Email] = None  # Placeholder
        self.address: Optional[Field] = None # Placeholder

    def __str__(self):
        phones_str = '; '.join(str(p) for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones_str}{birthday_str}"

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

    # Placeholder methods required by main.py
    def add_email(self, email_str: str) -> None:
        self.email = Email(email_str)

    def add_address(self, address_str: str) -> None:
        self.address = Field(address_str)


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
            
    # Minimal placeholder for Task 3 dependency
    def get_upcoming_birthdays(self):
        return "Upcoming birthdays feature pending Task 3 completion."