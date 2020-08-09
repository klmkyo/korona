from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
import scipy.interpolate as si
from pprint import pprint
import urllib.request
import time
from slugify import slugify
import requests
import base64
import csv
import json
import os

def downloadFile(docid, cookies, location):
    """
    cookies = {
    '.AspNetCore.Antiforgery.ylPDrIszQPI': str(a['value']),
    'ARRAffinity': str(d['value']),
    'visid_incap_2280950': str(e['value']),
    'incap_ses_408_2280950': str(f['value']),
    '.AspNetCore.Cookies': str(c['value']),
    '.AspNetCore.Session': str(b['value']),
    }"""

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
    with open(location, 'w') as f:
        f.write(data)
        if os.stat(location).st_size > 1024 * 10:
            success = 1
        else:
            print(str(line) + ': ' + '[Error] Próbowano pobrać, jednak pobrany plik jest podejrzanie małego rozmiaru {} ({}, {})'.format(name, pesel, barcode))
            success = 0
    return(success)

browser = webdriver.Firefox()
browser.install_addon("/home/klmkyo/korona/buster_captcha_solver_for_humans-1.0.1-an+fx.xpi")

with open('dane.txt', 'r') as f:
    raw = f.readlines()
dane = []

for line in raw:
    if not line.startswith('#'):
        x = line.split(';')
        x[1] = x[1].rstrip('\n')
        dane.append(x)
    
pprint(dane)

people = []

processed = []

for line, x in enumerate(dane):
    try:
        person = {}
        browser.get('https://wyniki.diag.pl/')

        barcode = x[0]
        person['Kod materiału'] = barcode
        bdate = x[1]
        
        day=bdate[4:6]
        month=bdate[2:4]
        year=bdate[:2]

        if int(year)<20: insert = 20
        else: insert = 19
        
        if insert == 20:
            month = str(int(month) - 20)

        bdate = day+month+str(insert)+year
        
        person['Data Urodzenia'] = '{}/{}/{}{}'.format(day,month,insert,year)

        elem = browser.find_element(By.ID, 'Barcode')
        elem.send_keys(barcode + Keys.RETURN)
        
        elem = browser.find_element(By.ID, 'BirthdaySingleOrderLoginInput')
        elem.send_keys(bdate + Keys.RETURN)
        
        try: browser.find_element(By.ID, 'solver-button').click()
        except: pass
        
        swait = WebDriverWait(browser, 5)
        try:
            swait.until(lambda browser: browser.find_element(By.ID, 'PESEL').text)
        except:
            print(str(line) + ': ' + '[Error] Błędne dane ' + barcode + ' ' + x[1])
        
        
        a = browser.get_cookie('.AspNetCore.Antiforgery.ylPDrIszQPI')
        b = browser.get_cookie('.AspNetCore.Session')
        c = browser.get_cookie('.AspNetCore.Cookies')
        d = browser.get_cookie('ARRAffinity')
        e = browser.get_cookie('visid_incap_2280950')
        f = browser.get_cookie('incap_ses_408_2280950')
        
        cookies = browser.get_cookies()

        c = {}
        for cookie in cookies:
            c[cookie['name']] = cookie['value']
            
        
        name = browser.find_element(By.ID, 'PatientNameAndSurname').text
        imie, nazwisko = name.split(' ')
        person['Imię'] = imie
        person['Nazwisko'] = nazwisko
        
        pesel = browser.find_element(By.ID, 'PESEL').text
        person['PESEL'] = pesel
        
        try:
            rwait = WebDriverWait(browser, 1.5)
            rwait.until(lambda browser: browser.find_element(By.XPATH, '/html/body/main/div[3]/section[1]/div[5]/div/div[2]/div[2]/div[2]/div/span').text)
            wynik = browser.find_element(By.XPATH, '/html/body/main/div[3]/section[1]/div[5]/div/div[2]/div[2]/div[2]/div/span').text
            person['Wynik badania'] = wynik
        except:
            person['Wynik badania'] = 'Niedostępny'
            pass
        
        if person['Wynik badania'] == 'Niedostępny':
            print(str(line) + ': ' + '[Alert] Brak wyników dla {} ({}, {})!'.format(name, pesel, barcode))
            continue
        else:
            try:
                dwait = WebDriverWait(browser, 3)
                dwait.until(lambda browser: browser.find_element(By.XPATH, '/html/body/main/div[3]/section[2]/div[3]/div/div[2]/div/div[3]/button'))
                print(str(line) + ': ' + '[Wynik] ' + name + " - " + wynik)
                browser.find_element(By.XPATH, '/html/body/main/div[3]/section[2]/div[3]/div/div[2]/div/div[3]/button')
                docid = browser.find_element(By.XPATH, '/html/body/main/div[3]/section[2]/div[3]/div/div[2]/div/div[3]/button').get_attribute('data-docid')
                
                for i in range(0,3):
                    if downloadFile(docid, c, 'wyniki/' + wynik + '/' + slugify(name)+'.pdf'):
                        people.append(person)
                        processed.append(x[0] + ';' + x[1])
                        break
                
            except:
                print(str(line) + ': ' + '[Error] Pobieranie wyników dla {} ({}, {}) nie powiodło się!'.format(name, pesel, barcode))
    except:
        print(str(line) + ': ' + '[Error] Wystąpił nieznany błąd przy {}'.format(x[0]))
lines = []
with open('dane.txt', 'r+') as f:
    for line in f.readlines():
        if line.rstrip('\n') in processed:
            name = ''
            for person in people:
                if line.rstrip('\n').split(';')[0] == person['Kod materiału']:
                    name=person['Nazwisko'] + person['Imię']
            line = "#" + line.rstrip('\n') + "\t" + name + '\n'
        lines.append(line)
    
with open('dane.txt', 'w') as f:
    f.writelines(lines)

with open('export' + str(time.time()) + '.json', 'w') as j:
    j.write(json.dumps(people, ensure_ascii=False))

rows = []
try:
    with open('output.csv', 'r') as read: 
        reader = csv.reader(read)
        for row in reader:
            rows.append(row)
except:
    pass
    
with open('output.csv', 'a+') as output:
    writer = csv.writer(output)
    for person in people:
        isAlready = False
        if rows:
            for x in rows: 
                if person['Kod materiału'] in x: isAlready = True
        if not isAlready:
            v = []
            for key, value in person.items():
                v.append(value)
            writer.writerows([v])