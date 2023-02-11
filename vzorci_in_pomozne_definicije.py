import re
from datetime import datetime
import os

seznam_supertypov = ["Basic", "Legendary", "Ongoing", "Snow", "World"]
problematicni_seti = ["PFNM", "PMTG1", "DD3", "PARL2"]
problematicni_tipi = ["Token", "Emblem"]
color_pentagon = "wubrg"
slovar_uradnih_imenovanj_setov = {'set': {"VAN" : "PVAN", "SLDC": "PHED", "XCLE": "CED", "XICE": "CEI", "RMB1": "FMB1", "XDND" : "AFR", "2E": "LEB", "2U": "2ED", "1E": "LEA", "PO2": "P02", "3ED":"FBB", "3E":"3ED"}}

URL_DO_STRANI_SETOV = "https://scryfall.com/sets"
FILENAME_KARTE_CSV = os.path.join("Podatki", "Tabele_in_JSON", "karte.csv")
FILENAME_KARTE_JSON = os.path.join("Podatki", "Tabele_in_JSON", "karte.json")
FILENAME_KARTE_DODATEK_CSV = os.path.join("Podatki", "Tabele_in_JSON", "dodatni_podatki_o_kartah.csv")
FILENAME_SETI_CSV = os.path.join("Podatki", "Tabele_in_JSON", "seti.csv")
FILENAME_SETI_JSON = os.path.join("Podatki", "Tabele_in_JSON", "seti.json")
FILENAME_POPOLNI_PODATKI_KARTE_JSON = os.path.join("Podatki", "Tabele_in_JSON", "popolni_podatki_o_kartah.json")

# Pomožne funkcije
###########################################################################################


def izlusci_podatke_o_kartah_iz_bloka(blok):
    karta = vzorec_karte.search(blok).groupdict()
    karta['id_karte'] = int(karta['id_karte'])
    karta['ime'] = karta['ime'].strip()
    karta['set'] = karta['set'].upper()
    karta['redkost'] = karta["redkost"].strip()
    karta['povprecna_cena'] = karta["povprecna_cena"]
    karta['povprecna_cena_foil'] = karta["povprecna_cena_foil"]

    return karta


def pridobi_ustrezno_ime_lokalne_datoteke(st_strani):
    return f"Podatki o kartah/Podatki iz setov/Karte iz seta st. {st_strani}.html"


def izlusci_podatke_o_setih(vsebina, vzorec, posamezen_set, podatki_o_kartah):
    if posamezen_set in problematicni_seti:
        # Spodnji seti so problematični, saj so na spletni strani MTGStocks shranjeni pod istim imenom, kljub temu,
        # da v resnici gre za več setov
        # Napake sem poravil ročno, saj so ti specifični podatki pomembni
        
        st_kart_v_problematicnem_setu = int(podatki_o_kartah["set"].value_counts()[posamezen_set])
        if posamezen_set == "DD3":
            return {"set": posamezen_set, "polno_ime": "Duel Decks: Anthology", "st_kart": st_kart_v_problematicnem_setu, "datum_izida": "2014-12-05"}
        elif posamezen_set == "PFNM":
            return {"set": posamezen_set, "polno_ime": "Friday Night Magic: Promos", "st_kart": st_kart_v_problematicnem_setu, "datum_izida": None}
        elif posamezen_set == "PMTG1":
            return {"set": posamezen_set, "polno_ime": "Promos", "st_kart": st_kart_v_problematicnem_setu, "datum_izida": None}
        elif posamezen_set == "PARL2":
            return {"set": posamezen_set, "polno_ime": "Arena Promos", "st_kart": st_kart_v_problematicnem_setu, "datum_izida": None}
    
    konkreten_set = {"set": posamezen_set}
    konkreten_set.update(vzorec.search(vsebina).groupdict())
    
    konkreten_set['polno_ime'] = konkreten_set['polno_ime'].strip()
    konkreten_set['st_kart'] = int(konkreten_set['st_kart'])
    konkreten_set['datum_izida'] = konkreten_set["datum_izida"] # tukaj bi se morda dalo še kaj dodati
    return konkreten_set


