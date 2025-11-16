import sys
import os
from typing import List, Callable
from datetime import datetime, timedelta

# Adjust path to import the assistant package from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all necessary components from the main application files
from assistant.main import (
    add_contact, change_contact, show_contact_detail, show_all, delete_contact,
    add_birthday, show_birthday, birthdays, search_command,
    add_note, edit_note, delete_note, show_all_notes,
    add_note_tag, remove_note_tag, find_notes_by_tag, show_notes_sorted,
    hello_command
)
from assistant.models import AddressBook, NoteBook
from assistant.serialization_utils import load_data, save_data, FILENAME

# --- DEMO HELPER FUNCTIONS ---

def run_test(function: Callable, args: List, context_obj):
    """
    Simulates calling a command handler, prints the context, and handles exceptions.
    """
    # Determine the command name for printing
    command_name = function.__name__ if function else "N/A"
    
    # Prepare arguments for display
    args_str = " ".join(map(str, args)) if args else ""
    
    print("-" * 50)
    print(f"EXECUTING: {command_name} {args_str}")

    try:
        # Pass the correct context object (AddressBook or NoteBook) to the function
        if command_name in ["hello_command"]:
             result = function()
        elif command_name in ["show_all", "show_all_notes"]:
             result = function(context_obj)
        elif hasattr(context_obj, 'data') and isinstance(context_obj.data, dict):
            if "note" in command_name:
                result = function(args, context_obj)
            else:
                result = function(args, context_obj)
        else:
            result = function(args, context_obj)


        print(f"STATUS: SUCCESS")
        if result:
            print(f"OUTPUT:\n{result}")

    except Exception as e:
        # Catching all exceptions and printing them as expected or unexpected
        print(f"STATUS: CAUGHT EXCEPTION -> {type(e).__name__}: {e}")

def setup_clean_environment():
    """Ensures no data file exists before the demo starts."""
    if os.path.exists(FILENAME):
        os.remove(FILENAME)
        print(f"Clean slate: Removed existing '{FILENAME}'.")
    else:
        print(f"Clean slate: No existing '{FILENAME}' found.")

# --- MAIN DEMO EXECUTION ---

