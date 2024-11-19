import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import pyttsx3

# Connect to the SQLite database
conn = sqlite3.connect('notepad.db')
cursor = conn.cursor()

# Create the notes table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS notepad (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    password TEXT,
    hidden INTEGER DEFAULT 0 
)
''')
conn.commit()

def load_notes():
    # Load only non-hidden and non-password-protected notes at startup
    cursor.execute('SELECT * FROM notepad WHERE hidden=0 AND (password IS NULL OR password="")')
    rows = cursor.fetchall()
    for row in rows:
        title = row[1]
        content = row[2]
        note_content = tk.Text(notebook, width=80, height=20)
        note_content.insert(tk.END, content)
        notebook.add(note_content, text=title)

def add_note():
    def save_note():
        title = title_entry.get()
        content = content_entry.get("1.0", tk.END)
        password = password_entry.get()
        hidden = hidden_var.get()

        # Save the note to the database
        cursor.execute('INSERT INTO notepad (title, content, password, hidden) VALUES (?, ?, ?, ?)', (title, content, password, hidden))
        conn.commit()

        # Add the note to the notebook only if it is not hidden
        if hidden == 0:
            note_content = tk.Text(notebook, width=80, height=20)
            note_content.insert(tk.END, content)
            notebook.add(note_content, text=title)

        # Close the new note window
        new_note_window.destroy()

    # Code to create new note window...
    # (Keep the existing code for creating and positioning widgets)
    new_note_window = tk.Toplevel(root)
    new_note_window.title("New Note")

    title_label = ttk.Label(new_note_window, text="Title:")
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="W")

    title_entry = ttk.Entry(new_note_window, width=80)
    title_entry.grid(row=0, column=1, padx=10, pady=10)

    content_label = ttk.Label(new_note_window, text="Content:")
    content_label.grid(row=1, column=0, padx=10, pady=10, sticky="W")

    content_entry = tk.Text(new_note_window, width=80, height=10)
    content_entry.grid(row=1, column=1, padx=10, pady=10)

    password_label = ttk.Label(new_note_window, text="Password:")
    password_label.grid(row=2, column=0, padx=10, pady=10, sticky="W")

    password_entry = ttk.Entry(new_note_window, width=30, show='*')
    password_entry.grid(row=2, column=1, padx=10, pady=10)

    hidden_var = tk.IntVar()
    hidden_checkbox = ttk.Checkbutton(new_note_window, text="Hide Note", variable=hidden_var)
    hidden_checkbox.grid(row=3, columnspan=2, padx=10, pady=10)

    save_button = ttk.Button(new_note_window, text="Save", command=save_note)
    save_button.grid(row=4, columnspan=2, padx=10, pady=10)

def show_hidden_notes():
    password = simpledialog.askstring("Show Hidden Note", "Enter the password for the hidden note:")
    if password is not None:
        # Hide all current notes before showing the hidden note
        for tab_id in notebook.tabs():
            notebook.hide(tab_id)
        
        # Check for the hidden note with the correct password
        cursor.execute('SELECT * FROM notepad WHERE password=? AND hidden=1', (password,))
        row = cursor.fetchone()
        if row:
            title = row[1]
            content = row[2]
            note_content = tk.Text(notebook, width=80, height=20)
            note_content.insert(tk.END, content)
            notebook.add(note_content, text=title)
            notebook.select(note_content)
        else:
            messagebox.showerror("Error", "Incorrect password or no hidden note found with this password.")


def delete_note():
    current_tab = notebook.index(notebook.select())
    note_title = notebook.tab(current_tab, "text")

    confirm = messagebox.askyesno("Delete Note", f"Are you sure you want to delete {note_title}?")

    if confirm:
        notebook.forget(current_tab)
        cursor.execute('DELETE FROM notepad WHERE title=?', (note_title,))
        conn.commit()

def convert_text_to_speech():
    current_tab = notebook.index(notebook.select())
    note_title = notebook.tab(current_tab, "text")
    cursor.execute('SELECT content FROM notepad WHERE title=?', (note_title,))
    content = cursor.fetchone()[0]
    
    engine = pyttsx3.init() #initializes
    engine.say(content) #converts fetched content to speech
    engine.runAndWait() #Runs the text-to-speech engine to speak the content aloud.

def edit_note():
    current_tab = notebook.index(notebook.select())
    note_title = notebook.tab(current_tab, "text")
    cursor.execute('SELECT * FROM notepad WHERE title=?', (note_title,))
    row = cursor.fetchone()
    
    def save_edit():
        new_title = title_entry.get()
        new_content = content_entry.get("1.0", tk.END)
        new_password = password_entry.get()
        new_hidden = hidden_var.get()

        cursor.execute('UPDATE notepad SET title=?, content=?, password=?, hidden=? WHERE id=?', (new_title, new_content, new_password, new_hidden, row[0]))
        conn.commit()

        # Remove the old tab and add the updated note
        notebook.forget(current_tab)
        note_content = tk.Text(notebook, width=80, height=20)
        note_content.insert(tk.END, new_content)
        notebook.add(note_content, text=new_title)
        new_note_window.destroy()

    new_note_window = tk.Toplevel(root)
    new_note_window.title("Edit Note")

    title_label = ttk.Label(new_note_window, text="Title:")
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="W")

    title_entry = ttk.Entry(new_note_window, width=80)
    title_entry.grid(row=0, column=1, padx=10, pady=10)
    title_entry.insert(tk.END, row[1])

    content_label = ttk.Label(new_note_window, text="Content:")
    content_label.grid(row=1, column=0, padx=10, pady=10, sticky="W")

    content_entry = tk.Text(new_note_window, width=80, height=10)
    content_entry.grid(row=1, column=1, padx=10, pady=10)
    content_entry.insert(tk.END, row[2])

    password_label = ttk.Label(new_note_window, text="Password:")
    password_label.grid(row=2, column=0, padx=10, pady=10, sticky="W")

    password_entry = ttk.Entry(new_note_window, width=30, show='*')
    password_entry.grid(row=2, column=1, padx=10, pady=10)
    password_entry.insert(tk.END, row[3])

    hidden_var = tk.IntVar()
    hidden_checkbox = ttk.Checkbutton(new_note_window, text="Hide Note", variable=hidden_var)
    hidden_checkbox.grid(row=3, columnspan=2, padx=10, pady=10)
    hidden_checkbox.state(['selected' if row[4] == 1 else '!selected'])

    save_button = ttk.Button(new_note_window, text="Save", command=save_edit)
    save_button.grid(row=4, columnspan=2, padx=10, pady=10)

root = tk.Tk()
root.title("BuildingNote App")
root.geometry("800x500")
root.configure(bg="#f2f2f2")  # Set the main background color

style = ttk.Style() #search the style
style.configure("TNotebook.Tab", font=("TkDefaultFont", 14, "bold"), background="#f2f2f2", foreground="#343a40")  # Set the notebook tab colors

notebook = ttk.Notebook(root, style="TNotebook")
notebook.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Button Styles
button_style = {"font": ("TkDefaultFont", 12, "bold")}
button_colors = {
    "foreground": "green",
    "activeforeground": "white",
    "highlightbackground": "#f2f2f2",  # Set the button highlight color to match the main background
}

new_button = ttk.Button(root, text="New Note", command=add_note, style="info.TButton")
new_button.pack(side=tk.LEFT, padx=10, pady=10)
style.configure("info.TButton", font=("TkDefaultFont", 12, "bold"), foreground="green", activeforeground="white", highlightbackground="#f2f2f2")

voice_button = ttk.Button(root, text="Text to Voice", command=convert_text_to_speech, style="primary.TButton")
voice_button.pack(side=tk.LEFT, padx=10, pady=10)
style.configure("primary.TButton", font=("TkDefaultFont", 12, "bold"), foreground="green", activeforeground="white", highlightbackground="#f2f2f2")

show_hidden_button = ttk.Button(root, text="Show Hidden Notes", command=show_hidden_notes, style="info.TButton")
show_hidden_button.pack(side=tk.LEFT, padx=10, pady=10)
style.configure("info.TButton", font=("TkDefaultFont", 12, "bold"), foreground="green", activeforeground="white", highlightbackground="#f2f2f2")

delete_button = ttk.Button(root, text="Delete", command=delete_note, style="primary.TButton")
delete_button.pack(side=tk.LEFT, padx=10, pady=10)
style.configure("primary.TButton", font=("TkDefaultFont", 12, "bold"), foreground="green", activeforeground="white", highlightbackground="#f2f2f2")

edit_button = ttk.Button(root, text="Edit Note", command=edit_note, style="info.TButton")
edit_button.pack(side=tk.LEFT, padx=10, pady=10)
style.configure("info.TButton", font=("TkDefaultFont", 12, "bold"), foreground="green", activeforeground="white", highlightbackground="#f2f2f2")

load_notes()

root.mainloop()
