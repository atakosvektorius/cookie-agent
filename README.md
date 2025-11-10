#  Agentas interneto slapukams rinkti į BDAR atitikties serverį

Tai BDAR (Bendrojo duomenų apsaugos reglamento) slapukų atitikties įrankis, skirtas padėti svetainėms atitikti Europos Sąjungos duomenų apsaugos reikalavimus. 


</br>


## Technologijos
- **Chrome ir chromedriver** - Google Chrome naršyklę ir jos kontroleris (v142)
- **noVNC ir Linux deskop** - GUI (Xfce4) pasiekiamas per naršyklę
- **Python ir Selenium** - Web automatizacija
- **Docker & Docker Compose** - Konteinerizacija

</br>


## Naudojimas

### 1. Nuklonuokite repozitoriją

```bash
git clone https://github.com/atakosvektorius/agent
cd agent
```

### 2. Sukonfigūruokite Docker Compose

```bash
cp docker-compose.yml.sample docker-compose.yml
```
Pastaba API raktas ir serverio adresas yra localhost rekomenduojama pakeisti į <serverio-ip> docker-compose.yml faile

### 3. Paleiskite Docker konteinerius

```bash
./runUpdateThisStack.sh
```

</br>



## Naudojimas per naršyklę 

Sistema bus pasiekiama adresu:
````
http://<serverio-ip>:7900
````


## Licencija ir kontaktai

Šis projektas sukurtas "Atakos vektorius", https://atakosvektorius.lt