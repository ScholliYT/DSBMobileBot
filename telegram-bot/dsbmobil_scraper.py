import requests
import sys
from bs4 import BeautifulSoup
import json
import unicodedata
from collections import OrderedDict

URL_PREFIX = "https://iphone.dsbcontrol.de/iPhoneService.svc/DSB";
class DSBMobile:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def auth(self):
        print("authenticating...")
        if(not self.username or not self.password):
            print("no username or password")
            return False

        r = requests.get(URL_PREFIX + "/authid/" + self.username + "/" + self.password)
        self.key = r.json()

        return self.key != "00000000-0000-0000-0000-000000000000"

    def getTimeTables(self):
        r = requests.get(URL_PREFIX + "/timetables/" + self.key)
        timetablesjson = r.json()
        timetables = []
        for tjson in timetablesjson:
            timetable = TimeTable(tjson["ishtml"], tjson["timetabledate"], tjson["timetablegroupname"], tjson["timetabletitle"], tjson["timetableurl"])
            timetables.append(timetable)
        return timetables

class TimeTable:
    def __init__(self, isHtml, date, groupName, title, url):
        self.isHtml = isHtml
        self.date = date
        self.groupName = groupName
        self.title = title
        self.url = url

class SubstitutionTable:
    def __init__(self, date):
        self.date = date
        self.substitutions = []
        self.specialText = ""

class Substitution:
    def __init__(self, classname, text):
        self.classname = classname
        self.text = text

def order_dict(dictionary):
    return {k: order_dict(v) if isinstance(v, dict) else v
            for k, v in sorted(dictionary.items())}

def getNewData(dsbmobile):
    

    tables = []
    for t in filter(lambda x: x.groupName=="Pläne", dsbmobile.getTimeTables()):
        print(t.title + ": " + t.url)
        r = requests.get(t.url)
        # TODO: remove "\xa0" from stirng
        soup = BeautifulSoup(r.content, "html.parser")
        legend = soup.find("legend")
        if(legend):
            date = legend.text.strip()
            st = SubstitutionTable(date)
            motd = soup.find("div", attrs={"class": "MessageOfTheDay"})
            if(motd):
                st.specialText = motd.text.strip()
            tables.append(st)


        date_box = soup.find("div", attrs={"class": "dayHeader"})
        if(date_box):
            date = date_box.text.strip() # strip() is used to remove starting and trailing
            st = SubstitutionTable(date)

            table = soup.find("table")
            if(table):
                tbody = table.find("tbody")
                table_data = [[cell.text for cell in row("td")]
                            for row in BeautifulSoup(str(table), "html.parser")("tr")]
                for s in table_data:
                    if(len(s)==1):
                        #append to previous
                        st.substitutions.append(Substitution(st.substitutions[-1].classname, s[0]))
                    else:
                        st.substitutions.append(Substitution(s[0], s[1]))
            else:
                st.specialText = "couldn't find table"
            tables.append(st)


    print("\n")
    groupedTables = {}
    for table in tables:
        groupedTable = {}
        print(table.date)
        if(table.specialText):
            print(table.specialText)

        for s in table.substitutions:
            for classname in s.classname.split(','):
                classname = classname.strip()
                if(classname in groupedTable):
                    groupedTable[classname].append(s.text)
                else:
                    groupedTable[classname] = [s.text]
        groupedTables[table.date] = groupedTable

    groupedTables = order_dict(groupedTables)
    print("\n")
    print(groupedTables)
    return groupedTables