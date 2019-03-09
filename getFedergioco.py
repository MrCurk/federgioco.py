import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime


########################################################################################################################
# CLASS
########################################################################################################################
### CASINO CLASS
class Casino:
    def __init__(self, name):
        self.name = name
        self.data = dict()

    def printData(self):
        print("name={0}, {1}".format(self.name, self.data))


########################################################################################################################
# FUNCTION
########################################################################################################################
### function to generate load id(current unix time)
def generateLoadId():
    return int(datetime.now().timestamp())


########################################################################################################################
### function print log
def printLog(text, value=None, value1=None, value2=None, value3=None):
    utcnow = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.now().strftime('%H:%M:%S')
    string4print = None
    if value is None:
        string4print = "{0}({1}) / {2}".format(utcnow, now, text)
    elif value1 is None:
        string4print = "{0}({1}) / {2} / {3}".format(utcnow, now, text, value)
    elif value2 is None:
        string4print = "{0}({1}) / {2} / {3} / {4}".format(utcnow, now, text, value, value1)
    elif value3 is None:
        string4print = "{0}({1}) / {2} / {3} / {4} / {5}".format(utcnow, now, text, value, value1, value2)
    else:
        string4print = "{0}({1}) / {2} / {3} / {4} / {5} / {6}".format(utcnow, now, text, value, value1, value2, value3)

    print(string4print)


########################################################################################################################
# PROGRAM
########################################################################################################################
##  CONFIG PARAMETERS - geting data from config file


########################################################################################################################
# generate load id
loadId = generateLoadId()

# create casinos list
casinos = list()

# get html page data
source = urllib.request.urlopen("http://www.federgioco.it/ajax_dati_comparati.php?periodo=Gennaio&anno=2019").read()
soup = BeautifulSoup(source, "lxml")

# get table from html page
table = soup.table

# get table header
table_header = table.find_all("th")
# create casinos list
for singleColumn in table_header:
    casinos.append(Casino(singleColumn.text))

# remove position 0, "INTROITI DI GIOCO"
del casinos[0]

# get tables rows
table_rows = table.find_all("tr")
# get single row
for singleRow in table_rows:
    # get columns from single row
    columns = singleRow.find_all("td")
    i = 0
    gameName = None
    # get single column from columns
    for singleColumn in columns:
        if i == 0:
            #first column is game name
            gameName = singleColumn.text
        else:
            #others columns are data
            casinos[i - 1].data[gameName] = singleColumn.text
        i += 1


for item in casinos:
    item.printData()
