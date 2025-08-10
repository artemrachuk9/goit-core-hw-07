from collections import UserDict
from datetime import datetime, timedelta

def input_error(f):
    def w(*a): 
        try: return f(*a)
        except (KeyError, IndexError): return "Invalid input."
        except ValueError as e: return str(e)
    return w

class Field: 
    def __init__(self, v): self.value = v
    @property
    def value(self): return self._v
    @value.setter
    def value(self, v): self._v = v

class Name(Field): pass

class Phone(Field):
    def __init__(self, v):
        if not (v.isdigit() and len(v) == 10): raise ValueError("Phone must be 10 digits.")
        super().__init__(v)

class Birthday(Field):
    def __init__(self, v):
        try: self.date = datetime.strptime(v, "%d.%m.%Y").date()
        except: raise ValueError("Use format DD.MM.YYYY")
        super().__init__(v)

class Record:
    def __init__(self, name): self.name = Name(name); self.phones = []; self.birthday = None
    def add_phone(self, p): self.phones.append(Phone(p))
    def change_phone(self, o, n):
        for i, ph in enumerate(self.phones):
            if ph.value == o: self.phones[i] = Phone(n); return
        raise ValueError("Old phone not found.")
    def add_birthday(self, d): self.birthday = Birthday(d)
    def get_birthday(self): return self.birthday.value if self.birthday else "No birthday"
    def __str__(self):
        ph = ", ".join(p.value for p in self.phones) or "No phones"
        return f"{self.name.value}: {ph}; Birthday: {self.get_birthday()}"

class AddressBook(UserDict):
    def add_record(self, r): self.data[r.name.value] = r
    def find(self, n): return self.data.get(n)
    def get_upcoming_birthdays(self):
        t = datetime.today().date()
        out = []
        for r in self.data.values():
            if r.birthday:
                b = r.birthday.date.replace(year=t.year)
                if b < t: b = b.replace(year=t.year + 1)
                if 0 <= (b - t).days <= 7:
                    if b.weekday() >= 5: b += timedelta(days=7 - b.weekday())
                    out.append(f"{r.name.value}: {b.strftime('%d.%m.%Y')}")
        return out

@input_error
def add(args, book):
    n, p = args
    r = book.find(n) or Record(n); book.add_record(r)
    r.add_phone(p)
    return "Contact added." if len(r.phones) == 1 else "Contact updated."

@input_error
def change(args, book): book.find(args[0]).change_phone(args[1], args[2]); return "Phone updated."
@input_error
def phone(args, book): return ", ".join(p.value for p in book.find(args[0]).phones)
@input_error
def all(args, book): return "\n".join(str(r) for r in book.values()) or "Empty book."
@input_error
def add_birthday(args, book): book.find(args[0]).add_birthday(args[1]); return "Birthday added."
@input_error
def show_birthday(args, book): return book.find(args[0]).get_birthday()
@input_error
def birthdays(args, book): return "\n".join(book.get_upcoming_birthdays()) or "No upcoming birthdays."

def main():
    book = AddressBook()
    cmds = {
        "add": add, "change": change, "phone": phone, "all": all,
        "add-birthday": add_birthday, "show-birthday": show_birthday, "birthdays": birthdays
    }
    print("Welcome to the assistant bot!")
    while True:
        u = input("Enter command: ").strip().split()
        if not u: continue
        cmd, args = u[0], u[1:]
        if cmd in ["exit", "close"]: print("Good bye!"); break
        elif cmd == "hello": print("How can I help you?")
        elif cmd in cmds: print(cmds[cmd](args, book))
        else: print("Invalid command.")

if __name__ == "__main__": main()


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

