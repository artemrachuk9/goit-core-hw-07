from collections import UserDict
from datetime import datetime, timedelta
import re


class Field:
    def __init__(self, value):
        self._value = None
        self.value = value  

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

    @Field.value.setter
    def value(self, val):
        if re.fullmatch(r"\d{10}", val):
            self._value = val
        else:
            raise ValueError("Phone number must be 10 digits.")


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)

    @Field.value.setter
    def value(self, val):
        try:
            datetime.strptime(val, "%d.%m.%Y")
            self._value = val
        except ValueError:
            raise ValueError("Birthday must be in format DD.MM.YYYY.")


class Record:
    def __init__(self, name: Name):
        self.name = name
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: Phone):
        self.phones.append(phone)

    def remove_phone(self, phone: Phone):
        self.phones = [p for p in self.phones if p.value != phone.value]

    def edit_phone(self, old_phone: Phone, new_phone: Phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone.value:
                self.phones[i] = new_phone
                return True
        return False

    def add_birthday(self, birthday: Birthday):
        self.birthday = birthday

    def __str__(self):
        phones = ", ".join(p.value for p in self.phones)
        birthday = self.birthday.value if self.birthday else "N/A"
        return f"Name: {self.name.value}, Phones: {phones}, Birthday: {birthday}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def get_upcoming_birthdays(self):
        today = datetime.today()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                bday = datetime.strptime(record.birthday.value, "%d.%m.%Y")
                bday_this_year = bday.replace(year=today.year)
                if 0 <= (bday_this_year - today).days < 7:
                    upcoming.append({
                        "name": record.name.value,
                        "birthday": bday_this_year.strftime("%d.%m.%Y")
                    })
        return upcoming



def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Invalid input. Please check your command."
    return wrapper



@input_error
def add_contact(args, book):
    name = Name(args[0])
    phone = Phone(args[1])
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return f"Contact {name.value} added."

@input_error
def add_birthday(args, book):
    name = args[0]
    birthday = Birthday(args[1])
    record = book.data.get(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        raise KeyError

@input_error
def show_contact(args, book):
    name = args[0]
    record = book.data.get(name)
    if record:
        return str(record)
    else:
        raise KeyError

@input_error
def show_birthdays(_, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays this week."
    return "\n".join(f"{b['name']}: {b['birthday']}" for b in upcoming)

@input_error
def edit_phone(args, book):
    name, old, new = args
    record = book.data.get(name)
    if record and record.edit_phone(Phone(old), Phone(new)):
        return f"Phone updated for {name}."
    else:
        return "Phone not found."

@input_error
def remove_phone(args, book):
    name, phone = args
    record = book.data.get(name)
    if record:
        record.remove_phone(Phone(phone))
        return f"Phone removed for {name}."
    else:
        raise KeyError



def parse_command(command):
    parts = command.strip().split()
    cmd = parts[0].lower()
    args = parts[1:]
    return cmd, args



def main():
    book = AddressBook()
    commands = {
        "add": add_contact,
        "birthday": add_birthday,
        "show": show_contact,
        "birthdays": show_birthdays,
        "edit": edit_phone,
        "remove": remove_phone,
        "exit": lambda args, book: "Goodbye!",
        "close": lambda args, book: "Goodbye!"
    }

    while True:
        user_input = input(">>> ")
        cmd, args = parse_command(user_input)
        if cmd in ["exit", "close"]:
            print("Goodbye!")
            break
        handler = commands.get(cmd)
        if handler:
            print(handler(args, book))
        else:
            print("Unknown command. Try again.")


if __name__ == "__main__":
    main()

"""
add Artem 0987654321
add-birthday Artem 10.08.1995
phone Artem
change Artem 0987654321 1234567890
show-birthday Artem
birthdays
all
exit
"""