def izlusci_podatke_manacosta_in_barve(niz):
    """
    Iz karte izluščimo podatke cene in barve. Treba je poloviti nekaj izjem.
    """
    seznam_simbolov = re.findall(vzorec_za_manacost, niz)
    cmc = 0
    manacost = ""
    barva = ""
    for simbol in seznam_simbolov:
        manacost += simbol
        if simbol.isnumeric():
            cmc += int(simbol)
        elif simbol in "wubrg":
            cmc += 1
            if simbol not in barva:
                barva += simbol
        else:
            if simbol not in "{(p)}x":
                cmc += 1
            if simbol not in "{(p)}c":
                print("Program je našel nenavaden simbol", simbol)
    
    # To je majhen popravek za karte s hybrid manacostom
    # Potreben je, ker je to bug na strani MTGSrocks (narobno zapisuje hybrid cost)
    cmc -= manacost.count("(") + manacost.count("{")
    
    if barva == "":
        barva += "c"
    if manacost == "":
        manacost += "0"
    return {"cmc": cmc, "manacost": manacost, "barva": barva}


def doloci_super_sub_in_cardtype(niz):
    """
    Določimo supertype in subtype karte. Treba je poloviti nekaj izjem.
    """
    niz = niz.removesuffix(", ").strip()
    supertype, subtype, cardtype = [], [], []
    
    # Najprej polovimo nekaj starih karth (niso navedene pravilno na spletni strani)
    if "Enchant " in niz:
        cardtype.append("Enchantment")
        subtype.append("Aura")
        return supertype, cardtype, subtype
    if "Summon " in niz:
        niz = niz.replace("Summon ", "Creature - ")
        if "Legend" in niz:
            supertype.append("Legendary")
            niz = niz.replace("Legend", "")
    
    # Če smo pri tem izpraznili niz, samo returnamo
    if len(niz) > 0:
        for suprtype in seznam_supertypov:
            if suprtype in niz:
                supertype.append(suprtype)
                niz = niz.replace(f"{suprtype} ","")
        if "-" in niz or "—" in niz:
            niz = niz.replace("—","-")
            str_cardtype, str_subtype = niz.split(" - ")
            cardtype = [typ.strip() for typ in str_cardtype.split(" ") if typ.strip() != ""]
            subtype = [typ.strip() for typ in str_subtype.split(" ") if typ.strip() != ""]
        elif " " in niz:
            cardtype = [typ.strip() for typ in niz.split(" ") if typ.strip() != ""]
        else:
            cardtype.append(niz.strip())
        
    return supertype, cardtype, subtype

def pretvori_findall_seznam_v_singleton(seznam):
    if len(seznam) == 1:
        return seznam[0]
    else:
        return None
    

def izlusci_podatke_o_specificni_karti_iz_njene_datoteke(niz):
    povprecje_eu = re.findall(vzorec_povprecja_eu, niz)
    cardtype = re.findall(vzorec_cardtypea, niz)
    oracle_text = re.findall(vzorec_oracle_texta, niz)
    reserved_list = re.findall(vzorec_reserved_list, niz)
    najdi_vse_low = re.findall(vzorec_all_time_low, niz)
    najdi_vse_high = re.findall(vzorec_all_time_high, niz)
    
    povprecje_eu, cardtype, oracle_text, reserved_list = map(pretvori_findall_seznam_v_singleton, [povprecje_eu, cardtype, oracle_text, reserved_list])
    
    if cardtype:
        print(cardtype)
        
        supertype, cardtype, subtype = doloci_super_sub_in_cardtype(cardtype)
    else:
        supertype, subtype = [], []
        
    # Ponekod je oracle text nekonsistenten, zato moramo ročno poloviti nekaj napak. Spodaj konkretno so odpravljene napake pri Planeswalkerjih.
    
    if oracle_text:
        oracle_text = re.sub(vzorec_za_popravo_oracle_texta_notranje_znacke, r"(\1)", oracle_text)
        oracle_text = re.sub(vzorec_za_popravo_oracle_texta_zunanje_znacke, r"\1", oracle_text)
        oracle_text = re.sub(vzorec_za_popravo_oracle_texta_planeswalker_uptake, r"(\+\1)", oracle_text)
        oracle_text = re.sub(vzorec_za_popravo_oracle_texta_planeswalker_downtake, r"(\-\1)", oracle_text)
        oracle_text = oracle_text.replace('""(t)',"(tap)").replace('(t)',"(tap)") # To je zaradi buga na spletni strani
    
    if len(najdi_vse_low) == 1:
        if len(najdi_vse_low[0]) == 2:
            all_time_low, all_time_low_datum = najdi_vse_low[0][0], najdi_vse_low[0][1]
    else:
        all_time_low, all_time_low_datum = None, None
    if len(najdi_vse_high) == 1:
        if len(najdi_vse_high[0]) == 2:
            all_time_high, all_time_high_datum = najdi_vse_high[0][0], najdi_vse_high[0][1]
    else:
        all_time_high, all_time_high_datum = None, None
    return {"povprecje_eu": povprecje_eu, "supertype": supertype, "cardtype": cardtype, "subtype": subtype, "oracle_text": oracle_text, "reserved_list":reserved_list, "all_time_low": all_time_low, "all_time_low_datum": all_time_low_datum, "all_time_high": all_time_high, "all_time_high_datum": all_time_high_datum}


