import re
import requests
import csv
import json

debug_mode = True

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

print(vzorec_karte)

def izloci_podatke_o_kartah(blok):
    karta = vzorec_karte.search(blok).groupdict()
    karta['id_karte'] = int(karta['id_karte'])
    karta['ime'] = karta['ime'].strip()
    karta['set'] = karta['set'].upper()
    karta['redkost'] = karta["redkost"].strip()
    karta['povprecna_cena'] = karta["povprecna_cena"].strip()
    karta['povprecna_cena_foil'] = karta["povprecna_cena_foil"].strip()

    return karta

karte = []
stetje = 0

with open("Innistrad_ Crimson Vow - MTGStocks.txt", "r") as f:
    vsebina = f.read()
    for blok in vzorec_bloka.finditer(vsebina):
        stetje += 1
        
        if debug_mode:
            print(stetje)
            print(blok.group(0))
            print(vzorec_karte.search(blok.group(0)))
        
        karte.append(izloci_podatke_o_kartah(blok.group(0)))
        

with open("karte.json", "w") as dat:
    json.dump(karte, dat, indent=4, ensure_ascii=False)
    

with open("karte.csv", "w") as dat:
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
    



    



 