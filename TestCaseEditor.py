import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinter.scrolledtext import ScrolledText
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class TestApplication:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Test Case Writer")
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        self.test_title = ""
        self.test_items = []
        self.selected_item_index = None
        
        self.tests_directory = "tests"
        if not os.path.exists(self.tests_directory):
            os.makedirs(self.tests_directory)
            
        self.create_main_menu()
        
    def create_main_menu(self):
        for widget in self.window.winfo_children():
            widget.destroy()
            
        self.window.title("Test Case Writer - Main Menu")
        
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(main_frame, text="Test Case Writer", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=10)
        
        ttk.Button(main_frame, text="Create New Test", command=self.start_new_test).grid(row=1, column=0, pady=5)
        
        tests_frame = ttk.LabelFrame(main_frame, text="Past Tests", padding="5")
        tests_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        tests_frame.grid_rowconfigure(0, weight=1)
        tests_frame.grid_columnconfigure(0, weight=1)
        
        list_frame = ttk.Frame(tests_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        self.test_listbox = tk.Listbox(list_frame)
        self.test_listbox.grid(row=0, column=0, sticky="nsew")
        self.test_listbox.bind('<Double-Button-1>', self.open_test_from_list)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.test_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.test_listbox.configure(yscrollcommand=scrollbar.set)
        
        buttons_frame = ttk.Frame(tests_frame)
        buttons_frame.grid(row=1, column=0, pady=5)
        
        ttk.Button(buttons_frame, text="Open Selected Test", command=self.open_test_button).grid(row=0, column=0, padx=5)
        ttk.Button(buttons_frame, text="Delete Selected Test", command=self.delete_test).grid(row=0, column=1, padx=5)
        
        self.list_tests()

    def list_tests(self):
        self.test_listbox.delete(0, tk.END)
        for file in sorted(os.listdir(self.tests_directory)):
            if file.endswith('.json'):
                with open(os.path.join(self.tests_directory, file), 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                    self.test_listbox.insert(tk.END, test_data["title"])

    def open_test_from_list(self, event):
            if self.test_listbox.curselection():
                self.open_test_button()

    def open_test_button(self):
        if not self.test_listbox.curselection():
            messagebox.showwarning("Warning", "Please select a test!")
            return
            
        selected_test = self.test_listbox.get(self.test_listbox.curselection())
        file_name = os.path.join(self.tests_directory, f"{selected_test}.json")
        
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            
            self.test_title = test_data["title"]
            self.test_items = test_data["items"]
            self.create_test_window()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while opening the test: {str(e)}")

    def delete_test(self):
        if not self.test_listbox.curselection():
            messagebox.showwarning("Warning", "Please select a test!")
            return
            
        selected_test = self.test_listbox.get(self.test_listbox.curselection())
        if messagebox.askyesno("Confirmation", f"Are you sure you want to delete the test {selected_test}?"):
            file_name = os.path.join(self.tests_directory, f"{selected_test}.json")
            try:
                os.remove(file_name)
                self.list_tests()
                messagebox.showinfo("Success", "Test deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while deleting the test: {str(e)}")

    def start_new_test(self):
        self.test_title = ""
        self.test_items = []
        self.create_title_window()

    def create_title_window(self):
        # Clear existing widgets
        for widget in self.window.winfo_children():
            widget.destroy()
            
        self.window.title("Create Test - Title")
        
        title_frame = ttk.Frame(self.window, padding="20")
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(title_frame, text="Enter Test Title:", 
                 font=("Arial", 12)).grid(row=0, column=0, pady=10)
        
        self.title_entry = ttk.Entry(title_frame, width=40)
        self.title_entry.grid(row=1, column=0, pady=10)
        
        button_frame = ttk.Frame(title_frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(button_frame, text="Return to Main Menu", 
                  command=self.create_main_menu).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Continue", 
                  command=self.create_test_window).grid(row=0, column=1, padx=5)

    def create_test_window(self):
        if not self.test_title and not self.title_entry.get().strip():
            messagebox.showerror("Error", "Please enter a test title!")
            return
                    
        if not self.test_title:
            self.test_title = self.title_entry.get()

        # Clear existing widgets
        for widget in self.window.winfo_children():
            widget.destroy()

        # Main frame
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Add click event to the main frame
        self.main_frame.bind('<Button-1>', self.frame_click)
        
        # Title
        ttk.Label(self.main_frame, text=f"Test: {self.test_title}", 
            font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        
        # Left panel
        left_panel = ttk.LabelFrame(self.main_frame, text="Test Item", padding="5")
        left_panel.grid(row=1, column=0, sticky="nsew", padx=5)
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.bind('<Button-1>', self.frame_click)
        
        # Add click event to all labels
        for label in left_panel.winfo_children():
            if isinstance(label, ttk.Label):
                label.bind('<Button-1>', self.frame_click)
                
        # Item entry
        ttk.Label(left_panel, text="Item:").grid(row=0, column=0, sticky="w", pady=2)
        self.item_entry = ttk.Entry(left_panel)
        self.item_entry.grid(row=1, column=0, sticky="ew", pady=2)
        
        # Description
        ttk.Label(left_panel, text="Description:").grid(row=2, column=0, sticky="w", pady=2)
        self.description_entry = ScrolledText(left_panel, height=4)
        self.description_entry.grid(row=3, column=0, sticky="ew", pady=2)
        
        # Steps
        ttk.Label(left_panel, text="Steps:").grid(row=4, column=0, sticky="w", pady=2)
        self.steps_entry = ScrolledText(left_panel, height=4)
        self.steps_entry.grid(row=5, column=0, sticky="ew", pady=2)
        
        # Input
        ttk.Label(left_panel, text="Input:").grid(row=6, column=0, sticky="w", pady=2)
        self.input_entry = ScrolledText(left_panel, height=4)
        self.input_entry.grid(row=7, column=0, sticky="ew", pady=2)

        # Output
        ttk.Label(left_panel, text="Output:").grid(row=8, column=0, sticky="w", pady=2)
        self.output_entry = ScrolledText(left_panel, height=4)
        self.output_entry.grid(row=9, column=0, sticky="ew", pady=2)
        
        # Item buttons
        item_buttons = ttk.Frame(left_panel)
        item_buttons.grid(row=10, column=0, pady=5)
        item_buttons.bind('<Button-1>', self.frame_click)
        
        self.add_button = ttk.Button(item_buttons, text="Add Item", command=self.add_item)
        self.add_button.grid(row=0, column=0, padx=2)
        
        self.update_button = ttk.Button(item_buttons, text="Update Item", 
                                        command=self.update_item, state='disabled')
        self.update_button.grid(row=0, column=1, padx=2)
        
        # Right panel (Item List)
        right_panel = ttk.LabelFrame(self.main_frame, text="Test Items", padding="5")
        right_panel.grid(row=1, column=1, sticky="nsew", padx=5)
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.bind('<Button-1>', self.frame_click)
        
        # Item list
        self.item_listbox = tk.Listbox(right_panel)
        self.item_listbox.grid(row=0, column=0, sticky="nsew", pady=5)
        self.item_listbox.bind('<<ListboxSelect>>', self.select_item)
        
        # Item list scrollbar
        list_scrollbar = ttk.Scrollbar(right_panel, orient="vertical", 
                                    command=self.item_listbox.yview)
        list_scrollbar.grid(row=0, column=1, sticky="ns")
        self.item_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        # Item control buttons
        control_frame = ttk.Frame(right_panel)
        control_frame.grid(row=1, column=0, columnspan=2, pady=5)
        control_frame.bind('<Button-1>', self.frame_click)
        
        ttk.Button(control_frame, text="Move Up", 
                command=self.move_up).grid(row=0, column=0, padx=2)
        ttk.Button(control_frame, text="Move Down", 
                command=self.move_down).grid(row=0, column=1, padx=2)
        ttk.Button(control_frame, text="Delete", 
                command=self.delete_item).grid(row=0, column=2, padx=2)
        
        # Bottom buttons
        bottom_buttons = ttk.Frame(self.main_frame)
        bottom_buttons.grid(row=2, column=0, columnspan=2, pady=5)
        bottom_buttons.bind('<Button-1>', self.frame_click)
        
        ttk.Button(bottom_buttons, text="Save and Return to Main Menu", 
                command=self.save_and_return).grid(row=0, column=0, padx=5)
        ttk.Button(bottom_buttons, text="Return to Main Menu", 
                command=self.ask_return_to_main_menu).grid(row=0, column=1, padx=5)
        
        ttk.Button(bottom_buttons, text="Share", 
            command=self.share_test).grid(row=0, column=2, padx=5)
        self.update_item_list()
        

    def frame_click(self, event):

        widget = event.widget
        
        if not isinstance(widget, (ttk.Entry, ScrolledText)):
            self.secili_madde_index = None
            self.update_button.config(state='disabled')
            self.add_button.config(state='normal')
            self.item_listbox.selection_clear(0, tk.END)

    def select_item(self, event):
        if not self.item_listbox.curselection():
            return
            
        self.selected_item_index = self.item_listbox.curselection()[0]
        item = self.test_items[self.selected_item_index]
        
        # Fill the form fields
        self.clear_fields()
        self.item_entry.insert(0, item['item'])
        self.description_entry.insert("1.0", item['description'])
        self.steps_entry.insert("1.0", item['steps'])
        self.input_entry.insert("1.0", item['input'])
        self.output_entry.insert("1.0", item['output'])
        
        # Enable update button
        self.update_button.config(state='normal')
        self.add_button.config(state='disabled')

    def update_item(self):
        if self.selected_item_index is None:
            return
            
        new_item = {
            "item": self.item_entry.get(),
            "description": self.description_entry.get("1.0", tk.END).strip(),
            "steps": self.steps_entry.get("1.0", tk.END).strip(),
            "input": self.input_entry.get("1.0", tk.END).strip(),
            "output": self.output_entry.get("1.0", tk.END).strip()
        }
        
        self.test_items[self.selected_item_index] = new_item
        self.update_item_list()
        self.clear_fields()
        self.selected_item_index = None
        self.update_button.config(state='disabled')
        self.add_button.config(state='normal')

    def move_up(self):
        if not self.item_listbox.curselection() or self.item_listbox.curselection()[0] == 0:
            return
            
        idx = self.item_listbox.curselection()[0]
        self.test_items[idx], self.test_items[idx-1] = \
            self.test_items[idx-1], self.test_items[idx]
        self.update_item_list()
        self.item_listbox.selection_set(idx-1)

    def move_down(self):
        if not self.item_listbox.curselection() or \
           self.item_listbox.curselection()[0] == len(self.test_items) - 1:
            return
            
        idx = self.item_listbox.curselection()[0]
        self.test_items[idx], self.test_items[idx+1] = \
            self.test_items[idx+1], self.test_items[idx]
        self.update_item_list()
        self.item_listbox.selection_set(idx+1)

    def delete_item(self):
        if not self.item_listbox.curselection():
            return
            
        if messagebox.askyesno("Confirmation", "Are you sure you want to delete the selected item?"):
            idx = self.item_listbox.curselection()[0]
            del self.test_items[idx]
            self.update_item_list()
            self.clear_fields()
            self.selected_item_index = None
            self.update_button.config(state='disabled')
            self.add_button.config(state='normal')

    def update_item_list(self):
        self.item_listbox.delete(0, tk.END)
        for i, item in enumerate(self.test_items, 1):
            self.item_listbox.insert(tk.END, f"{i}. {item['item']}")

    def add_item(self):
        if not self.item_entry.get().strip():
            messagebox.showerror("Error", "Please enter a test item!")
            return
            
        new_item = {
            "item": self.item_entry.get(),
            "description": self.description_entry.get("1.0", tk.END).strip(),
            "steps": self.steps_entry.get("1.0", tk.END).strip(),
            "input": self.input_entry.get("1.0", tk.END).strip(),
            "output": self.output_entry.get("1.0", tk.END).strip()
        }
        
        self.test_items.append(new_item)
        self.update_item_list()
        self.clear_fields()
        
    def clear_fields(self):
        self.item_entry.delete(0, tk.END)
        self.description_entry.delete("1.0", tk.END)
        self.steps_entry.delete("1.0", tk.END)
        self.input_entry.delete("1.0", tk.END)
        self.output_entry.delete("1.0", tk.END)
        
    def save_and_return(self):
        if not self.test_items:
            messagebox.showerror("Error", "Please add at least one test item!")
            return
            
        test_data = {
            "title": self.test_title,
            "items": self.test_items,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        file_name = os.path.join(self.tests_directory, f"{self.test_title}.json")
        
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Success", "Test saved successfully!")
            self.create_main_menu()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the test: {str(e)}")


    def confirm_return_to_main_menu(self):
        if messagebox.askyesno("Confirmation", "Unsaved changes will be lost. Do you want to continue?"):
            self.create_main_menu()

    def start(self):
        self.window.mainloop()

    def create_item_window(self):
        try:
            self.bottom_buttons_frame = ttk.Frame(self.right_frame)
            self.bottom_buttons_frame.grid(row=14, column=0, pady=10, sticky="ew")
            
            self.main_menu_btn = ttk.Button(self.bottom_buttons_frame, text="Return to Main Menu", command=self.confirm_return_to_main_menu)
            self.main_menu_btn.pack(side=tk.LEFT, padx=5)
            
            self.share_btn = ttk.Button(self.bottom_buttons_frame, text="Share")
            self.share_btn.pack(side=tk.LEFT, padx=10)
            
        except Exception as e:
            print(f"Error creating item window: {str(e)}")

    def share_test(self):
        try:
            if not self.test_items:
                messagebox.showerror("Error", "No test items available for sharing!")
                return
                
            recipient_email = simpledialog.askstring("Email Address", "Please enter the recipient's email address:")
            
            if not recipient_email:
                return
                
            if '@' not in recipient_email or '.' not in recipient_email:
                messagebox.showerror("Error", "Invalid email address!")
                return
                
            test_data = {
                'title': self.test_title,
                'test_items': self.test_items,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            json_data = json.dumps(test_data, indent=4, ensure_ascii=False)
            
            self.send_email(recipient_email, json_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while sharing the test: {str(e)}")

    def send_email(self, recipient_email, json_data):
        try:
            sender_email = "" # email address
            email_password = "" # one-time password
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = "Test Sharing"
            
            body = f"""
            Hello,
            
            Please find the test data for {self.test_title} attached.
            
            Best regards.
            """
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            json_attachment = MIMEApplication(json_data.encode('utf-8'))
            json_attachment.add_header('Content-Disposition', 'attachment', filename=f'{self.test_title}_test_data.json')
            msg.attach(json_attachment)
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()  # Secure connection
                server.login(sender_email, email_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())

            messagebox.showinfo("Success", f"Test data has been sent to {recipient_email}!")
            
        except smtplib.SMTPAuthenticationError:
            messagebox.showerror("Error", 
                "Authentication failed for email sending! \n"
                "Please check your email address and application password.")
        
        except smtplib.SMTPException as e:
            messagebox.showerror("Error", 
                f"An SMTP error occurred during email sending: {str(e)}")
            
        except Exception as e:
            messagebox.showerror("Error", 
                f"An unexpected error occurred during email sending: {str(e)}")
            
    def start(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = TestApplication()
    app.start()