# Pomožne funkcije za čiščenje podatkov
###########################################################################################


def pretvori_datum_v_datetime(string_datuma):
    """
    Funkcija, ki obe vrsti datuma pretvori v ustretno datetime obliko (datum_izida in datum all_time_high/low)
    """
    
    # Za vsak slučaj
    if not string_datuma:
        return None
    
    # Ločimo primera 'Apr 29, 2022' in '2022-04-29'
    if "," in string_datuma:
        return datetime.strptime(string_datuma, "%b %d, %Y")
    else:
        return datetime.strptime(string_datuma, "%Y-%m-%d")
    

def popravi_cardtype_aftermath(seznam_cardtypa):
    """
    Popravimo seznam cardtypa, ki se pojavi zaradi nenavadnega/nekonsistentnega zapisa Aftermath kart na spletni strani
    """
    if not seznam_cardtypa:
        return None
    
    popravljen_seznam = []
    for tip in seznam_cardtypa:
        if tip not in popravljen_seznam and "//" not in tip:
            popravljen_seznam.append(tip)
    return popravljen_seznam


def popravi_subtype_adventure(seznam_subtypa):
    """
    Popravimo seznam subtypa, ki se pojavi zaradi nenavadnega/nekonsistentnega zapisa Adventure kart na spletni strani
    """
    if not seznam_subtypa:
        return None
    
    popravljen_seznam = []
    for tip in seznam_subtypa:
        if "//" in tip:
                break
        elif tip not in popravljen_seznam:
            popravljen_seznam.append(tip)
    return popravljen_seznam


def zavrti_cikel(cikel,smer_urinega = True):
    if smer_urinega:
        return cikel[1:] + cikel[0]
    else:
        return cikel[-1] + cikel[:-1]

def razdalja_med_crkama_v_ciklu(prva_crka, druga_crka, niz_barve, smer_urinega = True):
    if niz_barve[color_pentagon.index(prva_crka)] == druga_crka:
        return 0
    else:
        return 1 + razdalja_med_crkama_v_ciklu(prva_crka, druga_crka, zavrti_cikel(niz_barve, smer_urinega), smer_urinega)


def prvi_string_je_v_drugem(niz1, niz2):
    for crka in niz1:
        if crka not in niz2:
            return False
    return True

