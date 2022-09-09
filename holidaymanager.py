from datetime import datetime, date
import json
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from config import * 
 

def getHTML(url):
    response = requests.get(url)
    return response.text

def getJson(url):
    response = requests.get(url)
    return response.json()

@dataclass
class Holiday:
    name: str
    date: datetime
      
    def __init__(self, name, date):
        self._name = name
        self._date = date    
    
    def __str__ (self):
        return f'{self._name} ({self._date.strftime("%Y-%m-%d")})'    # Holiday output when printed.

    @property
    def name(self):
        return self._name
    
    @property
    def date(self):
        return self._date    

@dataclass
class HolidayList:
    def __init__(self):
        self.innerHolidays = []

    def addHoliday(self):
        print("Add A Holiday")
        print("====================")
        isValid = False
        holiname = str(input("Holiday Name:    ")).title()
        while not isValid:
            holidate = input("Holiday Date (yyyy-mm-dd):    ")
            try:
                valid_date = datetime.strptime(holidate, '%Y-%m-%d').date()
                if (date(2020, 1, 1) <= valid_date <= date(2024, 12, 31)):
                    isValid = True
                else:
                    print('Date out of range!')
            except:
                print('Invalid date!')  
                continue
        if self.findHoliday(holiname, holidate) == True:    #don't let duplicates in
            print(f'Sorry. {holiname} ({holidate}) already in list!')
        else:
            aHoliday = Holiday(name = holiname, date = holidate)
            self.innerHolidays.append(aHoliday)     # Use innerHolidays.append to add holiday 
            print(f'Success! {holiname} ({holidate}) is added to the list.')      # print to the user that you added a holiday  

    def findHoliday(self, holiname, holidate):
        checkHoliday = Holiday(name = holiname, date = holidate)
        if checkHoliday in self.innerHolidays:
            return True     #Return holiday        
        else:
            return False
            
    def removeHoliday(self):
        print("Remove A Holiday")
        print("====================")
        isValid = False
        holiname = str(input("Holiday Name:    ")).title()
        while not isValid:
            holidate = input("Holiday Date (yyyy-mm-dd):    ")
            try:
                valid_date = datetime.strptime(holidate, '%Y-%m-%d').date()
                if (date(2020, 1, 1) <= valid_date <= date(2024, 12, 31)):
                    isValid = True
                else:
                    print('Date out of range!')
            except:
                print('Invalid date!')  
                continue
        if self.findHoliday(holiname, holidate) == True:     #don't let duplicates in
            print(f'Success. {holiname} ({holidate}) is removed from holiday list.')      # print to the user that you added a holiday
            isValid= True
            checkHoliday = Holiday(name = holiname, date = holidate)
            self.innerHolidays.pop(self.innerHolidays.index(checkHoliday))
        else:
            print(f'{holiname} ({holidate}) not found.')

    def readJSON(self): 
        fileLocation = open('holidays.json')
        holigiven = json.load(fileLocation)['holidays']
        for k in holigiven:
            aHoliday = Holiday(k['name'], datetime.strptime(k['date'], '%Y-%m-%d'))
            self.innerHolidays.append(aHoliday)

    def saveToJSON(self):
        holidays = list(map(lambda h: {"date": h.date.strftime('%Y-%m-%d'), "name": h.name}, self.innerHolidays))
        jsonString = json.dumps({"holidays":holidays}, indent = 1)
        jsonFile = open("allholidays.json",'w')
        jsonFile.write(jsonString)
        jsonFile.close
        print('Save successful. New file named allholidays.json is created.')
        
    def scrapeHolidays(self): 
        for i in range(2020, 2025):     # Remember, 2 previous years, current year, and 2  years into the future. 
            html = getHTML(f"https://www.timeanddate.com/holidays/us/{i}")      # Scrape Holidays from https://www.timeanddate.com/holidays/us/ 
            soup = BeautifulSoup(html, 'html.parser')
            tablebody = soup.find('table').find('tbody') 
            for j in tablebody.find_all_next('tr'):
                holidate = str(j.find('th', attrs = {'class':'nw'}))
                holidate =(f'{holidate[15:-5]} {i}')
                holiname = str(j.find('a'))
                holiname = holiname[holiname.find('>')+1:-4]
                if holidate != ' 2020' and holiname != '':     #getting blanks in same place in both date and name for some reason. so this takes care of that
                    holidate=datetime.strptime(holidate,'%b %d %Y') #strp separates, strf re-arranges
                    aHoliday = Holiday(name = holiname, date = holidate)
                    if aHoliday not in self.innerHolidays:     #don't let duplicates in
                        self.innerHolidays.append(aHoliday)
                    else:
                        continue
                else:
                    continue

    def numHolidays(self):
        return len(self.innerHolidays)   # Return the total number of holidays in innerHolidays

    def filterHolidaysByWeek(self, selectYear,selectWeek):
        holidaysinweek = list(filter(lambda aHoliday: aHoliday.date.isocalendar()[0] == int(selectYear) and aHoliday.date.isocalendar()[1] == int(selectWeek), self.innerHolidays))
        for i in holidaysinweek:
            print(i)


    def viewCurrentWeek(self):
        print('View Holidays')
        print("====================")
        temp = []
        selectYear = self.get_year("Which year?:    ")
        selectWeek = self.get_week("Which week?:    ")
        if selectWeek == datetime.today().isocalendar()[1] and selectYear == datetime.today().isocalendar()[0]:
            selectWeather = input(f"Would you like to see the weather for current week?[y/n]")
            if selectWeather == "y":  
                url = f'http://api.openweathermap.org/data/2.5/forecast?lat=42.937084&lon=-75.6107&appid={APIKey}'
                yearToDateWeather = getJson(url)
                emptyWeather = []
                newWeather = []
                for d in yearToDateWeather["list"]:
                    dw = d['weather'][0]
                    dd = dw['description']
                    dt = d['dt_txt']
                    dt = datetime.strftime(datetime.strptime(dt,'%Y-%m-%d %H:%M:%S'), '%Y-%m-%d') #strp separates, strf re-arranges
                    emptyWeather.append({dt :dd})
                newWeather.append(emptyWeather[0])
                newWeather.append(emptyWeather[7])
                newWeather.append(emptyWeather[15])
                newWeather.append(emptyWeather[23])
                newWeather.append(emptyWeather[31])
                newWeather.append(emptyWeather[39])
                print("This week's weather:")
                for i in range(len(newWeather)):
                    print(newWeather[i])
                print("This week's holidays:")
                self.filterHolidaysByWeek(selectYear,selectWeek)
            else:
                self.filterHolidaysByWeek(selectYear,selectWeek)
        else:
            self.filterHolidaysByWeek(selectYear,selectWeek)

    def display_main_menu(self):
        print("\nMain Menu\n")
        print("====================")
        menu_options = {1: 'Add A Holiday', 2: 'Remove A Holiday', 3: 'Save Holiday List', 4: 'View Holidays', 5: 'Exit'}
        for i in menu_options:
            print(f'{i}. {menu_options[i]}')

    def get_menu_int(self, prompt):
        my_int = 0
        is_Valid = False
        while not is_Valid:
            try:
                my_int = int(input(prompt))
                if my_int <1 or my_int>5:
                    raise ValueError
                else:
                    return my_int
            except ValueError:
                print('Invalid Integer, try again. Select menu option from 1 to 5.   ')
        return my_int

    def get_year(self, prompt):
        my_int = 0
        is_Valid = False
        while not is_Valid:
            try:
                my_int = int(input(prompt))
                if my_int <2020 or my_int>2024:
                    raise ValueError
                else:
                    return my_int
            except ValueError:
                print('Invalid Integer, try again. Select year between 2020 and 2024.   ')
        return my_int

    def get_week(self, prompt):
        my_int = 0
        is_Valid = False
        while not is_Valid:
            try:
                my_int = int(input(prompt))
                if my_int <1 or my_int>52:
                    raise ValueError
                else:
                    return my_int
            except ValueError:
                print('Invalid Integer, try again. Select week number between 1 and 52.   ')
        return my_int

def main():
    holidays = HolidayList()
    holidays.scrapeHolidays()
    holidays.readJSON()
    print(f'Welcome to the Holiday Manager!\nThere are {holidays.numHolidays()} holidays already added to the list.')

    exit_choice = 'y'
    while exit_choice != 'n':
        holidays.display_main_menu()
        menu_choice = holidays.get_menu_int('Select menu option from 1 to 5.     ')
        if menu_choice == 1:
            holidays.addHoliday()
        elif menu_choice ==2:
            holidays.removeHoliday()
        elif menu_choice ==3:
            holidays.saveToJSON()
        elif menu_choice ==4:
            holidays.viewCurrentWeek()
        elif menu_choice ==5:
            print('Exit')
            print("====================")
            print("Any unsaved changes will be lost.")
        exit_choice = input('Back to main menu? Any unsaved changes will be lost. [y/n]     ')
    print('Goodbye!') 



if __name__ == "__main__":
    main();



