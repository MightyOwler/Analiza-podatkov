# Analiza podatkov - MTG trg

Analiziral bom karte iz vsakega pomembnejšega Magic: the Gathering. Podatke bom vzel s strani [MTGStocks.com](https://www.mtgstocks.com/sets), saj so lahko dostopni in bolj popolni kot na evropski spletni strani. Na njej je mogoče razbrati tudi povprečno evropsko ceno kart.

Pri vsaki karti bom zajel:
* njen indeks na MTGStocks.com
* ime
* redkost
* set, v katerem se nahaja
* poveprečno ceno in povprečno ceno foil verzije karte (ameriški trg)
* povprečno ceno (evropski trg)
* najnižjo in najvišjo doseženo ceno ter datuma teh dogodkov (ameriški trg)
* ali je na reserved listu
* mana value, CMC in barvo karte
* supertype, cardtype in subtype
* oracle text

Pri vsakem setu bom zajel:
* kodo seta
* polno ime
* št. kart
* datum izida

Delovne hipoteze:
* Ali obstaja povezava med starostjo in ceno kart?
* Kateri tipi kart so najbolj vredni?
* Kateri seti so najbolj vredni?
* Koliko časa od izida karte v povprečju dosežejo najnižjo ceno?
* Ali se da z naivnim Bayesovim klasifikatorjem ugotoviti barvo karte glede na:
  1. oracle text
  2. supertype, cardtype in subtype
  3. ime
  