def popravi_vrstni_red_barve(niz_barve):
    """
    Funkcija popravi vrstni red stringa barve
    
    Izkaže se, da je še najlažje ločiti funkcijo glede na to, koliko barv je vsebovanih
    Celoten postopek določanja vrstnega reda je opisan tule: https://magic.wizards.com/en/articles/archive/ask-wizards-june-2004-2004-06-01
    """
    if not prvi_string_je_v_drugem(niz_barve, color_pentagon):
        return niz_barve
    if len(niz_barve) < 2 or len(niz_barve) > 5:
        return niz_barve
    if len(niz_barve) == 5:
        return color_pentagon
    if len(niz_barve) == 2:
        transpozicija_niza = niz_barve[::-1]
        if razdalja_med_crkama_v_ciklu(niz_barve[0], niz_barve[1], color_pentagon) > 2:
            return transpozicija_niza
        else:
            return niz_barve
    if len(niz_barve) == 4:
        manjka_barva = color_pentagon[::]
        for crka in niz_barve:
            if crka not in manjka_barva:
                return niz_barve
            else:
                manjka_barva = manjka_barva.replace(crka, "")
        kopija_pentagona = color_pentagon[::]
        while kopija_pentagona[-1] != manjka_barva:
            kopija_pentagona = zavrti_cikel(kopija_pentagona)
        return kopija_pentagona.replace(manjka_barva, "")
    if len(niz_barve) == 3:
        string_barv_v_pravem_redu = ""
        for barva in color_pentagon:
            if barva in niz_barve:
                string_barv_v_pravem_redu += barva 
        while razdalja_med_crkama_v_ciklu(string_barv_v_pravem_redu[2], string_barv_v_pravem_redu[0], color_pentagon) == 1:
            string_barv_v_pravem_redu = zavrti_cikel(string_barv_v_pravem_redu)
        if razdalja_med_crkama_v_ciklu(string_barv_v_pravem_redu[2], string_barv_v_pravem_redu[0], color_pentagon) == 3:
            return string_barv_v_pravem_redu
        kopija_pentagona = color_pentagon[::]
        while not prvi_string_je_v_drugem(string_barv_v_pravem_redu, kopija_pentagona[::2]):
            kopija_pentagona = zavrti_cikel(kopija_pentagona)
        return kopija_pentagona[::2]
            
        

def popravi_barvo_karte(niz_barve, niz_oracle_texta, niz_cardtypa):
    """
    Ta funkcija vzame string barve, ki ga ustrezno popravi glede na oracle text + vrsntni red barv (UW -> WU)
    """
    if not niz_barve or "Land" in niz_cardtypa:
        return "c"
    
    for barva in color_pentagon:
        if barva not in niz_barve:
            if f"({barva})" in niz_oracle_texta:
                niz_barve += barva
    # Odpravimo možnost colorless.
    if len(niz_barve) >= 2:
        niz_barve = niz_barve.replace("c","")
    return popravi_vrstni_red_barve(niz_barve)

# Vzorci
###########################################################################################


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
    r'.*?<td class="text-end">'
    r' (?P<povprecna_cena>.*?) </td>(<\!---->)+(<td class="text-end">.*?</td>.*?<td class="text-end"> (?P<povprecna_cena_foil>.*?) </td>.*?<td class="text-end">.*?</td>)?',  
    flags=re.DOTALL
    )

vzorec_povprecja_eu = re.compile(
    r'Europe avg </p> (?P<povprecje_eu>.*?) <',
    flags=re.DOTALL
)

vzorec_cardtypea = re.compile(
    r'class="card-oracle-item".*?</i> (?P<cardtype>.*?) <',
    flags=re.DOTALL
)

vzorec_oracle_texta = re.compile(
    r'<.*?class="card-oracle-item card-oracle-text">(?P<oracle_text>.*?)</p>',
    flags=re.DOTALL
)

vzorec_all_time_low = re.compile(
    r'All Time Low </p><h3.*?>(?P<all_time_low>.*?)</h3><h5.*?> (?P<datum_all_time_low>.*?) </h5>',
    flags=re.DOTALL
)

vzorec_all_time_high = re.compile(
    r'All Time High </p><h3.*?>(?P<all_time_high>.*?)</h3><h5.*?> (?P<datum_all_time_high>.*?) </h5>',
    flags=re.DOTALL
)

vzorec_reserved_list = re.compile(
    r'Reserved list\?</p><h3.*?>(?P<reserved_list>.*?)</h3>',
    flags=re.DOTALL
)

vzorec_za_popravo_oracle_texta_notranje_znacke = re.compile(
    r'<i class="ms ms-cost ms-(.*?)"></i>',
    flags=re.DOTALL
)
vzorec_za_popravo_oracle_texta_zunanje_znacke = re.compile(
    r'<i>\((.*)\)</i>',
    flags=re.DOTALL
)
vzorec_za_popravo_oracle_texta_planeswalker_uptake = re.compile(
    r'<i class="ms ms-loyalty-(\d*) ms-loyalty-up"></i>',
    flags=re.DOTALL
)

vzorec_za_popravo_oracle_texta_planeswalker_downtake = re.compile(
    r'<i class="ms ms-loyalty-(\d*) ms-loyalty-down"></i>',
    flags=re.DOTALL
)

vzorec_za_manacost = re.compile(r'" class="ms ms-cost ms-(?P<mana_cost>.*?)["| ]',
                                flags=re.DOTALL)