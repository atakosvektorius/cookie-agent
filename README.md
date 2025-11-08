#  Agentas slapukams rinkti į BDAR atitikties serverį

Tai BDAR (Bendrojo duomenų apsaugos reglamento) slapukų atitikties įrankis, skirtas padėti svetainėms atitikti Europos Sąjungos duomenų apsaugos reikalavimus. Pagrindinis serveris https://github.com/atakosvektorius/cookie-web


</br>


## Technologijos
- **Chrome ir chromedriver** - Google Chrome naršyklę ir jos kontroleris (v142)
- **noVNC ir Linux deskop** - GUI (Xfce4) pasiekiamas per naršyklę
- **Python ir Selenium** - Web automatizacija

### Infrastruktūra
- **Docker & Docker Compose** - Konteinerizacija

</br>


## 📦 Naudojimas

### 1. Klonuokite Repozitoriją

```bash
git clone https://github.com/atakosvektorius/cookie-agent.git
cd cookie-agent
```

### 2. Sukonfigūruokite Docker Compose

```bash
cp docker-compose.yml.sample docker-compose.yml
```
Pastaba API raktas ir serverio adresas yra standartiniai reikia pakeisti į kitą

```bash
nano docker-compose.yml
```



### 4. Paleiskite Docker Konteinerius

```bash
./runUpdateThisStack.sh
```

</br>



## Naudojimas per naršyklę 

Sistema bus pasiekiama adresu:
````
http://<serverio-ip>:7900
````


## 📄 Licencija

Šis projektas sukurtas "Atakos vektorius".

</br>




## 📞 Kontaktai

Dėl klausimų ar pagalbos, susisiekite su Atakos Vektoriaus komanda per mūsų oficialų tinklalapį:

https://atakosvektorius.lt