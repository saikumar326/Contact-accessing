from flask import Flask, request, jsonify
from threading import Thread
import tkinter as tk
from tkinter import scrolledtext
import os

# Flask application setup
app = Flask(__name__)

# Initialize global lists for contacts and call logs
received_contacts = []
received_call_logs = []

# Function to save data to text file
def save_data_to_text_file(file_path, data):
    try:
        with open(file_path, "w") as file:
            for item in data:
                file.write(str(item) + "\n")
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")

# Flask route to receive data
@app.route('/api/data', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()
        contacts = data.get('contacts', [])
        call_logs = data.get('callLogs', [])
        message = data.get('message', "No message provided")

        # Save received data to global lists
        received_contacts.extend(contacts)
        received_call_logs.extend(call_logs)

        log_entry = {
            "contacts": contacts,
            "callLogs": call_logs,
            "message": message,
        }

        print(f"Data received: {log_entry}")

        # Send success response
        return jsonify({"message": "Data received successfully"}), 200
    except Exception as e:
        print(f"Error processing data: {e}")
        return jsonify({"message": "Error processing data", "error": str(e)}), 500

# Function to run Flask server in a separate thread
def run_server():
    app.run(host='0.0.0.0', port=5000, use_reloader=False)

# GUI setup
class FlaskGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Server")  # Set the window title
        self.master.geometry("800x600")

        # Set the window icon
        self.master.iconbitmap('D:\servericon.png')  # Provide your own .ico file path here

        # Storage directory input
        self.storage_directory_label = tk.Label(master, text="Enter storage directory:")
        self.storage_directory_label.pack(pady=10)

        self.storage_directory_entry = tk.Entry(master, width=50)
        self.storage_directory_entry.pack(pady=10)

        # Frames for contacts and call logs
        self.contacts_frame = tk.Frame(master)
        self.contacts_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.call_logs_frame = tk.Frame(master)
        self.call_logs_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Contacts section
        tk.Label(self.contacts_frame, text="Contacts", font=("Arial", 14)).pack(pady=5)
        self.contacts_text = scrolledtext.ScrolledText(self.contacts_frame, wrap=tk.WORD, width=40, height=30)
        self.contacts_text.pack(fill=tk.BOTH, expand=True)

        # Call Logs section
        tk.Label(self.call_logs_frame, text="Call Logs", font=("Arial", 14)).pack(pady=5)
        self.call_logs_text = scrolledtext.ScrolledText(self.call_logs_frame, wrap=tk.WORD, width=40, height=30)
        self.call_logs_text.pack(fill=tk.BOTH, expand=True)

        # Start, Stop, and Save buttons at the bottom
        self.buttons_frame = tk.Frame(master)
        self.buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.start_button = tk.Button(self.buttons_frame, text="Start Server", command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(self.buttons_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.buttons_frame, text="Save Data", command=self.save_data)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Server thread placeholder
        self.server_thread = None
        self.server_running = False

    def start_server(self):
        if not self.server_running:
            self.server_thread = Thread(target=run_server, daemon=True)
            self.server_thread.start()
            self.server_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

    def stop_server(self):
        if self.server_running:
            # Flask doesn't have an in-built way to stop the server gracefully
            self.server_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def save_data(self):
        # Get storage directory from input field
        storage_directory = self.storage_directory_entry.get()

        # Validate directory
        if not os.path.exists(storage_directory):
            os.makedirs(storage_directory)

        # Save data to text files in the specified directory
        contacts_file = os.path.join(storage_directory, "contacts.txt")
        call_logs_file = os.path.join(storage_directory, "call_logs.txt")

        save_data_to_text_file(contacts_file, received_contacts)
        save_data_to_text_file(call_logs_file, received_call_logs)

        print(f"Data saved to {storage_directory}.")
        
    def update_received_data(self):
        # Update contacts
        self.contacts_text.delete(1.0, tk.END)
        for contact in received_contacts:
            self.contacts_text.insert(tk.END, str(contact) + "\n\n")

        # Update call logs
        self.call_logs_text.delete(1.0, tk.END)
        for call_log in received_call_logs:
            self.call_logs_text.insert(tk.END, str(call_log) + "\n\n")

        # Call this method again after 1 second
        self.master.after(1000, self.update_received_data)

# Main function
def main():
    root = tk.Tk()
    gui = FlaskGUI(root)
    gui.update_received_data()
    root.mainloop()

if __name__ == "__main__":
    main()
