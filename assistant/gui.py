import customtkinter as ctk
from tkinter import messagebox
from .models import AddressBook, NoteBook, Record, Note, DataValidationError
from .serialization_utils import load_data, save_data
from .gui_backend import (
    add_contact_gui, add_note_gui, edit_contact_gui, edit_note_gui,
    search_notes_by_tag_gui, delete_contact_gui, delete_note_gui
)

# --- Pop-up Windows ---

class AddContactWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.app = master

        self.title("Add New Contact")
        self.geometry("400x300")
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(1, weight=1)

        self.name_label = ctk.CTkLabel(self, text="Name*")
        self.name_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Enter contact's name")
        self.name_entry.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

        self.phone_label = ctk.CTkLabel(self, text="Phone*")
        self.phone_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.phone_entry = ctk.CTkEntry(self, placeholder_text="Enter 10-digit phone number")
        self.phone_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        self.email_label = ctk.CTkLabel(self, text="Email")
        self.email_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.email_entry = ctk.CTkEntry(self, placeholder_text="(Optional)")
        self.email_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        self.address_label = ctk.CTkLabel(self, text="Address")
        self.address_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.address_entry = ctk.CTkEntry(self, placeholder_text="(Optional)")
        self.address_entry.grid(row=3, column=1, padx=20, pady=10, sticky="ew")

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        self.save_button = ctk.CTkButton(self.button_frame, text="Save", command=self.save_action)
        self.save_button.pack(side="left", padx=10)
        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancel", command=self.destroy)
        self.cancel_button.pack(side="left", padx=10)

    def save_action(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name or not phone:
            messagebox.showerror("Error", "Name and Phone are required fields.", parent=self)
            return

        try:
            add_contact_gui(name, phone, email, address, self.app.book)
            self.app.populate_contact_list()
            self.app.show_contact_details(name)
            self.destroy()
        except DataValidationError as e:
            messagebox.showerror("Validation Error", str(e), parent=self)

class EditContactWindow(AddContactWindow):
    def __init__(self, master, record: Record):
        super().__init__(master)
        self.record = record
        self.title("Edit Contact")

        self.name_entry.insert(0, record.name.value)
        self.name_entry.configure(state="disabled")
        
        self.original_phone = record.phones[0].value if record.phones else ""
        self.phone_entry.insert(0, self.original_phone)
        
        if record.email:
            self.email_entry.insert(0, record.email.value)
        if record.address:
            self.address_entry.insert(0, record.address.value)

    def save_action(self):
        new_phone = self.phone_entry.get().strip()
        new_email = self.email_entry.get().strip()
        new_address = self.address_entry.get().strip()

        try:
            edit_contact_gui(self.record, new_phone, new_email, new_address)
            self.app.populate_contact_list()
            self.app.show_contact_details(self.record.name.value)
            self.destroy()
        except DataValidationError as e:
            messagebox.showerror("Validation Error", str(e), parent=self)


class AddNoteWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.app = master

        self.title("Add New Note")
        self.geometry("500x400")
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_entry = ctk.CTkEntry(self, placeholder_text="Enter note title*")
        self.title_entry.pack(padx=20, pady=(10,5), fill="x")

        self.content_textbox = ctk.CTkTextbox(self, wrap="word")
        self.content_textbox.pack(padx=20, pady=5, fill="both", expand=True)

        self.tags_entry = ctk.CTkEntry(self, placeholder_text="Enter tags separated by spaces (e.g., #work #urgent)")
        self.tags_entry.pack(padx=20, pady=(5,10), fill="x")

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10)

        self.save_button = ctk.CTkButton(self.button_frame, text="Save", command=self.save_action)
        self.save_button.pack(side="left", padx=10)
        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancel", command=self.destroy)
        self.cancel_button.pack(side="left", padx=10)

    def save_action(self):
        title = self.title_entry.get().strip()
        content = self.content_textbox.get("1.0", "end-1c").strip()
        tags = self.tags_entry.get().strip().split()

        if not title or not content:
            messagebox.showerror("Error", "Title and Content are required.", parent=self)
            return

        try:
            add_note_gui(title, content, tags, self.app.notes)
            self.app.populate_note_list()
            self.app.show_note_details(title)
            self.destroy()
        except DataValidationError as e:
            messagebox.showerror("Validation Error", str(e), parent=self)

class EditNoteWindow(AddNoteWindow):
    def __init__(self, master, note: Note):
        super().__init__(master)
        self.note = note
        self.title("Edit Note")

        self.title_entry.insert(0, note.title)
        self.title_entry.configure(state="disabled")
        self.content_textbox.insert("1.0", note.content)
        if note.tags:
            self.tags_entry.insert(0, " ".join(f"#{t}" for t in note.tags))

    def save_action(self):
        new_content = self.content_textbox.get("1.0", "end-1c").strip()
        new_tags = self.tags_entry.get().strip().split()

        if not new_content:
            messagebox.showerror("Error", "Content cannot be empty.", parent=self)
            return

        try:
            edit_note_gui(self.note, new_content, new_tags)
            self.app.populate_note_list()
            self.app.show_note_details(self.note.title)
            self.destroy()
        except DataValidationError as e:
            messagebox.showerror("Validation Error", str(e), parent=self)


