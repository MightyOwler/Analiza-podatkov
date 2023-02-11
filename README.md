# Analiza podatkov - MTG trg

Analiziral bom karte iz vsakega pomembnejšega seta _Magic: the Gathering_. Podatke bom vzel s strani [MTGStocks.com](https://www.mtgstocks.com/sets), saj so lahko dostopni in bolj popolni kot na evropski spletni strani. Na njej je mogoče razbrati tudi povprečno evropsko ceno kart.

## Pri vsaki karti bom zajel:

- njen indeks na MTGStocks.com
- ime
- redkost
- set, v katerem se nahaja
- poveprečno ceno in povprečno ceno foil verzije karte (ameriški trg)
- povprečno ceno (evropski trg)
- najnižjo in najvišjo doseženo ceno ter datuma teh dogodkov (ameriški trg)
- ali je na reserved listu
- mana value, CMC in barvo karte
- supertype, card type in subtype
- oracle text

## Pri vsakem setu bom zajel:

- kodo seta
- polno ime
- št. kart
- datum izida

## Delovne hipoteze in vprašanja:

1. Ali obstaja povezava med redkostjo in ceno kart?
2. Ali obstaja povezava med starostjo in ceno kart?
3. Kateri tipi kart so najbolj vredni?
4. Kateri seti so najbolj vredni?
5. Koliko časa od izida karte v povprečju dosežejo najnižjo ceno?
6. Kakšne so razlike med ameriškim in evropskim trgom?
7. Ali se da z naivnim Bayesovim klasifikatorjem ugotoviti barvo karte glede na oracle text?
