import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
from datetime import datetime
import pymysql
import pandas as pd
from passlib.hash import pbkdf2_sha256
import time
from PIL import Image, ImageTk

# Set appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class StudentManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1500x900+0+0")
        self.root.resizable(False, False)
        
        self.conn = None
        self.cursor = None
        self.current_user = None
        
        # Slider variables
        self.s = "Student Management System"
        self.count = 0
        self.text = ""
        
        # Initialize UI
        self.setup_ui()
        self.show_db_connection_window()
        self.clock()
        self.slider()
        
    def setup_ui(self):
        """Initialize all UI components"""
        # Header with slider and clock
        self.header_frame = ctk.CTkFrame(self.root, height=80)
        self.header_frame.pack(fill="x")
        
        self.sliderLabel = ctk.CTkLabel(self.header_frame, text="", font=("Arial", 24, "bold"))
        self.sliderLabel.pack(side="left", padx=20)
        
        self.datetimeLabel = ctk.CTkLabel(self.header_frame, text="", font=("Arial", 14))
        self.datetimeLabel.pack(side="right", padx=20)
        
        # Left sidebar frame
        self.left_frame = ctk.CTkFrame(self.root, width=300, height=700)
        self.left_frame.place(x=50, y=80)
        
        # Right content frame
        self.right_frame = ctk.CTkFrame(self.root, height=700, width=1050)
        self.right_frame.place(x=380, y=80)
        
        # Setup buttons and tables
        self.setup_sidebar_buttons()
        self.setup_student_table()
        
    def slider(self):
        """Animated text slider for header"""
        if self.count == len(self.s):
            self.count = 0
            self.text = ""
        self.text = self.text + self.s[self.count]
        self.sliderLabel.configure(text=self.text)
        self.count += 1
        self.sliderLabel.after(300, self.slider)
        
    def clock(self):
        """Live clock display"""
        date = time.strftime("%d/%m/%Y")
        currenttime = time.strftime("%H:%M:%S")
        self.datetimeLabel.configure(text=f"Date: {date}\nTime: {currenttime}")
        self.datetimeLabel.after(1000, self.clock)
        
    def setup_sidebar_buttons(self):
        """Create navigation buttons in sidebar"""
        self.buttons = {}
        
        buttons_config = [
            ("Add Student", "add", lambda: self.toplevel_data("Add Student", "ADD STUDENT", self.add_data)),
            ("Search Student", "search", lambda: self.toplevel_data("Search Student", "Search", self.search_data)),
            ("Delete Student", "delete", self.delete_student),
            ("Update Student", "update", lambda: self.toplevel_data("Update Student", "Update", self.update_data)),
            ("Show All Students", "show", self.show_student),
            ("Export Data", "export", self.export_data),
            ("Teacher Tools", "teacher", self.show_teacher_tools),
            ("Parent Portal", "parent", self.show_parent_portal),
            ("Exit", "exit", self.exit_program)
        ]
        
        for text, key, command in buttons_config:
            self.buttons[key] = ctk.CTkButton(
                self.left_frame, 
                text=text, 
                width=200,
                command=command,
                state="disabled" if key not in ["exit"] else "normal"
            )
            self.buttons[key].pack(pady=10)
    
    def setup_student_table(self):
        """Setup the student data table"""
        # Scrollbars
        scroll_x = ttk.Scrollbar(self.right_frame, orient="horizontal")
        scroll_y = ttk.Scrollbar(self.right_frame, orient="vertical")
        
        # Treeview Table
        self.student_table = ttk.Treeview(
            self.right_frame,
            columns=("ID", "Name", "Mobile", "Email", "Address", "Gender", "DOB", "Date", "Time"),
            xscrollcommand=scroll_x.set,
            yscrollcommand=scroll_y.set
        )
        
        # Configure scrollbars
        scroll_x.config(command=self.student_table.xview)
        scroll_y.config(command=self.student_table.yview)
        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")
        
        self.student_table.pack(fill="both", expand=True)
        
        # Table headings
        columns = ["ID", "Name", "Mobile", "Email", "Address", "Gender", "DOB", "Date", "Time"]
        for col in columns:
            self.student_table.heading(col, text=col)
            self.student_table.column(col, width=100, anchor="center")
        
        self.student_table["show"] = "headings"
    
    def show_db_connection_window(self):
        """Show database connection window"""
        self.connectwindow = ctk.CTkToplevel(self.root)
        self.connectwindow.title("DATABASE CONNECTION")
        self.connectwindow.geometry("470x250+730+230")
        self.connectwindow.resizable(False, False)
        self.connectwindow.grab_set()
        
        # Connection fields
        fields = [
            ("Host Name", "host"),
            ("User Name", "user"),
            ("Password", "password")
        ]
        
        self.connection_entries = {}
        for i, (label_text, key) in enumerate(fields):
            label = ctk.CTkLabel(self.connectwindow, text=label_text, font=("Arial", 20, "bold"), text_color="orange")
            label.grid(row=i, column=0, padx=20, pady=10, sticky="w")
            
            entry = ctk.CTkEntry(self.connectwindow, width=200, font=("Arial", 15))
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.connection_entries[key] = entry
        
        # Connect button
        connect_btn = ctk.CTkButton(
            self.connectwindow, 
            text="CONNECT", 
            command=self.connect_database
        )
        connect_btn.grid(row=3, column=0, columnspan=2, pady=20)
    
    def connect_database(self):
        """Connect to MySQL database"""
        try:
            host = self.connection_entries["host"].get()
            user = self.connection_entries["user"].get()
            password = self.connection_entries["password"].get()
            
            # self.conn = pymysql.connect(host='localhost', user='root', password='1111')
            # self.cursor = self.conn.cursor()
            self.conn = pymysql.connect(host=host, user=user, password=password)
            self.cursor = self.conn.cursor()
            
            # Create database and tables
            self._create_database_tables()
            
            messagebox.showinfo("Success", "Database Connected Successfully", parent=self.connectwindow)
            self.connectwindow.destroy()
            
            # Enable all buttons except exit (already enabled)
            for key, button in self.buttons.items():
                if key != "exit":
                    button.configure(state="normal")
                    
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Error: {str(e)}", parent=self.connectwindow)
    
    def _create_database_tables(self):
        """Create all required database tables"""
        # Student table
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS studentmanagementsystem")
        self.cursor.execute("USE studentmanagementsystem")
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                NAME VARCHAR(30),
                MOBILE_NO VARCHAR(10),
                Email VARCHAR(40),
                ADDRESS VARCHAR(150),
                GENDER VARCHAR(20),
                DOB VARCHAR(20),
                date VARCHAR(50),
                time VARCHAR(50)
            )
        """)
        
        # Create all other tables (auth, courses, etc.)
        self._create_auth_tables()
        self._create_course_tables()
        self._create_registration_tables()
        self._create_attendance_tables()
        self._create_gradebook_tables()
        self._create_communication_tables()
        
        self.conn.commit()
    
    def toplevel_data(self, title, button_text, command):
        """Create student data entry form"""
        self.data_window = ctk.CTkToplevel(self.root)
        self.data_window.title(title)
        self.data_window.geometry("500x550")
        self.data_window.resizable(False, False)
        self.data_window.grab_set()
        
        # Form fields
        labels = ["ID", "Name", "Phone", "E-mail", "Address", "Gender", "DOB"]
        self.form_entries = []
        
        for i, label_text in enumerate(labels):
            label = ctk.CTkLabel(self.data_window, text=label_text, font=("Arial", 16))
            label.grid(row=i, column=0, padx=20, pady=10, sticky="w")
            
            entry = ctk.CTkEntry(self.data_window, width=250, font=("Arial", 16))
            entry.grid(row=i, column=1, padx=20, pady=10, sticky="w")
            self.form_entries.append(entry)
        
        # Action button
        action_btn = ctk.CTkButton(
            self.data_window, 
            text=button_text, 
            command=command,
            width=180
        )
        action_btn.grid(row=7, columnspan=2, pady=20)
        
        # For update, pre-fill with selected student data
        if title == "Update Student":
            self._prefill_update_form()
    
    def _prefill_update_form(self):
        """Pre-fill form with selected student data for update"""
        try:
            selected = self.student_table.focus()
            content = self.student_table.item(selected)
            data = content["values"]
            
            if not data:
                messagebox.showerror("Error", "No student selected to update", parent=self.data_window)
                self.data_window.destroy()
                return
            
            for entry, value in zip(self.form_entries, data[:7]):  # Only first 7 fields
                entry.insert(0, value)
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load selected data: {str(e)}", parent=self.data_window)
            self.data_window.destroy()
    
    def add_data(self):
        """Add new student record"""
        # Validate all fields
        if any(entry.get() == "" for entry in self.form_entries):
            messagebox.showerror("Error", "All fields are required", parent=self.data_window)
            return
            
        currentdate = time.strftime("%d/%m/%Y")
        currenttime = time.strftime("%H:%M:%S")
        
        try:
            query = """
                INSERT INTO student 
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = [entry.get() for entry in self.form_entries] + [currentdate, currenttime]
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            result = messagebox.askyesno(
                "Success", 
                "Data added successfully. Clear the form?", 
                parent=self.data_window
            )
            
            if result:
                for entry in self.form_entries:
                    entry.delete(0, 'end')
                    
            self.show_student()
            
        except pymysql.err.IntegrityError:
            messagebox.showerror("Error", "ID already exists", parent=self.data_window)
        except Exception as e:
            messagebox.showerror("Error", f"{e}", parent=self.data_window)
    
    def search_data(self):
        """Search for student records"""
        query = """
            SELECT * FROM student 
            WHERE ID=%s OR NAME=%s OR MOBILE_NO=%s OR
            Email=%s OR ADDRESS=%s OR GENDER=%s OR DOB=%s
        """
        values = [entry.get() for entry in self.form_entries]
        
        self.cursor.execute(query, values)
        rows = self.cursor.fetchall()
        
        self.student_table.delete(*self.student_table.get_children())
        for row in rows:
            self.student_table.insert("", "end", values=row)
    
    def delete_student(self):
        """Delete selected student record"""
        selected = self.student_table.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a student to delete")
            return
            
        content = self.student_table.item(selected)
        content_id = content["values"][0]
        
        confirm = messagebox.askyesno("Confirm Delete", f"Delete ID {content_id}?")
        if not confirm:
            return
            
        try:
            self.cursor.execute("DELETE FROM student WHERE ID=%s", (content_id,))
            self.conn.commit()
            messagebox.showinfo("Deleted", f"Student ID {content_id} deleted.")
            self.show_student()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {str(e)}")
    
    def update_data(self):
        """Update student record"""
        query = """
            UPDATE student SET 
            NAME=%s, MOBILE_NO=%s, Email=%s,
            ADDRESS=%s, GENDER=%s, DOB=%s, 
            date=%s, time=%s 
            WHERE ID=%s
        """
        values = [entry.get() for entry in self.form_entries[1:]]  # Skip ID
        values += [time.strftime("%d/%m/%Y"), time.strftime("%H:%M:%S")]
        values.append(self.form_entries[0].get())  # Add ID for WHERE clause
        
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Updated", f"ID {values[-1]} updated successfully", parent=self.data_window)
            self.data_window.destroy()
            self.show_student()
        except Exception as e:
            messagebox.showerror("Error", f"Update failed: {str(e)}", parent=self.data_window)
    
    def show_student(self):
        """Display all student records"""
        self.cursor.execute("SELECT * FROM student")
        rows = self.cursor.fetchall()
        
        self.student_table.delete(*self.student_table.get_children())
        for row in rows:
            self.student_table.insert("", "end", values=row)
    
    def export_data(self):
        """Export student data to CSV"""
        file = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Student Data"
        )
        if not file:
            return
            
        # Get all data from table
        data = []
        for item in self.student_table.get_children():
            data.append(self.student_table.item(item)["values"])
        
        # Create DataFrame and save
        df = pd.DataFrame(data, columns=[
            "ID", "Name", "Mobile", "Email", "Address", "Gender", "DOB", "Date", "Time"
        ])
        df.to_csv(file, index=False)
        messagebox.showinfo("Success", f"Data exported to {file}")
    
    def show_teacher_tools(self):
        """Show teacher tools window"""
        try:
            tools_window = ctk.CTkToplevel(self.root)
            tools_window.title("Teacher Tools")
            tools_window.geometry("900x800")
            tools_window.resizable(False, False)
            tools_window.grab_set()
            tools_window.focus_force()
        
            # Create CTkTabview 
            tabview = ctk.CTkTabview(tools_window)
            tabview.pack(expand=True, fill="both", padx=10, pady=10)
            
            # Info box
            ctk.CTkLabel( tools_window,
            text="🔧 This module design is complete, but the backend is not optimized yet. \n © yogeshwar_vadla",
            font=("Arial", 16),
            text_color="orange"
            ).pack(pady=20)
            # Add tabs
            tabview.add("Gradebook")
            tabview.add("Attendance")
            tabview.add("Courses")
            
            # Setup each tab
            self.setup_gradebook_tab(tabview.tab("Gradebook"))
            self.setup_attendance_tab(tabview.tab("Attendance"))
            self.setup_course_tab(tabview.tab("Courses"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Teacher Tools: {str(e)}")
    
    # def setup_gradebook_tab(self, frame):
    #     ctk.CTkLabel(frame, text="Add Grade Item", font=("Arial", 18)).pack(pady=10)
    
    #         # Add sample grade items
    #     sample_grades = [
    #         ("Homework", "Week 1", 100, "2024-05-01"),
    #         ("Quiz", "Chapter 1", 50, "2024-05-10"),
    #         ("Exam", "Midterm", 200, "2024-06-15")
    #     ]
        
    #     # Treeview to display grades
    #     grade_tree = ttk.Treeview(frame, columns=("Category", "Item", "Points", "Due Date"), show="headings")
    #     grade_tree.heading("Category", text="Category")
    #     grade_tree.heading("Item", text="Item")
    #     grade_tree.heading("Points", text="Points")
    #     grade_tree.heading("Due Date", text="Due Date")
        
    #     for grade in sample_grades:
    #         grade_tree.insert("", "end", values=grade)
        
    #     grade_tree.pack(expand=True, fill="both", padx=10, pady=10)
        
    #     # Add form controls below
    #     control_frame = ctk.CTkFrame(frame)
    #     control_frame.pack(fill="x", padx=10, pady=10)
        
    #     category_label = ctk.CTkLabel(frame, text="Category:")
    #     category_label.pack()
    #     self.category_entry = ctk.CTkEntry(frame, width=200)  # Store as instance variable
    #     self.category_entry.pack(pady=5)
        
    #     item_label = ctk.CTkLabel(frame, text="Item Name:")
    #     item_label.pack()
    #     item_entry = ctk.CTkEntry(frame, width=200)
    #     item_entry.pack(pady=5)

    #     points_label = ctk.CTkLabel(frame, text="Total Points:")
    #     points_label.pack()
    #     points_entry = ctk.CTkEntry(frame, width=200)
    #     points_entry.pack(pady=5)

    #     def dummy_add_item():
    #         messagebox.showinfo("Gradebook", "Grade item added (dummy)")

        # ctk.CTkButton(frame, text="Add Grade Item", command=dummy_add_item).pack(pady=10)

    def setup_gradebook_tab(self, frame):   # Setup gradebook management tab type 2 design/UI
        # Main container frame
        main_frame = ctk.CTkFrame(frame)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Form frame (top section)
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", padx=5, pady=5)
        
        # Title
        ctk.CTkLabel(form_frame, text="Add Grade Item", font=("Arial", 18)).pack(pady=5)
        
        # Form fields
        fields = [
            ("Category:", "category_entry"),
            ("Item Name:", "item_entry"),
            ("Total Points:", "points_entry")
        ]
        
        for label_text, var_name in fields:
            ctk.CTkLabel(form_frame, text=label_text).pack()
            entry = ctk.CTkEntry(form_frame, width=200)
            entry.pack(pady=2)
            setattr(self, var_name, entry)  # Store as instance variable
        
        # Add button
        ctk.CTkButton(
            form_frame, 
            text="Add Grade Item", 
            command=self.add_grade_item
        ).pack(pady=10)
        
        # Separator
        ctk.CTkLabel(main_frame, text="Current Grade Items", font=("Arial", 16)).pack(pady=5)
        
        # Treeview frame (bottom section)
        tree_frame = ctk.CTkFrame(main_frame)
        tree_frame.pack(expand=True, fill="both", pady=5)
        
        # Treeview with scrollbars
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side="right", fill="y")
        
        self.grade_tree = ttk.Treeview(
            tree_frame,
            columns=("Category", "Item", "Points", "Due Date"),
            show="headings",
            yscrollcommand=tree_scroll.set
        )
        self.grade_tree.pack(expand=True, fill="both")
        tree_scroll.config(command=self.grade_tree.yview)
        
        # Configure columns
        for col in ["Category", "Item", "Points", "Due Date"]:
            self.grade_tree.heading(col, text=col)
            self.grade_tree.column(col, width=120, anchor="center")
        
        # Add sample data
        sample_grades = [
            ("Homework", "Week 1", 100, "2024-05-01"),
            ("Quiz", "Chapter 1", 50, "2024-05-10"),
            ("Exam", "Midterm", 200, "2024-06-15")
        ]
        
        for grade in sample_grades:
            self.grade_tree.insert("", "end", values=grade)
    
    def add_grade_item(self):
        """Add new grade item to the treeview"""
        try:
            category = self.category_entry.get()
            item = self.item_entry.get()
            points = self.points_entry.get()
            
            if not all([category, item, points]):
                messagebox.showwarning("Input Error", "All fields are required")
                return
                
            # Add to treeview
            self.grade_tree.insert("", "end", values=(
                category,
                item,
                points,
                "2024-06-30"  # Default due date
            ))
            
            # Clear entries
            self.category_entry.delete(0, "end")
            self.item_entry.delete(0, "end")
            self.points_entry.delete(0, "end")
            
            messagebox.showinfo("Success", "Grade item added")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")
    
    # def setup_attendance_tab(self, frame):
    #     """Setup attendance management tab"""
    #     ctk.CTkLabel(frame, text="Record Attendance", font=("Arial", 18)).pack(pady=10)
        
    #         # Add sample attendance records
    #     sample_attendance = [
    #         ("CS101", "2024-05-01", "25/30", "John Smith"),
    #         ("MATH202", "2024-05-03", "18/20", "Sarah Johnson"),
    #         ("ENG105", "2024-05-05", "22/25", "Michael Brown")
    #     ]
        
    #     # Treeview for attendance
    #     attendance_tree = ttk.Treeview(frame, columns=("Course", "Date", "Attendance", "Teacher"), show="headings")
    #     attendance_tree.heading("Course", text="Course")
    #     attendance_tree.heading("Date", text="Date")
    #     attendance_tree.heading("Attendance", text="Attendance")
    #     attendance_tree.heading("Teacher", text="Teacher")
        
    #     for record in sample_attendance:
    #         attendance_tree.insert("", "end", values=record)
        
    #     attendance_tree.pack(expand=True, fill="both", padx=10, pady=10)

    #     self.section_id_entry = ctk.CTkEntry(frame, width=200)  # Store as instance variable
    #     self.section_id_entry.pack(pady=5)
        
    #     section_id_label = ctk.CTkLabel(frame, text="Section ID:")
    #     section_id_label.pack()
    #     section_id_entry = ctk.CTkEntry(frame, width=200)
    #     section_id_entry.pack(pady=5)

    #     meeting_date_label = ctk.CTkLabel(frame, text="Date (YYYY-MM-DD):")
    #     meeting_date_label.pack()
    #     meeting_date_entry = ctk.CTkEntry(frame, width=200)
    #     meeting_date_entry.pack(pady=5)

    #     def dummy_record_attendance():
    #         messagebox.showinfo("Attendance", "Class meeting recorded (dummy)")

    #     ctk.CTkButton(frame, text="Record Class", command=dummy_record_attendance).pack(pady=10)
    
    def setup_attendance_tab(self, frame):
        """Setup attendance management tab"""
        # Main container frame
        main_frame = ctk.CTkFrame(frame)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Form frame (top section)
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", padx=5, pady=5)
        
        # Title
        ctk.CTkLabel(form_frame, text="Record Attendance", font=("Arial", 18)).pack(pady=5)
        
        # Form fields
        fields = [
            ("Section ID:", "section_id_entry"),
            ("Date (YYYY-MM-DD):", "meeting_date_entry"),
            ("Attendance Status:", "attendance_status_entry")
        ]
        
        for label_text, var_name in fields:
            ctk.CTkLabel(form_frame, text=label_text).pack()
            entry = ctk.CTkEntry(form_frame, width=200)
            entry.pack(pady=2)
            setattr(self, var_name, entry)  # Store as instance variable
        
        # Record button
        ctk.CTkButton(
            form_frame, 
            text="Record Attendance", 
            command=self.record_attendance
        ).pack(pady=10)
        
        # Separator
        ctk.CTkLabel(main_frame, text="Attendance Records", font=("Arial", 16)).pack(pady=5)
        
        # Treeview frame (bottom section)
        tree_frame = ctk.CTkFrame(main_frame)
        tree_frame.pack(expand=True, fill="both", pady=5)
        
        # Treeview with scrollbars
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side="right", fill="y")
        
        self.attendance_tree = ttk.Treeview(
            tree_frame,
            columns=("Course", "Date", "Status", "Recorded By"),
            show="headings",
            yscrollcommand=tree_scroll.set
        )
        self.attendance_tree.pack(expand=True, fill="both")
        tree_scroll.config(command=self.attendance_tree.yview)
        
        # Configure columns
        for col in ["Course", "Date", "Status", "Recorded By"]:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=120, anchor="center")
        
        # Add sample data
        sample_attendance = [
            ("CS101", "2024-05-01", "Present", "John Smith"),
            ("MATH202", "2024-05-03", "Absent", "Sarah Johnson"),
            ("ENG105", "2024-05-05", "Present", "Michael Brown")
        ]
        
        for record in sample_attendance:
            self.attendance_tree.insert("", "end", values=record)

    def record_attendance(self):
        """Add new attendance record to the treeview"""
        try:
            section_id = self.section_id_entry.get()
            date = self.meeting_date_entry.get()
            status = self.attendance_status_entry.get()
            
            if not all([section_id, date, status]):
                messagebox.showwarning("Input Error", "All fields are required")
                return
                
            # Add to treeview (using section_id as course code for demo)
            self.attendance_tree.insert("", "end", values=(
                f"Section {section_id}",
                date,
                status,
                "Teacher"  # Default value
            ))
            
            # Clear entries
            self.section_id_entry.delete(0, "end")
            self.meeting_date_entry.delete(0, "end")
            self.attendance_status_entry.delete(0, "end")
            
            messagebox.showinfo("Success", "Attendance recorded")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record attendance: {str(e)}")
        
    
    # def setup_course_tab(self, frame):
    #     """Setup course management tab"""
    #     ctk.CTkLabel(frame, text="Add New Course", font=("Arial", 18)).pack(pady=10)
        
    #      # Add sample courses
    #     sample_courses = [
    #         ("CS101", "Introduction to Programming", 3, "Computer Science"),
    #         ("MATH202", "Advanced Calculus", 4, "Mathematics"),
    #         ("ENG105", "Academic Writing", 3, "English")
    #     ]
        
    #     # Treeview for courses
    #     course_tree = ttk.Treeview(frame, columns=("Code", "Title", "Credits", "Department"), show="headings")
    #     course_tree.heading("Code", text="Code")
    #     course_tree.heading("Title", text="Title")
    #     course_tree.heading("Credits", text="Credits")
    #     course_tree.heading("Department", text="Department")
        
    #     for course in sample_courses:
    #         course_tree.insert("", "end", values=course)
        
    #     course_tree.pack(expand=True, fill="both", padx=10, pady=10)
        
    #     self.code_entry = ctk.CTkEntry(frame, width=200)  # Store as instance variable
    #     self.code_entry.pack(pady=5)
        
    #     code_label = ctk.CTkLabel(frame, text="Course Code:")
    #     code_label.pack()
    #     code_entry = ctk.CTkEntry(frame, width=200)
    #     code_entry.pack(pady=5)

    #     title_label = ctk.CTkLabel(frame, text="Course Title:")
    #     title_label.pack()
    #     title_entry = ctk.CTkEntry(frame, width=200)
    #     title_entry.pack(pady=5)

    #     credits_label = ctk.CTkLabel(frame, text="Credits:")
    #     credits_label.pack()
    #     credits_entry = ctk.CTkEntry(frame, width=200)
    #     credits_entry.pack(pady=5)

    #     def dummy_add_course():
    #         messagebox.showinfo("Course", "Course added (dummy)")

    #     ctk.CTkButton(frame, text="Add Course", command=dummy_add_course).pack(pady=10)
    
    def setup_course_tab(self, frame):
        """Setup course management tab"""
        # Main container frame
        main_frame = ctk.CTkFrame(frame)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Form frame (top section)
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", padx=5, pady=5)
        
        # Title
        ctk.CTkLabel(form_frame, text="Add New Course", font=("Arial", 18)).pack(pady=5)
        
        # Form fields
        fields = [
            ("Course Code:", "course_code_entry"),
            ("Course Title:", "course_title_entry"),
            ("Credits:", "course_credits_entry"),
            ("Department:", "course_dept_entry")
        ]
        
        for label_text, var_name in fields:
            ctk.CTkLabel(form_frame, text=label_text).pack()
            entry = ctk.CTkEntry(form_frame, width=200)
            entry.pack(pady=2)
            setattr(self, var_name, entry)  # Store as instance variable
        
        # Add button
        ctk.CTkButton(
            form_frame, 
            text="Add Course", 
            command=self.add_course
        ).pack(pady=10)
        
        # Separator
        ctk.CTkLabel(main_frame, text="Current Courses", font=("Arial", 16)).pack(pady=5)
        
        # Treeview frame (bottom section)
        tree_frame = ctk.CTkFrame(main_frame)
        tree_frame.pack(expand=True, fill="both", pady=5)
        
        # Treeview with scrollbars
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side="right", fill="y")
        
        self.course_tree = ttk.Treeview(
            tree_frame,
            columns=("Code", "Title", "Credits", "Department"),
            show="headings",
            yscrollcommand=tree_scroll.set
        )
        self.course_tree.pack(expand=True, fill="both")
        tree_scroll.config(command=self.course_tree.yview)
        
        # Configure columns
        for col in ["Code", "Title", "Credits", "Department"]:
            self.course_tree.heading(col, text=col)
            self.course_tree.column(col, width=120, anchor="center")
        
        # Add sample data
        sample_courses = [
            ("CS101", "Introduction to Programming", 3, "Computer Science"),
            ("MATH202", "Advanced Calculus", 4, "Mathematics"),
            ("ENG105", "Academic Writing", 3, "English")
        ]
        
        for course in sample_courses:
            self.course_tree.insert("", "end", values=course)

    def add_course(self):
        """Add new course to the treeview"""
        try:
            code = self.course_code_entry.get()
            title = self.course_title_entry.get()
            credits = self.course_credits_entry.get()
            dept = self.course_dept_entry.get()
            
            if not all([code, title, credits]):
                messagebox.showwarning("Input Error", "Code, Title and Credits are required")
                return
                
            # Add to treeview
            self.course_tree.insert("", "end", values=(
                code,
                title,
                credits,
                dept if dept else "General"
            ))
            
            # Clear entries
            self.course_code_entry.delete(0, "end")
            self.course_title_entry.delete(0, "end")
            self.course_credits_entry.delete(0, "end")
            self.course_dept_entry.delete(0, "end")
            
            messagebox.showinfo("Success", "Course added")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add course: {str(e)}")
    
    def show_parent_portal(self):
        """Show parent portal window"""
        portal_window = ctk.CTkToplevel(self.root)
        portal_window.title("Parent Portal")
        portal_window.geometry("800x500")
        portal_window.resizable(False, False)
        portal_window.grab_set()
        portal_window.focus_force()
        
        label = ctk.CTkLabel(portal_window, text="Parent Dashboard", font=("Arial", 22, "bold"))
        label.pack(pady=30)
        
        # Info box
        ctk.CTkLabel( portal_window,
        text="🔧 This module is under improvisation.\nThe design is complete, but the backend is not optimized yet.© yogeshwar_vadla",
        font=("Arial", 16),
        text_color="orange"
        ).pack(pady=20)
    
        features = [
            "- PLANNED FEATURES -",
            "- Child's Attendance Records",
            "- Academic Performance",
            "- Messages from Teachers",
            "- School Announcements",
            "- Upcoming Events"
        ]
        
        for feature in features:
            item = ctk.CTkLabel(portal_window, text=feature, font=("Arial", 16))
            item.pack(pady=5)
    
    def exit_program(self):
        """Exit the application"""
        confirm = messagebox.askyesno("Exit", "Do you really want to exit?")
        if confirm:
            if self.conn:
                self.conn.close()
            self.root.destroy()
    
    # ===== Database Table Creation Methods =====
    
    def _create_auth_tables(self):
        """Create authentication tables"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            role ENUM('admin', 'teacher', 'student', 'parent') NOT NULL,
            account_status ENUM('active', 'inactive', 'locked') DEFAULT 'active',
            last_login DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            profile_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            phone VARCHAR(20),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)
        self.conn.commit()
    
    def _create_course_tables(self):
        """Create course management tables"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INT AUTO_INCREMENT PRIMARY KEY,
            course_code VARCHAR(20) UNIQUE NOT NULL,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            credits DECIMAL(3,1) NOT NULL,
            department VARCHAR(50),
            is_active BOOLEAN DEFAULT TRUE
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_prerequisites (
            prerequisite_id INT AUTO_INCREMENT PRIMARY KEY,
            course_id INT NOT NULL,
            required_course_id INT NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(course_id),
            FOREIGN KEY (required_course_id) REFERENCES courses(course_id),
            UNIQUE KEY (course_id, required_course_id)
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_sections (
            section_id INT AUTO_INCREMENT PRIMARY KEY,
            course_id INT NOT NULL,
            section_code VARCHAR(10) NOT NULL,
            semester VARCHAR(20) NOT NULL,
            year YEAR NOT NULL,
            instructor_id INT,
            room VARCHAR(20),
            schedule VARCHAR(100),
            max_capacity INT,
            current_enrollment INT DEFAULT 0,
            FOREIGN KEY (course_id) REFERENCES courses(course_id),
            FOREIGN KEY (instructor_id) REFERENCES users(user_id),
            UNIQUE KEY (course_id, section_code, semester, year)
        )
        """)
        self.conn.commit()
    
    def _create_registration_tables(self):
        """Create registration tables"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            section_id INT NOT NULL,
            enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status ENUM('registered', 'waitlisted', 'dropped', 'completed') DEFAULT 'registered',
            grade VARCHAR(2),
            FOREIGN KEY (student_id) REFERENCES users(user_id),
            FOREIGN KEY (section_id) REFERENCES course_sections(section_id),
            UNIQUE KEY (student_id, section_id)
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollment_history (
            history_id INT AUTO_INCREMENT PRIMARY KEY,
            enrollment_id INT,
            student_id INT NOT NULL,
            section_id INT NOT NULL,
            action ENUM('register', 'drop', 'status_change', 'grade_update') NOT NULL,
            action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id)
        )
        """)
        self.conn.commit()
    
    def _create_attendance_tables(self):
        """Create attendance tracking tables"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_meetings (
            meeting_id INT AUTO_INCREMENT PRIMARY KEY,
            section_id INT NOT NULL,
            meeting_date DATE NOT NULL,
            start_time TIME,
            end_time TIME,
            topic VARCHAR(100),
            FOREIGN KEY (section_id) REFERENCES course_sections(section_id),
            UNIQUE KEY (section_id, meeting_date)
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_records (
            record_id INT AUTO_INCREMENT PRIMARY KEY,
            meeting_id INT NOT NULL,
            student_id INT NOT NULL,
            status ENUM('present', 'absent', 'late', 'excused') DEFAULT 'present',
            notes TEXT,
            recorded_by INT,
            record_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES class_meetings(meeting_id),
            FOREIGN KEY (student_id) REFERENCES users(user_id),
            FOREIGN KEY (recorded_by) REFERENCES users(user_id),
            UNIQUE KEY (meeting_id, student_id)
        )
        """)
        self.conn.commit()
    
    def _create_gradebook_tables(self):
        """Create gradebook tables"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS grade_categories (
            category_id INT AUTO_INCREMENT PRIMARY KEY,
            section_id INT NOT NULL,
            name VARCHAR(50) NOT NULL,
            weight DECIMAL(5,2) NOT NULL,
            total_points DECIMAL(6,2) NOT NULL,
            FOREIGN KEY (section_id) REFERENCES course_sections(section_id)
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS grade_items (
            item_id INT AUTO_INCREMENT PRIMARY KEY,
            category_id INT NOT NULL,
            name VARCHAR(100) NOT NULL,
            due_date DATE,
            total_points DECIMAL(6,2) NOT NULL,
            FOREIGN KEY (category_id) REFERENCES grade_categories(category_id)
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_grades (
            grade_id INT AUTO_INCREMENT PRIMARY KEY,
            item_id INT NOT NULL,
            student_id INT NOT NULL,
            points_earned DECIMAL(6,2),
            notes TEXT,
            recorded_by INT,
            record_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES grade_items(item_id),
            FOREIGN KEY (student_id) REFERENCES users(user_id),
            FOREIGN KEY (recorded_by) REFERENCES users(user_id),
            UNIQUE KEY (item_id, student_id)
        )
        """)
        self.conn.commit()
    
    def _create_communication_tables(self):
        """Create communication tables"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            announcement_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            author_id INT NOT NULL,
            publish_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expiry_date DATE,
            audience ENUM('all', 'faculty', 'students', 'parents', 'specific') DEFAULT 'all',
            FOREIGN KEY (author_id) REFERENCES users(user_id)
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS announcement_targets (
            target_id INT AUTO_INCREMENT PRIMARY KEY,
            announcement_id INT NOT NULL,
            user_id INT,
            group_id INT,
            FOREIGN KEY (announcement_id) REFERENCES announcements(announcement_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id INT AUTO_INCREMENT PRIMARY KEY,
            sender_id INT NOT NULL,
            subject VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            parent_message_id INT,
            FOREIGN KEY (sender_id) REFERENCES users(user_id),
            FOREIGN KEY (parent_message_id) REFERENCES messages(message_id)
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS message_recipients (
            recipient_id INT AUTO_INCREMENT PRIMARY KEY,
            message_id INT NOT NULL,
            recipient_user_id INT NOT NULL,
            status ENUM('unread', 'read', 'archived') DEFAULT 'unread',
            read_time DATETIME,
            FOREIGN KEY (message_id) REFERENCES messages(message_id),
            FOREIGN KEY (recipient_user_id) REFERENCES users(user_id)
        )
        """)
        self.conn.commit()
    
    # ===== Authentication Methods =====
    
    def register_user(self, username, password, email, role, first_name, last_name):
        """Register a new user"""
        if self._user_exists(username, email):
            return False, "Username or email already exists"
        
        password_hash = pbkdf2_sha256.hash(password)
        
        try:
            self.cursor.execute("""
            INSERT INTO users (username, password_hash, email, role)
            VALUES (%s, %s, %s, %s)
            """, (username, password_hash, email, role))
            
            user_id = self.cursor.lastrowid
            
            self.cursor.execute("""
            INSERT INTO user_profiles (user_id, first_name, last_name)
            VALUES (%s, %s, %s)
            """, (user_id, first_name, last_name))
            
            self.conn.commit()
            return True, "Registration successful"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
    
    def login(self, username, password):
        """Authenticate user"""
        self.cursor.execute("""
        SELECT user_id, password_hash, role, account_status FROM users 
        WHERE username = %s
        """, (username,))
        
        result = self.cursor.fetchone()
        
        if not result:
            return False, "Invalid username or password", None
        
        user_id, stored_hash, role, status = result
        
        if status != 'active':
            return False, "Account is not active", None
            
        if pbkdf2_sha256.verify(password, stored_hash):
            # Update last login
            self.cursor.execute("""
            UPDATE users SET last_login = NOW() 
            WHERE user_id = %s
            """, (user_id,))
            self.conn.commit()
            
            self.current_user = {
                "id": user_id,
                "username": username,
                "role": role
            }
            
            return True, "Login successful", role
        else:
            return False, "Invalid username or password", None
    
    def _user_exists(self, username, email):
        """Check if username/email exists"""
        self.cursor.execute("""
        SELECT user_id FROM users 
        WHERE username = %s OR email = %s
        """, (username, email))
        return self.cursor.fetchone() is not None
    
    # ===== Course Management Methods =====
    
    def add_course(self, course_code, title, credits, description="", department=""):
        """Add a new course"""
        try:
            self.cursor.execute("""
            INSERT INTO courses (course_code, title, credits, description, department)
            VALUES (%s, %s, %s, %s, %s)
            """, (course_code, title, credits, description, department))
            self.conn.commit()
            return True, "Course added successfully"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
    
    def add_prerequisite(self, course_code, prerequisite_code):
        """Add course prerequisite"""
        try:
            self.cursor.execute("""
            INSERT INTO course_prerequisites (course_id, required_course_id)
            VALUES (
                (SELECT course_id FROM courses WHERE course_code = %s),
                (SELECT course_id FROM courses WHERE course_code = %s)
            )
            """, (course_code, prerequisite_code))
            self.conn.commit()
            return True, "Prerequisite added successfully"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
    
    def create_section(self, course_code, section_code, semester, year, 
                     instructor_id=None, room=None, schedule=None, max_capacity=30):
        """Create course section"""
        try:
            self.cursor.execute("""
            INSERT INTO course_sections 
            (course_id, section_code, semester, year, instructor_id, room, schedule, max_capacity)
            VALUES (
                (SELECT course_id FROM courses WHERE course_code = %s),
                %s, %s, %s, %s, %s, %s, %s
            )
            """, (course_code, section_code, semester, year, 
                 instructor_id, room, schedule, max_capacity))
            self.conn.commit()
            return True, "Course section created successfully"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
    
    # ===== Registration Methods =====
    
    def register_student(self, student_id, section_id):
        """Register student for course section"""
        try:
            # Check capacity
            self.cursor.execute("""
            SELECT current_enrollment, max_capacity 
            FROM course_sections 
            WHERE section_id = %s
            """, (section_id,))
            enrollment, capacity = self.cursor.fetchone()
            
            if enrollment >= capacity:
                # Add to waitlist
                self.cursor.execute("""
                INSERT INTO enrollments (student_id, section_id, status)
                VALUES (%s, %s, 'waitlisted')
                """, (student_id, section_id))
                self.conn.commit()
                return False, "Course is full. You have been added to the waitlist."
            
            # Register student
            self.cursor.execute("""
            INSERT INTO enrollments (student_id, section_id)
            VALUES (%s, %s)
            """, (student_id, section_id))
            
            # Update enrollment count
            self.cursor.execute("""
            UPDATE course_sections 
            SET current_enrollment = current_enrollment + 1 
            WHERE section_id = %s
            """, (section_id,))
            
            # Log registration
            enrollment_id = self.cursor.lastrowid
            self.cursor.execute("""
            INSERT INTO enrollment_history 
            (enrollment_id, student_id, section_id, action, details)
            VALUES (%s, %s, %s, 'register', 'Initial registration')
            """, (enrollment_id, student_id, section_id))
            
            self.conn.commit()
            return True, "Registration successful"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
    
    def check_schedule_conflicts(self, student_id, new_section_id):
        """Check for schedule conflicts"""
        self.cursor.execute("""
        SELECT cs.schedule 
        FROM enrollments e
        JOIN course_sections cs ON e.section_id = cs.section_id
        WHERE e.student_id = %s AND e.status = 'registered'
        """, (student_id,))
        
        current_schedules = [row[0] for row in self.cursor.fetchall()]
        
        self.cursor.execute("""
        SELECT schedule FROM course_sections 
        WHERE section_id = %s
        """, (new_section_id,))
        new_schedule = self.cursor.fetchone()[0]
        
        # Simplified conflict check - would need proper schedule parsing
        for schedule in current_schedules:
            if schedule == new_schedule:
                return True
        return False
    
    # ===== Attendance Methods =====
    
    def record_class_meeting(self, section_id, meeting_date, start_time=None, end_time=None, topic=None):
        """Record class meeting"""
        try:
            self.cursor.execute("""
            INSERT INTO class_meetings 
            (section_id, meeting_date, start_time, end_time, topic)
            VALUES (%s, %s, %s, %s, %s)
            """, (section_id, meeting_date, start_time, end_time, topic))
            self.conn.commit()
            return True, "Class meeting recorded successfully"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
    
    def mark_attendance(self, meeting_id, student_id, status='present', notes=None, recorded_by=None):
        """Record student attendance"""
        try:
            self.cursor.execute("""
            INSERT INTO attendance_records 
            (meeting_id, student_id, status, notes, recorded_by)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            status = VALUES(status), 
            notes = VALUES(notes),
            recorded_by = VALUES(recorded_by),
            record_time = CURRENT_TIMESTAMP
            """, (meeting_id, student_id, status, notes, recorded_by))
            self.conn.commit()
            return True, "Attendance recorded successfully"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
    
    def generate_attendance_report(self, section_id, start_date=None, end_date=None):
        """Generate attendance report"""
        query = """
        SELECT 
            u.user_id,
            CONCAT(up.first_name, ' ', up.last_name) AS student_name,
            cm.meeting_date,
            ar.status,
            cm.topic
        FROM 
            enrollments e
            JOIN users u ON e.student_id = u.user_id
            JOIN user_profiles up ON u.user_id = up.user_id
            JOIN class_meetings cm ON e.section_id = cm.section_id
            LEFT JOIN attendance_records ar ON cm.meeting_id = ar.meeting_id AND ar.student_id = u.user_id
        WHERE 
            e.section_id = %s
            AND e.status = 'registered'
        """
        
        params = [section_id]
        
        if start_date and end_date:
            query += " AND cm.meeting_date BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        
        query += " ORDER BY student_name, cm.meeting_date"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    # ===== Gradebook Methods =====
    
    def add_grade_category(self, section_id, name, weight, total_points=100):
        """Add grade category"""
        try:
            # Validate total weight
            self.cursor.execute("""
            SELECT SUM(weight) FROM grade_categories 
            WHERE section_id = %s
            """, (section_id,))
            total_weight = self.cursor.fetchone()[0] or 0
            
            if total_weight + weight > 100:
                return False, "Total weight cannot exceed 100%"
            
            self.cursor.execute("""
            INSERT INTO grade_categories 
            (section_id, name, weight, total_points)
            VALUES (%s, %s, %s, %s)
            """, (section_id, name, weight, total_points))
            self.conn.commit()
            return True, "Grade category added successfully"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
    
    def add_grade_item(self, category_id, name, total_points, due_date=None):
        """Add grade item"""
        try:
            self.cursor.execute("""
            INSERT INTO grade_items 
            (category_id, name, total_points, due_date)
            VALUES (%s, %s, %s, %s)
            """, (category_id, name, total_points, due_date))
            self.conn.commit()
            return True, "Grade item added successfully"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
    
    def record_grade(self, item_id, student_id, points_earned, recorded_by, notes=None):
        """Record student grade"""
        try:
            self.cursor.execute("""
            INSERT INTO student_grades 
            (item_id, student_id, points_earned, recorded_by, notes)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            points_earned = VALUES(points_earned),
            notes = VALUES(notes),
            recorded_by = VALUES(recorded_by),
            record_time = CURRENT_TIMESTAMP
            """, (item_id, student_id, points_earned, recorded_by, notes))
            self.conn.commit()
            return True, "Grade recorded successfully"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
    
    def calculate_final_grade(self, section_id, student_id):
        """Calculate final grade"""
        self.cursor.execute("""
        SELECT 
            gc.name AS category,
            gc.weight,
            gc.total_points AS category_total,
            gi.name AS item,
            gi.total_points AS item_total,
            sg.points_earned
        FROM 
            grade_categories gc
            JOIN grade_items gi ON gc.category_id = gi.category_id
            LEFT JOIN student_grades sg ON gi.item_id = sg.item_id AND sg.student_id = %s
        WHERE 
            gc.section_id = %s
        """, (student_id, section_id))
        
        grades = self.cursor.fetchall()
        
        if not grades:
            return None
        
        # Calculate weighted grade
        total_weighted = 0
        
        for grade in grades:
            category, weight, category_total, item, item_total, points_earned = grade
            if points_earned is not None:
                item_percent = (points_earned / item_total) * 100
                weighted = item_percent * (weight / 100)
                total_weighted += weighted
        
        # Convert to letter grade
        if total_weighted >= 90:
            return 'A'
        elif total_weighted >= 80:
            return 'B'
        elif total_weighted >= 70:
            return 'C'
        elif total_weighted >= 60:
            return 'D'
        else:
            return 'F'
    
    # ===== Communication Methods =====
    
    def create_announcement(self, title, content, author_id, audience='all', expiry_date=None, specific_targets=None):
        """Create announcement"""
        try:
            self.cursor.execute("""
            INSERT INTO announcements 
            (title, content, author_id, audience, expiry_date)
            VALUES (%s, %s, %s, %s, %s)
            """, (title, content, author_id, audience, expiry_date))
            
            if audience == 'specific' and specific_targets:
                announcement_id = self.cursor.lastrowid
                for user_id in specific_targets:
                    self.cursor.execute("""
                    INSERT INTO announcement_targets 
                    (announcement_id, user_id)
                    VALUES (%s, %s)
                    """, (announcement_id, user_id))
            
            self.conn.commit()
            return True, "Announcement created successfully"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
    
    def send_message(self, sender_id, recipient_ids, subject, content, parent_message_id=None):
        """Send message"""
        try:
            self.cursor.execute("""
            INSERT INTO messages 
            (sender_id, subject, content, parent_message_id)
            VALUES (%s, %s, %s, %s)
            """, (sender_id, subject, content, parent_message_id))
            
            message_id = self.cursor.lastrowid
            
            for recipient_id in recipient_ids:
                self.cursor.execute("""
                INSERT INTO message_recipients 
                (message_id, recipient_user_id)
                VALUES (%s, %s)
                """, (message_id, recipient_id))
            
            self.conn.commit()
            return True, "Message sent successfully"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
    
    def get_unread_messages(self, user_id):
        """Get unread messages"""
        self.cursor.execute("""
        SELECT 
            m.message_id,
            m.subject,
            m.content,
            m.sent_time,
            CONCAT(up.first_name, ' ', up.last_name) AS sender_name,
            u.username AS sender_username
        FROM 
            message_recipients mr
            JOIN messages m ON mr.message_id = m.message_id
            JOIN users u ON m.sender_id = u.user_id
            JOIN user_profiles up ON u.user_id = up.user_id
        WHERE 
            mr.recipient_user_id = %s
            AND mr.status = 'unread'
        ORDER BY m.sent_time DESC
        """, (user_id,))
        
        return self.cursor.fetchall()
    
    def mark_message_read(self, message_id, user_id):
        """Mark message as read"""
        try:
            self.cursor.execute("""
            UPDATE message_recipients 
            SET status = 'read', read_time = NOW() 
            WHERE message_id = %s AND recipient_user_id = %s
            """, (message_id, user_id))
            self.conn.commit()
            return True, "Message marked as read"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)

# Main application entry point
if __name__ == "__main__":
    root = ctk.CTk()
    app = StudentManagementSystem(root)
    root.mainloop()