# --- Main Application ---

class App(ctk.CTk):
    def __init__(self, book: AddressBook, notes: NoteBook):
        super().__init__()

        self.book = book
        self.notes = notes
        self.selected_contact_name = None
        self.selected_note_title = None
        self.contact_buttons = {}
        self.note_buttons = {}

        self.title("Personal Assistant")
        self.geometry("800x600")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.tab_view = ctk.CTkTabview(self, anchor="w")
        self.tab_view.pack(padx=20, pady=10, fill="both", expand=True)

        self.contacts_tab = self.tab_view.add("Contacts")
        self.notes_tab = self.tab_view.add("Notes")

        self.setup_contacts_tab()
        self.setup_notes_tab()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_contacts_tab(self):
        self.contacts_tab.grid_columnconfigure(0, weight=1)
        self.contacts_tab.grid_columnconfigure(1, weight=2)
        self.contacts_tab.grid_rowconfigure(1, weight=1)

        self.contact_search_bar = ctk.CTkEntry(self.contacts_tab, placeholder_text="Search contacts...")
        self.contact_search_bar.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="ew")
        self.contact_search_bar.bind("<KeyRelease>", self.search_contacts_event)

        self.contact_list_frame = ctk.CTkScrollableFrame(self.contacts_tab, label_text="Contacts")
        self.contact_list_frame.grid(row=1, column=0, padx=10, pady=(5,10), sticky="nsew")

        self.contact_details = ctk.CTkTextbox(self.contacts_tab, wrap="word")
        self.contact_details.grid(row=1, column=1, padx=10, pady=(5,10), sticky="nsew")
        
        self.contact_actions = ctk.CTkFrame(self.contacts_tab)
        self.contact_actions.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        
        self.add_contact_btn = ctk.CTkButton(self.contact_actions, text="Add Contact", command=self.open_add_contact_window)
        self.add_contact_btn.pack(side="left", padx=10)
        self.edit_contact_btn = ctk.CTkButton(self.contact_actions, text="Edit Contact", command=self.open_edit_contact_window)
        self.edit_contact_btn.pack(side="left", padx=10)
        self.delete_contact_btn = ctk.CTkButton(self.contact_actions, text="Delete Contact", command=self.delete_selected_contact)
        self.delete_contact_btn.pack(side="left", padx=10)

        self.populate_contact_list()

    def setup_notes_tab(self):
        self.notes_tab.grid_columnconfigure(0, weight=1)
        self.notes_tab.grid_columnconfigure(1, weight=2)
        self.notes_tab.grid_rowconfigure(1, weight=1)

        self.note_search_bar = ctk.CTkEntry(self.notes_tab, placeholder_text="Search notes by tag...")
        self.note_search_bar.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="ew")
        self.note_search_bar.bind("<KeyRelease>", self.search_notes_event)

        self.note_list_frame = ctk.CTkScrollableFrame(self.notes_tab, label_text="Notes")
        self.note_list_frame.grid(row=1, column=0, padx=10, pady=(5,10), sticky="nsew")

        self.note_details = ctk.CTkTextbox(self.notes_tab, wrap="word")
        self.note_details.grid(row=1, column=1, padx=10, pady=(5,10), sticky="nsew")

        self.note_actions = ctk.CTkFrame(self.notes_tab)
        self.note_actions.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        self.add_note_btn = ctk.CTkButton(self.note_actions, text="Add Note", command=self.open_add_note_window)
        self.add_note_btn.pack(side="left", padx=10)
        self.edit_note_btn = ctk.CTkButton(self.note_actions, text="Edit Note", command=self.open_edit_note_window)
        self.edit_note_btn.pack(side="left", padx=10)
        self.delete_note_btn = ctk.CTkButton(self.note_actions, text="Delete Note", command=self.delete_selected_note)
        self.delete_note_btn.pack(side="left", padx=10)

        self.populate_note_list()

    def search_contacts_event(self, event=None):
        query = self.contact_search_bar.get().strip()
        if not query:
            self.populate_contact_list()
        else:
            results = self.book.search_contacts(query)
            self.populate_contact_list(results)

    def search_notes_event(self, event=None):
        query = self.note_search_bar.get().strip()
        if not query:
            self.populate_note_list()
        else:
            results = search_notes_by_tag_gui(query, self.notes)
            self.populate_note_list(results)

    def open_add_contact_window(self):
        AddContactWindow(self)

    def open_edit_contact_window(self):
        if not self.selected_contact_name:
            messagebox.showinfo("Info", "Please select a contact to edit.", parent=self)
            return
        record = self.book.find(self.selected_contact_name)
        if record:
            EditContactWindow(self, record)

    def open_add_note_window(self):
        AddNoteWindow(self)

    def open_edit_note_window(self):
        if not self.selected_note_title:
            messagebox.showinfo("Info", "Please select a note to edit.", parent=self)
            return
        note = self.notes.find_note_by_id(self.selected_note_title)
        if note:
            EditNoteWindow(self, note)

    def delete_selected_contact(self):
        if not self.selected_contact_name:
            messagebox.showinfo("Info", "Please select a contact to delete.", parent=self)
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {self.selected_contact_name}?", parent=self):
            try:
                delete_contact_gui(self.selected_contact_name, self.book)
                self.selected_contact_name = None
                self.populate_contact_list()
                self.contact_details.configure(state="normal")
                self.contact_details.delete("1.0", "end")
                self.contact_details.configure(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)

    def delete_selected_note(self):
        if not self.selected_note_title:
            messagebox.showinfo("Info", "Please select a note to delete.", parent=self)
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{self.selected_note_title}'?", parent=self):
            try:
                delete_note_gui(self.selected_note_title, self.notes)
                self.selected_note_title = None
                self.populate_note_list()
                self.note_details.configure(state="normal")
                self.note_details.delete("1.0", "end")
                self.note_details.configure(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)

    def populate_contact_list(self, records=None):
        for widget in self.contact_list_frame.winfo_children():
            widget.destroy()
        self.contact_buttons.clear()

        contact_records = records if records is not None else self.book.data.values()
        sorted_records = sorted(contact_records, key=lambda r: r.name.value)
        
        if not sorted_records:
            label = ctk.CTkLabel(self.contact_list_frame, text="No contacts found.")
            label.pack(pady=10, padx=10)
            return

        for record in sorted_records:
            name = record.name.value
            button = ctk.CTkButton(self.contact_list_frame, text=name,
                                   command=lambda n=name: self.show_contact_details(n),
                                   fg_color="transparent", anchor="w")
            button.pack(fill="x", padx=5, pady=2)
            self.contact_buttons[name] = button
        
        if self.selected_contact_name and self.selected_contact_name in self.contact_buttons:
            self.show_contact_details(self.selected_contact_name)


    def show_contact_details(self, name: str):
        self.selected_contact_name = name
        
        for btn_name, btn_widget in self.contact_buttons.items():
            if btn_name == name:
                btn_widget.configure(fg_color="#3B8ED0")
            else:
                btn_widget.configure(fg_color="transparent")

        record = self.book.find(name)
        if not record:
            self.contact_details.configure(state="normal")
            self.contact_details.delete("1.0", "end")
            self.contact_details.configure(state="disabled")
            return

        self.contact_details.configure(state="normal")
        self.contact_details.delete("1.0", "end")
        self.contact_details.insert("1.0", str(record))
        self.contact_details.configure(state="disabled")

    def populate_note_list(self, notes=None):
        for widget in self.note_list_frame.winfo_children():
            widget.destroy()
        self.note_buttons.clear()

        note_records = notes if notes is not None else self.notes.data.values()
        sorted_notes = sorted(note_records, key=lambda n: n.title)

        if not sorted_notes:
            label = ctk.CTkLabel(self.note_list_frame, text="No notes found.")
            label.pack(pady=10, padx=10)
            return

        for note in sorted_notes:
            title = note.title
            button = ctk.CTkButton(self.note_list_frame, text=title,
                                   command=lambda t=title: self.show_note_details(t),
                                   fg_color="transparent", anchor="w")
            button.pack(fill="x", padx=5, pady=2)
            self.note_buttons[title] = button
        
        if self.selected_note_title and self.selected_note_title in self.note_buttons:
            self.show_note_details(self.selected_note_title)

    def show_note_details(self, title: str):
        self.selected_note_title = title

        for btn_title, btn_widget in self.note_buttons.items():
            if btn_title == title:
                btn_widget.configure(fg_color="#3B8ED0")
            else:
                btn_widget.configure(fg_color="transparent")

        note = self.notes.find_note_by_id(title)
        if not note:
            self.note_details.configure(state="normal")
            self.note_details.delete("1.0", "end")
            self.note_details.configure(state="disabled")
            return
        
        tags_str = ", ".join(f"#{t}" for t in sorted(note.tags)) if note.tags else "No tags"
        full_text = f"Title: {note.title}\n\n"
        full_text += f"Tags: {tags_str}\n"
        full_text += "--------------------"
        full_text += note.content

        self.note_details.configure(state="normal")
        self.note_details.delete("1.0", "end")
        self.note_details.insert("1.0", full_text)
        self.note_details.configure(state="disabled")

    def on_closing(self):
        save_data(self.book, self.notes)
        self.destroy()

def main():
    book, notes = load_data()
    app = App(book=book, notes=notes)
    app.mainloop()

if __name__ == "__main__":
    main()