import tkinter as tk
from ttkbootstrap import Style
from tkinter import ttk, messagebox
import pypyodbc as odbc
import hashlib
from datetime import datetime
import yagmail

class StalaQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stala Quiz")
        self.root.geometry("600x400")

        self.style = Style(theme="minty")  

        self.username_label = ttk.Label(root, text="Username:")
        self.username_label.pack(pady=5)
        self.username_entry = ttk.Entry(root, width=30)
        self.username_entry.pack(pady=5, padx=20, ipady=3)

        self.password_label = ttk.Label(root, text="Password:")
        self.password_label.pack(pady=5)
        self.password_entry = ttk.Entry(root, show="*", width=30)
        self.password_entry.pack(pady=5, padx=20, ipady=3)

        self.login_button = ttk.Button(root, text="Login", command=self.login)
        self.login_button.pack(pady=10)

        self.signup_button = ttk.Button(root, text="Signup", command=self.show_signup_window)
        self.signup_button.pack(pady=10)

        self.quit_button = ttk.Button(root, text="Quit", command=root.destroy)
        self.quit_button.pack(pady=10)

        self.cursor = None
        self.mycon = None
        self.quiz_window = None
        self.questions = []

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        hashed_username = hashlib.md5(username.encode()).hexdigest()
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        if self.check_credentials(hashed_username, hashed_password):
            self.start_quiz(username)
        else:
            messagebox.showerror("Login Error", "Invalid username or password.")

    def show_signup_window(self):
        signup_window = tk.Toplevel(self.root)
        signup_window.title("Signup - Stala Quiz")

        self.signup_username_label = tk.Label(signup_window, text="Username:")
        self.signup_username_label.pack(pady=5)
        self.signup_username_entry = tk.Entry(signup_window, width=30)
        self.signup_username_entry.pack(pady=5, padx=20, ipady=3)

        self.signup_password_label = tk.Label(signup_window, text="Password:")
        self.signup_password_label.pack(pady=5)
        self.signup_password_entry = tk.Entry(signup_window, show="*", width=30)
        self.signup_password_entry.pack(pady=5, padx=20, ipady=3)

        self.signup_email_label = tk.Label(signup_window, text="Email:")
        self.signup_email_label.pack(pady=5)
        self.signup_email_entry = tk.Entry(signup_window, width=30)
        self.signup_email_entry.pack(pady=5, padx=20, ipady=3)

        self.signup_confirm_button = tk.Button(signup_window, text="Confirm Signup", command=lambda: self.signup(signup_window))
        self.signup_confirm_button.pack(pady=10)

    def signup(self, signup_window):
        username = self.signup_username_entry.get()
        password = self.signup_password_entry.get()
        email = self.signup_email_entry.get()

        if not username or not password or not email:
            messagebox.showerror("Signup Error", "Please enter all required fields.")
            return

        hashed_username = hashlib.md5(username.encode()).hexdigest()
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        if self.check_username_existence(hashed_username):
            messagebox.showerror("Signup Error", "Username already exists. Please choose another.")
        else:
            try:
                confirm = messagebox.askyesno("Confirm Signup",
                                              "Do you want to create an account with the provided information?")
                if confirm:
                    result = self.create_account(hashed_username, hashed_password, email)
                    if result:
                        messagebox.showinfo("Signup Successful", "Account created successfully. You can now log in.")
                        signup_window.destroy()
                    else:
                        messagebox.showerror("Signup Error",
                                             "An error occurred during account creation. Please try again.")
            except Exception as e:
                print(f"Error in signup: {e}")

    def check_credentials(self, username, password):
        try:
            hashed_password = hashlib.md5(password.encode()).hexdigest()  # Hash the password before comparing
            connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:staladatabase.database.windows.net,1433;Database=staladb;Uid=rootuserrohan;Pwd=ROHAN@jais12345;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
            self.mycon = odbc.connect(connection_string)
            self.cursor = self.mycon.cursor()
            self.cursor.execute("SELECT usrname, passwd FROM player WHERE usrname=? AND passwd=?", (username, hashed_password))
            data = self.cursor.fetchone()
            return data is not None
        except Exception as e:
            print(f"Error checking credentials: {e}")
            return False

    def check_username_existence(self, username):
        try:
            if not self.cursor:
                return False
            self.cursor.execute("SELECT usrname FROM player WHERE usrname=?", (username,))
            data = self.cursor.fetchone()
            return data is not None
        except Exception as e:
            print(f"Error checking username existence: {e}")
            return False

    def create_account(self, username, password, email):
        try:
            connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:staladatabase.database.windows.net,1433;Database=staladb;Uid=rootuserrohan;Pwd=ROHAN@jais12345;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
            self.mycon = odbc.connect(connection_string)
            self.cursor = self.mycon.cursor()
            hashed_password = hashlib.md5(password.encode()).hexdigest()  # Hash the password before storing
            query = "INSERT INTO player (usrname, passwd, email, datee, score, played) VALUES (?, ?, ?, ?, 0, 0)"
            self.cursor.execute(query, (username, hashed_password, email, datetime.now().strftime("%d-%m-%Y")))
            self.mycon.commit()
            print("Account created successfully.")
            self.mycon.close()
            return True
        except Exception as e:
            print(f"Error creating account: {e}")
            return False

    def start_quiz(self, username):
        self.root.iconify()

        self.quiz_window = tk.Toplevel(self.root)
        self.quiz_window.title("Stala Quiz - Quiz Window")

        self.questions = self.fetch_questions_from_database()
        self.current_question_index = self.fetch_played_question_count(username)

        self.quiz_label = tk.Label(self.quiz_window, text="Welcome to the Stala Quiz!", font=("Helvetica", 16))
        self.quiz_label.pack(pady=10)

        self.quiz_question_label = tk.Label(self.quiz_window, text="")
        self.quiz_question_label.pack(pady=10)

        self.quiz_options = []
        for option in ['A', 'B', 'C', 'D']:
            button = tk.Button(self.quiz_window, text="", command=lambda opt=option: self.answer_question(opt))
            button.pack(pady=5)
            self.quiz_options.append(button)

        self.score, self.played = self.fetch_user_score_and_played(username)

        self.quiz_score_label = tk.Label(self.quiz_window, text=f"Score: {self.score}, Played: {self.played}")
        self.quiz_score_label.pack(pady=10)

        self.exit_button = tk.Button(self.quiz_window, text="Exit", command=self.end_quiz)
        self.exit_button.pack(pady=10)

        self.load_question()
    def fetch_user_score_and_played(self, username):
        try:
            username_to_search = hashlib.md5(username.encode()).hexdigest()
            st = "SELECT score, played FROM player WHERE usrname = '{}';".format(username_to_search)
            self.cursor.execute(st)
            data = self.cursor.fetchone()
            if data:
                return data[0], data[1]
            else:
                return 0, 0
        except Exception as e:
            print(f"Error fetching user score and played count: {e}")
            return 0, 0

    def fetch_played_question_count(self, username):
        try:
            username_to_search = hashlib.md5(username.encode()).hexdigest()
            st = "SELECT played FROM player WHERE usrname = '{}';".format(username_to_search)
            self.cursor.execute(st)
            data = self.cursor.fetchone()
            if data:
                return data[0]
            else:
                return 0
        except Exception as e:
            print(f"Error fetching played question count: {e}")
            return 0

    def fetch_questions_from_database(self):
        try:
            st = 'SELECT * FROM questions'
            self.cursor.execute(st)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching questions: {e}")
            messagebox.showerror("Error", "An error occurred while fetching questions.")
            return []

    def load_question(self):
        try:
            data = self.questions[self.current_question_index]

            if data:
                question_text = data[0].capitalize()
                options = [data[i] for i in range(1, 5)]

                self.quiz_question_label.config(text=question_text)
                for i, option in enumerate(options):
                    self.quiz_options[i].config(text=f"{chr(65 + i)}. {option}")

            else:
                self.end_quiz()
        except Exception as e:
            print(f"Error loading question: {e}")
            messagebox.showerror("Error", "An error occurred while loading the question.")

        print("Loaded question:", data)  # Add this line to see the loaded question data

    def end_quiz(self):
        try:
            response = messagebox.askyesno("Quiz Finished",
                                           "Congratulations! You have completed the quiz.\nDo you want to receive an email with your final score?")

            username_to_search = hashlib.md5(self.username_entry.get().encode()).hexdigest()
            st = "UPDATE player SET score = {}, played = {} WHERE usrname = '{}';".format(self.score, self.played,
                                                                                          username_to_search)
            self.cursor.execute(st)
            self.mycon.commit()

            if response:
                self.send_email(self.username_entry.get())

            self.quiz_window.destroy()

            self.root.deiconify()
        except Exception as e:
            print(f"Error ending quiz: {e}")
            messagebox.showerror("Error", "An error occurred while ending the quiz.")

    def send_email(self, username):
        try:
            username_to_search = hashlib.md5(username.encode()).hexdigest()
            st = "SELECT email, score FROM player WHERE usrname = '{}';".format(username_to_search)
            self.cursor.execute(st)
            data = self.cursor.fetchone()

            if data:
                email = data[0]
                score = data[1]

                sender_email = "testingport123@gmail.com"
                sender_password = "vealeecorfomyaus"

                receiver_email = email
                subject = "Stala Quiz - Final Score"
                message = f"Dear {username},\n\nCongratulations! You have completed the Stala Quiz with a final score of {score}. Well done!\n\nBest regards,\nThe Stala Quiz Team"

                yag = yagmail.SMTP(sender_email, sender_password)
                yag.send(
                    to=receiver_email,
                    subject=subject,
                    contents=message
                )
                yag.close()

                print("Score has been Emailed to the respective player.")

                messagebox.showinfo("Email Sent", "The final score has been emailed to you.")
            else:
                print("Unable to fetch player data for email.")
        except Exception as e:
            print(f"Error sending email: {e}")
            messagebox.showerror("Error", "An error occurred while sending the email.")

    def answer_question(self, option):
        option_dict = {'A': 1, 'B': 2, 'C': 3, 'D': 4}

        try:
            data = self.questions[self.current_question_index]

            if data[option_dict[option]] == data[5].strip():
                messagebox.showinfo("Correct!", "Your answer is correct!")
                self.score += 10
            else:
                messagebox.showinfo("Incorrect!", "Your answer is incorrect. The correct answer is: " + data[5])
                self.score -= 5

            self.quiz_score_label.config(text=f"Score: {self.score}, Played: {self.played}")

        except Exception as e:
            print(f"Error answering question: {e}")
            messagebox.showerror("Error", "An error occurred while answering the question.")

        self.played += 1
        self.current_question_index += 1

        if self.current_question_index < len(self.questions):
            self.load_question()
        else:
            self.end_quiz()

if __name__ == "__main__":
    root = tk.Tk()
    app = StalaQuizApp(root)
    root.mainloop()
