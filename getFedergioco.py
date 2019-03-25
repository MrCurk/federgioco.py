# -*- coding: utf-8 -*-
import json
import sys
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import cx_Oracle


########################################################################################################################
# CLASS
########################################################################################################################
### CASINO CLASS
class Casino:
    def __init__(self, name, yearMonthr):
        self.name = name
        self.yearMonth = yearMonthr
        self.data = dict()

    def printData(self):
        print("name={0} monthYear={1}, Data{2}".format(self.name, self.yearMonth, self.data))


########################################################################################################################
# FUNCTION
########################################################################################################################
### function to generate load id(current unix time)
def generateLoadId():
    return int(datetime.now().timestamp())


########################################################################################################################
### function to generate monthYear
def toYearMonth(month, year):
    yearMonth = None
    if month < 10:
        yearMonth = str(year) + "0" + str(month)
    else:
        yearMonth = str(year) + str(month)
    return yearMonth


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
### function to convert string 12,111 value to integer
def string2Integer(value):
    # remove , from data
    data = value.replace(',', '')
    # remove . from data

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
    # create casinos list
    casinos = list()

    yearMonth = toYearMonth(month, year)

    url = "http://www.federgioco.it/ajax_dati_comparati.php?periodo={MONTH}&anno={YEAR}".format(
        MONTH=monthDictionarie[month], YEAR=year)

    # get html page data

    source = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source, "lxml")
    if soup.find(text="DATI NON PRESENTI"):
        printLog("ERR - NON DATA FOUND - EXIT PROGRAM", yearMonth)
        exit()

    # get table from html page
    table = soup.table

    # get table header
    table_header = table.find_all("th")
    # create casinos list
    for singleColumn in table_header:
        casinos.append(Casino(singleColumn.text, yearMonth))

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
                if gameName == "INGRESSI":  # INGRESSI has string format 11,111
                    casinos[i - 1].data[gameName] = string2Integer(singleColumn.text)
                else:  # other data fromat is 11.111,11
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

monthNumber = None
yearNumber = None
monthNumberLast = None
yearNumberLast = None

# get arguments and set month, year, config file
if len(sys.argv) <= 2:  # without argument or with 1 argument
    # date set to last month
    dateToGetData = (datetime.now().replace(day=1) - timedelta(days=1))
    monthNumber = int(dateToGetData.strftime('%m'))
    yearNumber = int(dateToGetData.strftime('%Y'))

    # dateLast set to -2 month
    if monthNumber == 1:
        monthNumberLast = 12
        yearNumberLast = yearNumber - 1
    else:
        monthNumberLast = monthNumber - 1
        yearNumberLast = yearNumber
else:  # with config argument and month and year
    monthNumber = int(sys.argv[2])
    yearNumber = int(sys.argv[3])

# create casinos list
casinos = list()

# get casino data for  month -2  from web
if monthNumberLast is not None and yearNumberLast is not None:
    casinos.append(fetchCasinoMonthData(monthNumberLast, yearNumberLast))

# get casino data for specific month year from web
casinos.append(fetchCasinoMonthData(monthNumber, yearNumber))

# connect to db, when not in test mode
con = None
cursor = None
if not test_mode_no_db:
    con = cx_Oracle.connect(connection_string)
    cursor = con.cursor()

for casinoMonthData in casinos:
    # loop through list of cities weather
    for item in casinoMonthData:
        # inserting into db
        if not test_mode_no_db:
            printLog("inserting data ", item.name, item.yearMonth)
            cursor.callproc('ADD_ITALY_CASINO_DATA',
                            [loadId, item.yearMonth, item.name,
                             item.data["INGRESSI"],
                             item.data["Totale Introiti Lordi"],
                             item.data["Roulette Francese"],
                             item.data["Fairoulette"],
                             item.data["Trente et Quarante"],
                             item.data["Chemin de Fer"],
                             item.data["Poker"],
                             item.data["Texas Hold'Em "],
                             item.data["Roulette Americana"],
                             item.data["Black Jack"],
                             item.data["Craps"],
                             item.data["Punto Banco"],
                             item.data["Slot Machines"],
                             item.data["Altri"]])
            print()

            printLog("End *****************", item.name)
            print()
        # testing mode only print
        else:
            # test print
            # item.printData()
            print(loadId, item.yearMonth, item.name,
                  item.data["INGRESSI"],
                  item.data["Totale Introiti Lordi"],
                  item.data["Roulette Francese"],
                  item.data["Fairoulette"],
                  item.data["Trente et Quarante"],
                  item.data["Chemin de Fer"],
                  item.data["Poker"],
                  item.data["Texas Hold'Em "],
                  item.data["Roulette Americana"],
                  item.data["Black Jack"],
                  item.data["Craps"],
                  item.data["Punto Banco"],
                  item.data["Slot Machines"],
                  item.data["Altri"])

# close db connection
if not test_mode_no_db:
    con.close()
