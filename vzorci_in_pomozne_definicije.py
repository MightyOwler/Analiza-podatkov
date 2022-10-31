import re

seznam_supertypov = ["Basic", "Legendary", "Ongoing", "Snow", "World"]
problematicni_seti = ["PFNM", "PMTG1", "DD3", "PARL2"]


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
    cmc -= barva.count("(") + barva.count("{")
    
    if barva == "":
        barva += "c"
    if manacost == "":
        manacost += "0"
    return {"cmc": cmc, "manacost": manacost, "barva": barva}


def doloci_super_sub_in_cardtype(niz):
    niz = niz.removesuffix(", ")
    supertype, subtype, cardtype = [], [], []
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


