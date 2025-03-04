# -*- coding: utf-8 -*-
"""EventPalMilestone1

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EWqngdgfgI2WgJHJUo_H9fw3qXt9_3fa
"""

!pip install bcrypt

import sqlite3
import uuid
import bcrypt

class User:
    def __init__(self, username, first_name, last_name, email, password):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

    def login(self, email, password):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            if bcrypt.checkpw(password.encode('utf-8'), user_data[4]):
                print("Login successful!")
                global current_user, logged_in
                current_user = user_data[0]
                logged_in = True
                return True
            else:
                print("Invalid password. Please try again.")
                return False
        else:
            print("You don't have an account with this email. Please register.")
            return False

    def logout(self):
        global logged_in, current_user
        logged_in = False
        current_user = None
        print("Logged out successfully.")

class Event:
    def __init__(self, event_name, date, time, description, organizer):
        self.event_name = event_name
        self.date = date
        self.time = time
        self.description = description
        self.organizer = organizer

    def has_events(self, organizer_name):
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM events WHERE organizer = ?", (organizer_name,))
        event_count = cursor.fetchone()[0]

        conn.close()

        return event_count > 0

    def create(self):
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                description TEXT,
                organizer TEXT NOT NULL
            )
        ''')

        cursor.execute("INSERT INTO events (event_name, date, time, description, organizer) VALUES (?, ?, ?, ?, ?)",
                       (self.event_name, self.date, self.time, self.description, self.organizer))
        conn.commit()
        conn.close()

        print("Event created successfully!")

    def view(self, organizer_name=None):
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()

        if organizer_name:
            cursor.execute("SELECT * FROM events WHERE organizer = ?", (organizer_name,))
        else:
            cursor.execute("SELECT * FROM events")

        events = cursor.fetchall()
        conn.close()

        if not events:
            print("You have no events created.")
            return

        if events:
            for event in events:
                print(f"Event ID: {event[0]}, Event Name: {event[1]}, Organizer: {event[5]}, Date: {event[2]}, Time: {event[3]}, Description: {event[4]}")
        else:
            print("No events found.")

        while True:
            action = input("Do you want to edit an event (E), delete an event (D), or go back (B)? ").upper()
            if action == 'E':
                self.edit(current_user)
            elif action == 'D':
                event_id_to_delete = input("Enter the ID of the event you want to delete: ")
                self.delete(current_user, event_id_to_delete)
            elif action == 'B':
                break
            else:
                print("Invalid choice.")

    def edit(self, organizer_name):
        event_id = input("Enter the ID of the event you want to edit: ")

        event_name = input("Enter new event name: ")
        date = input("Enter new date (YYYY-MM-DD): ")
        time = input("Enter new time (HH:MM): ")
        description = input("Enter new description: ")

        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE events
            SET event_name = ?, date = ?, time = ?, description = ?
            WHERE event_id = ? AND organizer = ?
        """, (event_name, date, time, description, event_id, organizer_name))

        conn.commit()
        conn.close()

        print("Event updated successfully!")

    def delete(self, organizer_name, event_id):
        confirm = input(f"Are you sure you want to delete event with ID '{event_id}'? (Y/N): ").upper()
        if confirm == 'Y':
            conn = sqlite3.connect('events.db')
            cursor = conn.cursor()

            cursor.execute("DELETE FROM events WHERE event_id = ? AND organizer = ?", (event_id, organizer_name))

            conn.commit()
            conn.close()

            print("Event deleted successfully!")
        else:
            print("Deletion canceled.")


def register_user(username, first_name, last_name, email, password):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT UNIQUE NOT NULL,
                first_name TEXT,
                last_name TEXT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("INSERT INTO users (username, first_name, last_name, email, password) VALUES (?, ?, ?, ?, ?)",
                           (username, first_name, last_name, email, hashed_password))
        conn.commit()
        print("Registration successful!")

    except sqlite3.IntegrityError as e:
            print(f"Error: {e}")
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def manage_events(user_type):
    if user_type == 'O':
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                description TEXT,
                organizer TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

        while True:
            action = input("Do you want to view your events (V), create a new event (C), or exit (X)? ").upper()
            if action == 'V':
                conn = sqlite3.connect('events.db')
                cursor = conn.cursor()
                cursor.execute("SELECT event_id, event_name FROM events WHERE organizer = ?", (current_user,))
                user_events = cursor.fetchall()
                conn.close()

                if user_events:
                    Event(None, None, None, None, None).view(current_user)
                else:
                    print("You have no events created.")

            elif action == 'C':
                event_name = input("Enter event name: ")
                date = input("Enter date (MM-DD-YYYY): ")
                time = input("Enter time (HH:MM): ")
                description = input("Enter description: ")
                event = Event(event_name, date, time, description, current_user)
                event.create()
            elif action == 'X':
                break
            else:
                print("Invalid choice.")


logged_in = False
current_user = None

while True:
    if not logged_in:
        choice = input("Do you want to login (L) or register (R)? ").upper()

        if choice == 'L':
            email = input("Enter your email: ")
            password = input("Enter your password: ")

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT UNIQUE NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            conn.commit()
            conn.close()

            user = User(None, None, None, email, password)
            if user.login(email, password):
                user_type = input("Organizer (O) or Attendee (A) interface? ").upper()
                manage_events(user_type)
                logout_choice = input("Do you want to logout (Y/N)? ").upper()
                if logout_choice == 'Y':
                    user.logout()

        elif choice == 'R':
            username = input("Enter your username: ")
            first_name = input("Enter your first name: ")
            last_name = input("Enter your last name: ")
            email = input("Enter your email: ")
            password = input("Enter your password: ")
            register_user(username, first_name, last_name, email, password)

        else:
            print("Invalid choice. Please enter L or R.")

    else:
        print("You are already logged in.")
        while True:
            user_type = input("Organizer (O) or Attendee (A) interface? ").upper()
            manage_events(user_type)
        if user_type in ('O', 'A'):
            manage_events(user_type)
        else:
            print("Invalid user type.")

        logout_choice = input("Do you want to logout (Y/N)? ").upper()
        if logout_choice == 'Y':
            user = User(None, None, None, None, None)
            user.logout()
            break