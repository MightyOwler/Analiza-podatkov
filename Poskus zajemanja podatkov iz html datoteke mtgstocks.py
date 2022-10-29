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
PRVI_SET = 45
ZADNJI_SET = 46

indeksi_setov_ki_obstajajo = [45, 46]

debug_mode_branje_iz_lokalnih_datotek = True

vzorec_bloka = re.compile(
    r'<td><mtg-set-icon.*?'
    r'</tr',
    flags=re.DOTALL
)

vzorec_karte = re.compile(
    r'<td><mtg-set-icon.*?>.*?<i _ngcontent.*? class="ss ss-fw ss-(?P<set>.+?)\b( ss-.*?)?"></i><!----></mtg-set-icon>'
    r'<a href="/prints/(?P<id_karte>\d*).*?">'
    r'(?P<ime>.*?)'
    r'</a>.*?</td>.*?<td> (?P<redkost>.*?) </td>'
    r'.*?<td class="text-end"> \$(?P<povprecna_cena>.*?) </td>(<\!---->)+(<td class="text-end">.*?</td>.*?<td class="text-end"> \$(?P<povprecna_cena_foil>.*?) </td>.*?<td class="text-end">.*?</td>)?',  
    flags=re.DOTALL
    )

def izloci_podatke_o_kartah(blok):
    karta = vzorec_karte.search(blok).groupdict()
    karta['id_karte'] = int(karta['id_karte'])
    karta['ime'] = karta['ime'].strip()
    karta['set'] = karta['set'].upper()
    karta['redkost'] = karta["redkost"].strip()
    karta['povprecna_cena'] = karta["povprecna_cena"]
    karta['povprecna_cena_foil'] = karta["povprecna_cena_foil"]

    return karta

def pridobi_ustrezno_ime_lokalne_datoteke(st_strani):
    return f"Podatki o kartah/Karte iz seta st. {st_strani}.html"

  


# Najprej poradiramo csv in json datoteki
# with open("karte.csv", "w") as dat:
#     pass

# with open("karte.json", "w") as dat:
#     pass


# for st_strani in range(PRVI_SET, ZADNJI_SET + 1):
#     url = (
#         f'https://www.mtgstocks.com/sets/{st_strani}' 
#     )
#     print(f"\n Zajemam {url}\n")
#     driver.get(url)
#     time.sleep(1)
    
#     # response = requests.post(url, allow_redirects=False, timeout=5, headers={
#     #     # "Accept-Language": "sl-si"
#     # })
#     vsebina = driver.page_source
#     naslov_strani = driver.title
    
#     stevilo_podstrani_s_kartami = vsebina.count("pagination-page page-item")
#     st_besed_Market_na_strani = vsebina.count(">Market<")
    
#     print("Naslov strani:", naslov_strani)
    
#     # with open("pomozna_datoteka_za_pregledovanje_zadnje_vsebine.txt", "w") as dat:
#     #     dat.write(vsebina)    
    
#     if naslov_strani in ["File not found - MTGStocks"]:
#         print(f'\n Stran št. {st_strani} ni dosegljiva.\n')
#     else:
#         print(f'\n Stran št. {st_strani} JE dosegljiva.\n')
#         indeksi_setov_ki_obstajajo.append(st_strani)
#         with open(pridobi_ustrezno_ime_lokalne_datoteke(st_strani), 'w') as dat:
#             if "Art Series:" in naslov_strani or "From the Vault:" in naslov_strani or st_besed_Market_na_strani == 0:
#                 continue
#             else:
#                 driver.find_element(by=By.XPATH, value = "//*[text() = 'Market']//..").click()
            
#             for podstran in range(1, stevilo_podstrani_s_kartami + 1):
#                 driver.find_element(by=By.XPATH, value = f"//*[contains(@class, 'pagination-page page-item')][{podstran}]//a").click()
#                 time.sleep(1)
#                 print(f"Pobrana {podstran}. podstran")
#                 dat.write(driver.page_source)

# with open("pomozna_datoteka_za_pravilne_indekse.txt", "w") as dat:
#     dat.write(indeksi_setov_ki_obstajajo)  


# Delujoče zajemanje podatkov setov s spletne strani, treba bo še zajeti podatke posameznih kart
# Spodnjo kodo se da izboljšati, karte damo ven, nato pa samo enkrat odpremo json in csv datoteki

karte = []
for st_seta in indeksi_setov_ki_obstajajo:
    
    stetje = 0
    with open(f"Podatki o kartah/Karte iz seta st. {st_seta}.html", "r") as f:
        print(f"Berem podatke kart iz seta #{st_seta}")
        
        
        vsebina = f.read()
        
        for blok in vzorec_bloka.finditer(vsebina):
            stetje += 1
            
            if debug_mode_branje_iz_lokalnih_datotek:
                print(stetje)
                print(blok.group(0))
                print(vzorec_karte.search(blok.group(0)).groupdict())
            
            karte.append(izloci_podatke_o_kartah(blok.group(0)))

with open("karte.json", "a") as dat:
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
        