import sqlite3 as s

class db():
    def __init__(self) -> None:
        self.db = s.connect("elec_data.db")
        self.cursor = self.db.cursor()

        self.time: tuple[int, int] = (2000,2000)
        self.loc: list[str] = []#Locations
        self.sources: list[str] = []#Sources of electricity; generation method
        #self.data: list[str]#Types of data to retrieve
        #self.org: str = "DESC"#Organization method

    def time_menu(self):
        """
            Menu for modifying stored time from console
        """
        #Get available dates
        self.cursor.execute("""
        SELECT DISTINCT year
        FROM Energy
        ORDER BY year;
        """)
        dates = self.cursor.fetchall()
        print("Date range:",dates[0][0],"-",dates[-1][0])

        valid_date: bool = False
        while not valid_date:
            new_start = int(input("Please select a start year: "))
            #Check if in range
            if (new_start,) in dates:
                valid_date = True
        valid_date = False
        while not valid_date:
            new_end = int(input("Please select an end year: "))
            #Check if date valid
            if ((new_end,) in dates) and (new_end >= new_start):
                valid_date = True
        self.time = (int(new_start), int(new_end))

    def loc_menu(self):
        #Get available locations
        self.cursor.execute("""
        SELECT DISTINCT country
        FROM Energy
        ORDER BY country;
        """)
        countries = self.cursor.fetchall()

        while(input("Do you want to add/remove a country? (y/n): ")=="y"):
            print("Countries:")
            for c in countries:
                print(" ",c[0])
            print("Currently selected countries:")
            for l in self.loc:
                print(" ",l)
            selected = input("Enter country to add or remove: ")
            if selected in self.loc:
                self.loc.remove(selected)
            elif (selected,) in countries:
                self.loc.append(selected)
            else:
                print("Invalid input.")


    def source_menu(self):
        #Get available sources
        self.cursor.execute("""
        SELECT DISTINCT source
        FROM Energy
        ORDER BY source;
        """)
        sources = self.cursor.fetchall()

        while(input("Do you want to add/remove a source? (y/n): ")=="y"):
            print("Sources:")
            for s in sources:
                print(" ",s[0])
            print("Currently selected sources:")
            for s in self.sources:
                print(" ",s)
            selected = input("Enter source to add or remove: ")
            if selected in self.sources:
                self.sources.remove(selected)
            elif (selected,) in sources:
                self.sources.append(selected)
            else:
                print("Invalid input.")

    def org_menu(self):
        print("Please select an option:")
        print("  a: Ascending order")
        print("  d: Descending order")
        print("  f: Change field to organize by")
        print("  q: Quit")
        #Get user input
        match input():
            case "a":
                self.org = ""
            case "d":
                self.org = "DESC"
            case "q":
                return False
            case _:
                print("Invalild input. Please try again.")
    
    def print(self):
        """Prints total energy from selected range & sources in treawatt-hours"""
        total: float = 0
        for c in self.loc:
            for y in range(self.time[0], self.time[1]+1):
                for s in self.sources:
                    self.cursor.execute("""
                    SELECT electricity
                    FROM Energy
                    WHERE country=?
                    AND year=?
                    AND source=?
                    """, (c,y,s))
                    data = self.cursor.fetchall()[0][0]
                    if data:
                        total += float(data)
        print("Total energy in terawatt-hours:", total)
    
    def menu(self) -> bool:
        """
            Prints to database interface main menu.
            Shows currently selected options
            Moves to submenus if necessary:
                +Time period (date range)
                +Geographic source selection
                +Generation method selection
                +Data selection
            Allows display of data from database.
            Returns True if menu stil being used, and False if exiting.
        """
        #Setup
        #choice: chr = ''
        #time period: tuple[date, date]
        
        #database = db_handler.db()

        print("Current choices:")
        print("  Time period:", self.time)
        print("  Locations:", self.loc)
        print("  Sources:", self.sources)
        #print("  Data:", "N/A")
        #print("  Organization method:", "N/A")

        #Print menu choices
        print("Please select an option:")
        print("  t: Change time period")
        print("  l: Change locations")
        print("  s: Change source of electricity")
        #print("  d: Select data to retrieve")
        #print("  o: Select Organization method")
        print("  p: Print data")
        print("  q: Quit")
        #Get user input
        match input():
            case "t":
                self.time_menu()
            case "l":
                self.loc_menu()
            case "s":
                self.source_menu()
            case "p":
                self.print()
            case "q":
                return False
            case _:
                print("Invalild input. Please try again.")
        return True
