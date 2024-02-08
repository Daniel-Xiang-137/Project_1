import hashlib
#import sqlite3###
from google.cloud import bigquery as bq
from google.oauth2 import service_account as sa

class user():
    def __init__(self) -> None:
        self.username: str = None
        self.password: str = None
        self._admin: bool = False

        self.credentials = sa.Credentials.from_service_account_file("engaged-tape-412316-0c6a1760feec.json")
        project_id = "engaged-tape-412316"
        self.client = bq.Client(credentials=self.credentials, project=project_id)
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
            self.set_username(input("Please input username: "))###########
            self.set_password(self.username, input("Please input password: "))
            self._admin = False
            #Check if username & password match in db. Adjust admin status to match
            rows = self.client.query("""
                SELECT admin
                FROM Energy_Data.Users
                WHERE username="{}" AND password="{}";
                """.format(self.username, self.password)).result()

            if (rows.total_rows > 0):
                print("Logging in...")
                if (next(rows)[0]):
                    print("Logging in as admin.")
                    self._admin = True
                return True
            else:
                print("Invalid username/password.")
        print("Ending program.")
        return False

    def logout(self, settings):
        #Upload info to database
        self.save_settings(settings=settings)
        self.username = None
        self.password = None
        self._admin = False
        pass

    def set_admin(self, username: str, is_admin: bool):###
        if (self._admin):
            #Check if user exists
            rows = self.client.query("""
                SELECT admin
                FROM Energy_Data.Users
                WHERE username="{}";
                """.format(username)).result()
            #Set admin privliges
            if (rows.total_rows > 0):
                self.client.query("""
                    UPDATE Energy_Data.Users
                    SET admin={}
                    WHERE username="{}";
                    """.format(is_admin, username)).result()
        return

    def insert_user(self, new_username: str, new_password: str, is_admin: bool):
        check = self.client.query("""SELECT username FROM Energy_Data.Users WHERE username="{}";""".format(new_username)).result()
        if check.total_rows == 0:
            if (is_admin and self._admin):
                self.client.query("""INSERT INTO Energy_Data.Users (username, password, admin) VALUES ("{}","{}",{});""".format(new_username, self.password_hash(new_username+new_password), True)).result()
            else:
                self.client.query("""INSERT INTO Energy_Data.Users (username, password, admin) VALUES ("{}","{}",{});""".format(new_username, self.password_hash(new_username+new_password), False)).result()
        else:
            print("ERROR: UNIQUE constraint failed. Try a different username.")
        

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
            self.client.query("""
                DELETE FROM Energy_Data.Users
                WHERE username="{}";""".format(username)).result()
            self.client.query("""
                DELETE FROM Energy_Data.User_Settings
                WHERE user="{}";""".format(username)).result()

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
        records = self.client.query("SELECT username FROM Energy_Data.Users;").result()
        for r in records:
            print(r[0])
    
    def get_settings(self):
        #Get settings if there are any
        settings = self.client.query("""
            SELECT start_date, end_date, locations, sources
            FROM Energy_Data.User_Settings
            WHERE user="{}";""".format(self.username)).result()
        if settings.total_rows > 0:
            s = next(settings)
            return (
                s.get("start_date"),
                s.get("end_date"),
                s.get("locations"),
                s.get("sources")
            )
        else:
            return None
    
    def save_settings(self, settings):
        self.client.query("""
            DELETE FROM Energy_Data.User_Settings
            WHERE user="{}";""".format(self.username)).result()
        self.client.query("""
            INSERT INTO Energy_Data.User_Settings
            VALUES ({}, {}, "{}", "{}", "{}");""".format(settings[0], settings[1], settings[2], settings[3], self.username)).result()