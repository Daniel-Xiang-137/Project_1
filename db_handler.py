#import sqlite3 as s
from google.cloud import bigquery as bq
from google.oauth2 import service_account as sa

class db():
    def __init__(self) -> None:
        #self.db = s.connect("elec_data.db")
        #self.cursor = self.db.cursor()
        
        self.credentials = sa.Credentials.from_service_account_file("engaged-tape-412316-0c6a1760feec.json")
        project_id = "engaged-tape-412316"
        self.client = bq.Client(credentials=self.credentials, project=project_id)

        self.time: tuple[int, int] = (2000,2000)
        self.loc: list[str] = []#Locations
        self.sources: list[str] = []#Sources of electricity; generation method
        #self.data: list[str]#Types of data to retrieve
        #self.org: str = "DESC"#Organization method

        self.table_sources = {
            "Biofuel":"biofuel_electricity",
            "Coal":"coal_electricity",
            "Fossil Fuel":"fossil_electricity",
            "Gas":"gas_electricity",
            "Hydropower":"Hydro_electricity",
            "Low-Carbon":"low_carbon_electricity",
            "Nuclear":"nuclear_electricity",
            "Oil":"oil_electricity",
            "Other Renewables":"other_renewable_electricity",
            "Other Renewables Excluding Biofuel":"other_renewable_exc_biofuel_electricity",
            "Renewables":"renewables_electricity",
            "Solar":"solar_electricity",
            "Wind":"wind_electricity"
        }
        

    def time_menu(self):
        """
            Menu for modifying stored time from console
        """
        #Get available dates
        q = self.client.query("""
            SELECT DISTINCT year
            FROM Energy_Data.Energy
            ORDER BY year;
            """).result()
        s = int(next(q)[0])
        while (True):
            try:
                e = int(next(q)[0])
            except StopIteration:
                break
        print("Date range:",s,"-",e)

        valid_date: bool = False
        while not valid_date:
            new_start = int(input("Please select a start year: "))
            #Check if in range
            if (new_start) in range(s, e+1):
                valid_date = True
        valid_date = False
        while not valid_date:
            new_end = int(input("Please select an end year: "))
            #Check if date valid
            if ((new_end) in range(s, e+1)) and (new_end >= new_start):
                valid_date = True
        self.time = (int(new_start), int(new_end))

    def loc_menu(self):
        #Get available locations
        q = self.client.query("""
            SELECT DISTINCT country
            FROM Energy_Data.Energy
            ORDER BY country;""").result()
        countries = []
        while True:
            try:
                countries.append(str(next(q)[0]))
            except StopIteration:
                break

        while(input("Do you want to add/remove a country? (y/n): ")=="y"):
            print("Countries:")
            for c in countries:
                print(" ",c)
            print("Currently selected countries:")
            for l in self.loc:
                print(" ",l)
            selected = input("Enter country to add or remove: ")
            if selected in self.loc:
                self.loc.remove(selected)
            elif selected in countries:
                self.loc.append(selected)
            else:
                print("Invalid input.")

    def source_menu(self):
        

        while(input("Do you want to add/remove a source? (y/n): ")=="y"):
            print("Sources:")
            for s in self.table_sources:
                print(" ",s)
            print("Currently selected sources:")
            for s in self.sources:
                print(" ",s)
            selected = input("Enter source to add or remove: ")
            if selected in self.sources:
                self.sources.remove(selected)
            elif selected in self.table_sources:
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
                    data = self.client.query("""
                        SELECT {}
                        FROM Energy_Data.Energy
                        WHERE country="{}"
                        AND year={}
                        """.format(self.table_sources[s],c,y)).result()
                    while True:
                        try:
                            #print(next(data).get(self.table_sources[s]))
                            t = next(data).get(self.table_sources[s])
                            if t:
                                total += t
                        except StopIteration:
                            break
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
    
    def get_settings(self):
        return (self.time[0],self.time[1],",".join(self.loc),",".join(self.sources))
    def set_settings(self, settings):
        #start: int, end: int, locations: list[str], sources: list[str]
        self.time = (int(settings[0]), int(settings[1]))
        self.loc = settings[2].split(",")
        self.sources = settings[3].split(",")
        if ("" in self.loc):
            self.loc.remove("")
        if ("" in self.sources):
            self.sources.remove("")