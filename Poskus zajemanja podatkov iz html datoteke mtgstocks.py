import re
import requests
import csv
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
    
# Tole dvoje je treba, da se Chrome sproti ne odpira
chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome("chromedriver.exe", options=chrome_options)


# Ko potegnemo podatke s strani, poberemo podatke prvih 50 kart iz vsakega seta.
# Začnemo šteti pri prvem, končamo pri zadnjem.
PRVI_SET = 810
ZADNJI_SET = 812

debug_mode = False

vzorec_bloka = re.compile(
    r'<td><mtg-set-icon.*?'
    r'</tr',
    flags=re.DOTALL
)

vzorec_karte = re.compile(
    r'<td><mtg-set-icon.*?>.*?<i _ngcontent.*? class="ss ss-fw ss-(?P<set>.{3})( ss-.*?)?"></i><!----></mtg-set-icon>'
    r'<a href="/prints/(?P<id_karte>\d*).*?">'
    r'(?P<ime>.*?)'
    r'</a>.*?</td>.*?<td> (?P<redkost>.*?) </td>'
    r'.*?<td class="text-end"> (?P<povprecna_cena>.*?) </td>'
    r'.*?<td class="text-end">.*?</td>'
    r'.*?<td class="text-end"> (?P<povprecna_cena_foil>.*?) </td>'
    r'.*?<td class="text-end">.*?</td>',
    flags=re.DOTALL
    )

def izloci_podatke_o_kartah(blok):
    karta = vzorec_karte.search(blok).groupdict()
    karta['id_karte'] = int(karta['id_karte'])
    karta['ime'] = karta['ime'].strip()
    karta['set'] = karta['set'].upper()
    karta['redkost'] = karta["redkost"].strip()
    karta['povprecna_cena'] = karta["povprecna_cena"].strip()
    karta['povprecna_cena_foil'] = karta["povprecna_cena_foil"].strip()

    return karta

def pridobi_ustrezno_ime_lokalne_datoteke(st_strani):
    return f"Podatki o kartah/Karte iz seta st. {st_strani}.html"


# Najprej poradiramo csv datoteko
with open("karte.csv", "w") as dat:
    pass


for st_strani in range(PRVI_SET, ZADNJI_SET):
    url = (
        f'https://www.mtgstocks.com/sets/{st_strani}' 
    )
    print(f"Zajemam {url}")
    driver.get(url)
    driver.find_element(by=By.XPATH, value='//*[@id="overview"]/mtg-sets-overview/data-table/div[2]/div/div/table/thead/tr[1]/th[3]').click()
    # response = requests.post(url, allow_redirects=False, timeout=5, headers={
    #     # "Accept-Language": "sl-si"
    # })
    vsebina = driver.page_source
    with open(pridobi_ustrezno_ime_lokalne_datoteke(st_strani), 'w') as dat:
        dat.write(vsebina)


# Delujoče zajemanje podatkov setov s spletne strani, treba bo še zajeti podatke posameznih kart

# for st_seta in range(PRVI_SET, ZADNJI_SET):
#     with open(f"Podatki o kartah/Karte iz seta st. {st_seta}.html", "r") as f:
        
#         print(f"Berem podatke kar iz seta #{st_seta}")
#         karte = []
#         stetje = 0
        
#         vsebina = f.read()
#         for blok in vzorec_bloka.finditer(vsebina):
#             stetje += 1
            
#             if debug_mode:
#                 print(stetje)
#                 print(blok.group(0))
            
#             karte.append(izloci_podatke_o_kartah(blok.group(0)))
#             time.sleep(5)
            

    with open("karte.json", "w") as dat:
        json.dump(karte, dat, indent=4, ensure_ascii=False)
        

    with open("karte.csv", "a") as dat:
        writer = csv.DictWriter(dat, [
            "id_karte",
            "ime",
            "set",
            "redkost",
            "povprecna_cena",
            "povprecna_cena_foil",
        ])
        writer.writeheader()
        writer.writerows(karte)
        



    



 