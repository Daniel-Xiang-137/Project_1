#import datetime
import user_manager
import db_handler




def main():
    #Login menu
    database = db_handler.db()
    u = user_manager.user()
    while (u.login()):
        while u.admin_menu():
            pass
        while database.menu():
            pass
    

if __name__=="__main__":
    main()