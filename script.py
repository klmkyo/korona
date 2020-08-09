#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pprint import pprint
import urllib.request
import time
import requests
import base64
import csv
import json
import os
import sys

if len(sys.argv) == 1:
    print('Użycie: skrypt.py <plik do odczytu danych> <plik do zapisania arkusza>')
    exit(1)

if sys.argv[1] in ['--help', '-h']:
    print('Użycie: skrypt.py <plik do odczytu danych> <plik do zapisania arkusza>')
    exit(1)
    
    
#ten plik miał nie opuszczać mojego komputera więc niestety nie starałem się jakoś pisać czytelnie kod
#w każdym razie Good Luck w czytaniu mojego bałaganu!


def downloadFile(docid, cookies, location):
    """Pobiera wyniki

    Args:
        docid (string): ID dokumentu
        cookies (list)
        location (string): miejsce zapisania dokumentu
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Upgrade-Insecure-Requests': '1',
        'Connection': 'keep-alive',
    }

    params = (
        ('documentid', str(docid)),
    )

    rawresponse = requests.get('https://wyniki.diag.pl/Document/GetPdf', headers=headers, params=params, cookies=cookies)
    
    data = rawresponse.text
    
    #zapisz pobrany plik PDF
    with open(location, 'w', encoding='UTF-8') as f:
        f.write(data)
        #czasami pobrany plik waży 0b (jest pusty)
        #aby temu zapobiec poniżej znajduję się check czy plik jest większy od 100kB (ponieważ typowy plik pdf z tej strony waży ~230kB)
        if os.stat(location).st_size > 1024 * 10:
            success = 1
        else:
            success = 0
    return(success)


#zainicjuj selenium, Firefox działa w tym programie o wiele lepiej niż chrome więc z niego korzystam
browser = webdriver.Firefox()

plikDoWczytania = sys.argv[1]
plikDoZapisaniaArkusza = sys.argv[2]

#stwórz foldery (jeśli jeszcze nie istnieją) do których będą pobierane wyniki
try:
    os.mkdir('wyniki')
    os.mkdir('wyniki/Pozytywny')
    os.mkdir('wyniki/Negatywny')
    os.mkdir('wyniki/Nierozstrzygający')
except:
    pass



#odczytaj kod oraz 6 pierwsze cyfr PESEL'U wymagane do zalogowania na wyniki.diag
with open(plikDoWczytania, 'r') as f:
    raw = f.readlines()
dane = []

#podziel odczytane linijki na kod i 6 cyfr PESEL'U
for line in raw:
    if len(line) > 1:
        if not line.startswith('#'):
            x = line.split(';')
            x[1] = x[1].rstrip('\n')
            dane.append(x)

#wyświetl wczytane dane
pprint(dane)



#to jest lista ludzi, której elementami są słowniki ludzi. Te słowniki zawierają imię, PESEL, wyniki badań itp.
#pod koniec programu słowniki te zostaną zapisane do arkusza CSV
people = []

#lista ludzi których wyniki udało się skutecznie pobrać
processed = []



#na każdą osobę z pliku wejdż na wyniki.diag.pl, zaloguj się jako ta osoba, a następnie pobierz jej plik
for line, x in enumerate(dane):
    try:
        #stwórz objekt osoby który zostanie dodany potem do people jeśli wszystko zadziała
        person = {}
        browser.get('https://wyniki.diag.pl/')

        #get kodu kreskowego
        barcode = x[0]
        person['Kod materiału'] = barcode
        
        #przekształcanie pierwszych 6 cyfr peselu na datę urodzenia
        bdate = x[1]
        
        day=bdate[4:6]
        month=bdate[2:4]
        year=bdate[:2]

        if int(year)<20: insert = 20
        else: insert = 19
        
        if insert == 20:
            month = str(int(month) - 20).zfill(2)

        bdate = day+month+str(insert)+year
        
        person['Data Urodzenia'] = '{}/{}/{}{}'.format(day,month,insert,year)

        #wpisz wcześniej użyte dane na stronę
        elem = browser.find_element(By.ID, 'Barcode')
        elem.send_keys(barcode + Keys.RETURN)
        
        elem = browser.find_element(By.ID, 'BirthdaySingleOrderLoginInput')
        elem.send_keys(bdate + Keys.RETURN)
        
        try: browser.find_element(By.ID, 'solver-button').click()
        except: pass
        
        #zaloguj się, jeśli to się nie powiedzie (najczęściej z powodu błędnie podanych danych) to przerwij
        swait = WebDriverWait(browser, 5)
        try:
            swait.until(lambda browser: browser.find_element(By.ID, 'PESEL').text)
        except:
            print(str(line) + ': ' + '[Error] Błędne dane (kod: ' + barcode + ', PESEL: ' + x[1] + ')')
        
        #zdobądź pliki cookie niezbędne do pobrania pliku
        cookies = browser.get_cookies()

        c = {}
        for cookie in cookies:
            c[cookie['name']] = cookie['value']
            
        #uzyskaj dane o osobie
        name = browser.find_element(By.ID, 'PatientNameAndSurname').text
        imie, nazwisko = name.split(' ')
        person['Imię'] = imie
        person['Nazwisko'] = nazwisko
        
        pesel = browser.find_element(By.ID, 'PESEL').text
        person['PESEL'] = pesel.zfill(11)
        
        #sprawdź czy wynik badań jest dostępny
        try:
            rwait = WebDriverWait(browser, 1.5)
            rwait.until(lambda browser: browser.find_element(By.XPATH, '/html/body/main/div[3]/section[1]/div[5]/div/div[2]/div[2]/div[2]/div/span').text)
            wynik = browser.find_element(By.XPATH, '/html/body/main/div[3]/section[1]/div[5]/div/div[2]/div[2]/div[2]/div/span').text
            person['Wynik badania'] = wynik
        except:
            person['Wynik badania'] = 'Niedostępny'
            pass
        
        #pobierz plik jeśli są wyniki badań
        if person['Wynik badania'] == 'Niedostępny':
            print(str(line) + ': ' + '[Alert] Brak wyników dla {} (kod: {}, PESEL: {}!'.format(name, barcode, pesel))
            continue
        else:
            try:
                dwait = WebDriverWait(browser, 3)
                dwait.until(lambda browser: browser.find_element(By.XPATH, '/html/body/main/div[3]/section[2]/div[3]/div/div[2]/div/div[3]/button'))
                print(str(line) + ': ' + '[Wynik] ' + name + " - " + wynik)
                browser.find_element(By.XPATH, '/html/body/main/div[3]/section[2]/div[3]/div/div[2]/div/div[3]/button')
                docid = browser.find_element(By.XPATH, '/html/body/main/div[3]/section[2]/div[3]/div/div[2]/div/div[3]/button').get_attribute('data-docid')
                
                #spróbuj pobrać plik, maksymalnie 3 razy
                for i in range(0,3):
                    if downloadFile(docid, c, 'wyniki/' + wynik + '/' + person['Nazwisko'].capitalize() + ' ' + person['Imię'].capitalize() + ' ' + person['PESEL']+'.pdf'):
                        people.append(person)
                        processed.append(x[0] + ';' + x[1])
                        break
                
            except:
                print("Unexpected error:", sys.exc_info()[1])
                print(str(line) + ': ' + '[Error] Pobieranie wyników dla {} (kod: {}, PESEL: {}) nie powiodło się!'.format(name, barcode, pesel))
    except:
        print(str(line) + ': ' + '[Error] Wystąpił nieznany błąd przy kodzie {}'.format(x[0]))
        

#zaznacz ludzi w pliku których plik PDF został już pobrany (aby się nie powtarzać)
lines = []
with open(plikDoWczytania, 'r+') as f:
    for line in f.readlines():
        if line.rstrip('\n') in processed:
            name = ''
            for person in people:
                if line.rstrip('\n').split(';')[0] == person['Kod materiału']:
                    name=person['Nazwisko'] + person['Imię']
            line = "#" + line.rstrip('\n') + "\t" + name + '\n'
        lines.append(line)
    
with open(plikDoWczytania, 'w') as f:
    f.writelines(lines)


#zapisywanie do arkusza
rows = []
try:
    with open(plikDoZapisaniaArkusza, 'r') as read: 
        reader = csv.reader(read)
        for row in reader:
            rows.append(row)
except:
    pass
    
with open(plikDoZapisaniaArkusza, 'a+') as output:
    writer = csv.writer(output)
    for person in people:
        isAlready = False
        #zabezpieczenie przed duplikatami osób w akruszu
        if rows:
            for x in rows: 
                if person['Kod materiału'] in x: isAlready = True
        if not isAlready:
            v = []
            for key, value in person.items():
                v.append(value)
            writer.writerows([v])