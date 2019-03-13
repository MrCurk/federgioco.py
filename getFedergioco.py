import json
import sys
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import os


########################################################################################################################
# CLASS
########################################################################################################################
### CASINO CLASS
class Casino:
    def __init__(self, name, monthYear):
        self.name = name
        self.monthYear = monthYear
        self.data = dict()

    def printData(self):
        print("name={0} monthYear={1}, Data{2}".format(self.name, self.monthYear, self.data))


########################################################################################################################
# FUNCTION
########################################################################################################################
### function to generate load id(current unix time)
def generateLoadId():
    return int(datetime.now().timestamp())


########################################################################################################################
### function to generate monthYear
def toMonthYear(month, year):
    monthYear = None
    if month < 10:
        monthYear = "0" + str(month) + str(year)
    else:
        monthYear = str(month) + str(year)
    return monthYear


########################################################################################################################
### function to convert string € value to float
def euroString2Float(value):
    # remove €
    data = value.replace(' €', '')
    # remove . from data
    data = data.replace('.', '')
    # substitute , with .
    data = data.replace(',', '.')

    return (data)


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
### function to get data fore specific month
def fetchCasinoMonthData(month, year):
    monthDictionarie = {1: "Gennaio", 2: "Febbraio", 3: "Marzo", 4: "Aprile", 5: "Maggio", 6: "Giugno", 7: "Luglio",
                        8: "Agosto", 9: "Settembre", 10: "Ottobre", 11: "Novembre", 12: "Dicembre"}

    monthYear = toMonthYear(month, year)
    url = "http://www.federgioco.it/ajax_dati_comparati.php?periodo={MONTH}&anno={YEAR}".format(
        MONTH=monthDictionarie[month], YEAR=year)

    # create casinos list
    casinos = list()

    # get html page data
    source = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source, "lxml")

    # get table from html page
    table = soup.table

    # get table header
    table_header = table.find_all("th")
    # create casinos list
    for singleColumn in table_header:
        casinos.append(Casino(singleColumn.text, monthYear))

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
                # first column is game name
                gameName = singleColumn.text
                if gameName == "INGRESSI (numero)":
                    gameName = "INGRESSI"
            else:
                # others columns are data
                casinos[i - 1].data[gameName] = euroString2Float(singleColumn.text)
            i += 1

    return casinos


########################################################################################################################
# string to boolean
def str_to_bool(s):
    if s.upper() == 'TRUE':
        return True
    elif s.upper() == 'FALSE':
        return False
    else:
        raise ValueError


########################################################################################################################
# PROGRAM
########################################################################################################################
##  CONFIG PARAMETERS - geting data from config file
## full path of config file
if len(sys.argv) > 1:
    config_full_path = sys.argv[1]
else:
    config_full_path = None

## read config file
if config_full_path != None:
    config_json = open(config_full_path).read()
else:
    config_json = open("config.json").read()

config_data = json.loads(config_json)

## config proxy
# get proxy data from config
proxyType = config_data["PROXY_TYPE"]
proxy = config_data["PROXY"]
proxyPort = config_data["PROXY_PORT"]
proxyUsername = config_data["PROXY_USERNAME"]
proxyPassword = config_data["PROXY_PASSWORD"]
proxyString = None
# set proxy string
if len(proxyType) > 0:
    if len(proxyUsername) == 0 and len(proxyPassword) == 0:
        proxyString = proxyType + "://" + proxy + ":" + proxyPort
    else:
        proxyString = proxyType + "://" + proxyUsername + ":" + proxyPassword + "@" + proxy + ":" + proxyPort
    # set proxy
    os.environ['http_proxy'] = proxyString
    os.environ['HTTP_PROXY'] = proxyString
    os.environ['https_proxy'] = proxyString
    os.environ['HTTPS_PROXY'] = proxyString

# test mode, without db connection == True
test_mode_no_db = str_to_bool(config_data["test_mode_no_db"])

# connection string
dbTns = config_data["DB_TNS"]
connection_string = None
if len(dbTns) == 0:
    connection_string = config_data["DB_USERNAME"] + "/" + config_data["DB_PASSWORD"]
else:
    connection_string = config_data["DB_USERNAME"] + "/" + config_data["DB_PASSWORD"] + "@" + config_data["DB_TNS"]

########################################################################################################################
# generate load id
loadId = generateLoadId()
casinos = fetchCasinoMonthData(1, 2019)
for item in casinos:
    item.printData()
