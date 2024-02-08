#import datetime
import user_manager
import db_handler

def main():
    #Login menu
    database = db_handler.db()
    u = user_manager.user()
    while (u.login()):
        settings = u.get_settings()
        #print(settings)
        if settings != None:
            database.set_settings(settings=settings)
        else:
            database.set_settings((2000,2000,"",""))
        while u.admin_menu():
            pass
        while database.menu():
            pass
        print("Logging out.")
        settings = database.get_settings()
        u.logout(settings)
    

if __name__=="__main__":
    main()