def main_demo():
    print("=" * 60)
    print("STARTING COMPREHENSIVE END-TO-END DEMO SCRIPT")
    print("=" * 60)

    # --- 0. INITIAL SETUP ---
    setup_clean_environment()
    book = AddressBook()
    notes = NoteBook()
    
    # --- 1. INITIAL STATE & EMPTY BOOK/NOTES TESTS ---
    print("\n\n--- 1. TESTING ON A CLEAN, EMPTY STATE ---")
    run_test(hello_command, [], None)
    run_test(show_all, [], book)
    run_test(show_all_notes, [], notes)
    run_test(show_contact_detail, ["NonExistent"], book)
    run_test(birthdays, [], book)
    run_test(search_command, ["query"], book)

    # --- 2. INPUT VALIDATION AND ERROR HANDLING ---
    print("\n\n--- 2. TESTING INPUT VALIDATION AND ERROR HANDLING ---")
    # Contact errors
    run_test(add_contact, ["TestUser"], book) # Missing phone
    run_test(add_contact, ["TestUser", "123"], book) # Invalid phone
    run_test(add_contact, ["TestUser", "1234567890", "bad-email"], book) # Invalid email
    run_test(change_contact, ["TestUser", "1234567890", "0987654321"], book) # Contact not found
    # Birthday errors
    run_test(add_birthday, ["TestUser", "99.99.2023"], book) # Invalid date format
    run_test(add_birthday, ["TestUser", "01.01.2099"], book) # Future date
    # Note errors
    run_test(add_note, ["TestNote"], notes) # Missing content
    run_test(add_note_tag, ["TestNote", "#invalid tag"], notes) # Invalid tag format
    run_test(edit_note, ["NonExistentNote", "new content"], notes) # Note not found

    # --- 3. CONTACT MANAGEMENT ---
    print("\n\n--- 3. TESTING CONTACT CRUD AND SEARCH ---")
    run_test(add_contact, ["JohnDoe", "1112223333", "john.doe@example.com", "123 Main St"], book)
    run_test(add_contact, ["JaneSmith", "4445556666"], book)
    run_test(add_contact, ["JohnDoe", "7778889999"], book) # Add second phone to John
    run_test(show_all, [], book)
    run_test(show_contact_detail, ["JohnDoe"], book)
    run_test(show_contact_detail, ["johndoe"], book) # Test case-insensitivity
    run_test(change_contact, ["JohnDoe", "1112223333", "1110001110"], book)
    run_test(show_contact_detail, ["JohnDoe"], book) # Verify change
    run_test(search_command, ["jane"], book) # Search by name
    run_test(search_command, ["000"], book) # Search by phone
    run_test(search_command, ["example.com"], book) # Search by email
    run_test(delete_contact, ["JaneSmith"], book)
    run_test(show_all, [], book) # Verify deletion

    # --- 4. BIRTHDAY FEATURES ---
    print("\n\n--- 4. TESTING BIRTHDAY FUNCTIONALITY ---")
    # Find the next Saturday to test weekend rollover
    today = datetime.now()
    days_until_saturday = (5 - today.weekday() + 7) % 7
    saturday_birthday = today + timedelta(days=days_until_saturday)
    saturday_str = saturday_birthday.strftime("%d.%m.%Y")
    
    run_test(add_contact, ["SaturdayPerson", "5551112222"], book)
    run_test(add_birthday, ["JohnDoe", "15.11.1990"], book)
    run_test(add_birthday, ["SaturdayPerson", saturday_str], book)
    run_test(show_birthday, ["JohnDoe"], book)
    print("\n--- Checking upcoming birthdays (should include SaturdayPerson on Monday) ---")
    run_test(birthdays, ["10"], book) # Check within 10 days

    # --- 5. NOTE MANAGEMENT ---
    print("\n\n--- 5. TESTING NOTE CRUD, TAGS, AND SORTING ---")
    run_test(add_note, ["Meeting", "Discuss Q4 results.", "#work", "#urgent"], notes)
    run_test(add_note, ["ShoppingList", "Milk, bread, eggs.", "#personal", "#home"], notes)
    run_test(add_note, ["Ideas", "Brainstorm new project ideas.", "#work"], notes)
    run_test(add_note, ["Meeting", "UPDATED: Q4 results discussion is postponed.", "#work", "#cancelled"], notes) # Overwrite
    run_test(show_all_notes, [], notes)
    run_test(edit_note, ["ShoppingList", "Milk, bread, eggs, and cheese."], notes)
    run_test(add_note_tag, ["Ideas", "#brainstorm"], notes)
    run_test(remove_note_tag, ["Meeting", "urgent"], notes)
    run_test(show_all_notes, [], notes) # Verify changes
    run_test(find_notes_by_tag, ["work"], notes)
    run_test(find_notes_by_tag, ["personal"], notes)
    # Add notes with same tag count to test secondary sort by title
    run_test(add_note, ["Zebra", "Note about zebras", "#animals"], notes)
    run_test(add_note, ["Apple", "Note about apples", "#food"], notes)
    print("\n--- Sorting notes by tag count (Zebra and Apple have 1, should be sorted by title) ---")
    run_test(show_notes_sorted, ["tags"], notes)
    print("\n--- Sorting notes by title ---")
    run_test(show_notes_sorted, ["title"], notes)
    run_test(delete_note, ["Ideas"], notes)
    run_test(show_all_notes, [], notes) # Verify deletion

    # --- 6. PERSISTENCE ---
    print("\n\n--- 6. TESTING DATA PERSISTENCE (SAVE AND LOAD) ---")
    print("--- State before saving ---")
    run_test(show_all, [], book)
    run_test(show_all_notes, [], notes)
    
    # Save data
    save_data(book, notes)
    print(f"\nData saved to '{FILENAME}'.")
    
    # Clear current objects
    book_after_save = AddressBook()
    notes_after_save = NoteBook()
    print("In-memory objects cleared.")
    print("--- State after clearing memory (should be empty) ---")
    run_test(show_all, [], book_after_save)
    run_test(show_all_notes, [], notes_after_save)

    # Load data
    book_after_load, notes_after_load = load_data()
    print(f"\nData loaded from '{FILENAME}'.")
    print("--- State after loading from file (should be restored) ---")
    run_test(show_all, [], book_after_load)
    run_test(show_all_notes, [], notes_after_load)

    # Verify counts
    print("\n--- Final Verification ---")
    print(f"Contacts in memory: {len(book_after_load)}")
    print(f"Notes in memory: {len(notes_after_load)}")
    assert len(book_after_load) > 0, "Error: No contacts were loaded."
    assert len(notes_after_load) > 0, "Error: No notes were loaded."
    print("Assertion passed: Data was successfully loaded.")

    print("\n=" * 60)
    print("COMPREHENSIVE DEMO COMPLETE.")
    print("=" * 60)

if __name__ == "__main__":
    main_demo()
