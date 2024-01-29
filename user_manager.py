import hashlib
import sqlite3

class user():
    def __init__(self) -> None:
        self.username: str = None
        self.password: str = None
        self._admin: bool = False

        self.db = sqlite3.connect("user_data.db")
        self.cursor = self.db.cursor()
        #self.cursor.row_factory = sqlite3.Row
        pass

    def set_username(self, username: str):
        self.username = username
        return
    
    def password_hash(self, password: str) -> str:
        h = hashlib.new("sha256")
        h.update(password.encode("utf-8"))
        return str(h.hexdigest())

    def set_password(self, username: str, password: str):
        self.password = self.password_hash(username+password)
        return
    
    def login(self) -> bool:
        #Temp menu
        while (input("Are you logging in? (y/n): ") == "y"):
            #Get username & password
            self.set_username(input("Please input username (max length 64): "))###########
            self.set_password(self.username, input("Please input password: "))
            self._admin = False
            #Check if username & password match in db. Adjust admin status to match
            self.cursor.execute("""
                           SELECT admin
                           FROM Users
                           WHERE username=? AND password=?;""",
                        (self.username, self.password))
            rows = self.cursor.fetchall()
            if (rows):
                print("Logging in...")
                if (rows[0][0]=="TRUE"):
                    print("Logging in as admin.")
                    self._admin = True
                return True
            else:
                print("Invalid username/password.")
        print("Ending program.")
        return False

    def set_admin(self, username: str, is_admin: bool):###
        if (self._admin):
            #Check if user exists
            self.cursor.execute("""
            SELECT admin
            FROM Users
            WHERE username=?;
            """, (username,))
            rows = self.cursor.fetchall()
            #Set admin privliges
            if (rows):
                self.cursor.execute("""
                UPDATE Users
                SET admin=?
                WHERE username=?;
                """, (is_admin, username))
                self.db.commit()
        return

    def insert_user(self, new_username: str, new_password: str, is_admin: bool):
        try:
            if (is_admin):
                self.cursor.execute("INSERT INTO Users (username, password, admin) VALUES (?,?,?);",
                            (new_username, self.password_hash(new_username+new_password), "TRUE"))
            else:
                self.cursor.execute("INSERT INTO Users (username, password, admin) VALUES (?,?,?);",
                            (new_username, self.password_hash(new_username+new_password), "FALSE"))
        except sqlite3.IntegrityError:
            print("ERROR: UNIQUE constraint failed. Try a different username.")
        self.db.commit()

    def make_user(self):
        new_username: str = input("Please input username: ")
        new_password: str = input("Please input password: ")
        is_admin = False
        #If admin, alow to make as admin
        if (self._admin):
            if (input("Should this user be admin? (y/n): ") == "y"):
                is_admin = True
        #Insert user
        self.insert_user(new_username, new_password, is_admin)
        return

    def delete_user(self):
        if not self._admin:
            print("You need admin status for that!")
        else:
            username = input("Please input the username of the account to delete: ")
            self.cursor.execute("""
            DELETE FROM Users
            WHERE username=?;""",
            (username,))

    def admin_menu(self) -> bool:
        if self._admin:
            #Print menu choices
            print("Please select an option:")
            print("  p: Print users")
            print("  c: Create new user")
            print("  a: Adjust admin status")
            print("  d: Delete user")
            print("  q: Quit")
            #Get user input
            match input():
                case "p":
                    self.print_users()
                case "c":
                    self.make_user()
                case "a":
                    if not self._admin:
                        print("You need admin status for that!")
                    else:
                        username = input("Please input the username of the account to adjust: ")
                        is_admin = False
                        if input("Should this user be an admin? (y/n): ") == "y":
                            is_admin = True
                        self.set_admin(username, is_admin)
                case "d":
                    self.delete_user()
                case "q":
                    print("Exiting menu.")
                    return False
                case _:
                    print("Invalild input. Please try again.")
        else:
            return False
        return True
    
    def print_users(self):
        self.cursor.execute("SELECT username FROM Users;")
        records = self.cursor.fetchall()
        for r in records:
            print(r[0])