import requests
from bs4 import BeautifulSoup
import sqlite3
from sqlite3 import Error
import time

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
        :param db_file: database file
        :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
 
    return conn

def saveToDB(row):
    conn = create_connection('test.db')
    sql = ''' INSERT INTO SCRAPED_DATA(TALOS_REPORT_ID, VENDOR, REPORT_DATE)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, row)
    conn.commit()
    conn.close()
    return cur.lastrowid

def processTableData(i):
    # Each element is of the form '\n              TALOS-2019-0886\n            '
    # So we remove the '\n' and whitespaces
    data = i.text.replace('\n', '')
    return data.strip()


def parseTable(table):
    table_rows = table[0].find_all('tr')

    #The first row is empty, since it has table header (th) tags, not table data (td) tags.
    table_rows.pop(0)

    for tr in table_rows:
        td = tr.find_all('td')
        row = [processTableData(i) for i in td]
        saveToDB(row)
    return True

def get_count():
    url = "https://talosintelligence.com/"

    # Request with fake header, talosintelligence bans if user agent is not correct. Copied from my browser
    page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:70.0) Gecko/20100101 Firefox/70.0'})
    soup = BeautifulSoup(page.content, 'html5lib')
    table = soup.select('table.home-preview-table:nth-child(4)')
    #table = soup.find('table', attrs = {'class':'home-preview-table'}) 

    return parseTable(table)

def createTableIfNotExists():
    conn = create_connection('test.db')
    print ("Opened database successfully")
    conn.execute('''CREATE TABLE IF NOT EXISTS SCRAPED_DATA
         (ID INTEGER PRIMARY KEY,
         TALOS_REPORT_ID           TEXT    NOT NULL,
         VENDOR            TEXT     NOT NULL,
         REPORT_DATE        TEXT,
         CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP);''')
    print ("Table created successfully")
    conn.close()

def main():
    createTableIfNotExists()
    while True:
        print(get_count())
        time.sleep(60)

if __name__== "__main__":
  main()