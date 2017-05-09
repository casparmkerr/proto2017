# proto2017
Her ligger koden til skuffen <hackd/>, laget av gruppe 5 (Caspar, Idun, Malin og Ylva).

For å fungere må koden kjøre på Raspberry Pi (vi prøvde kun med modell 3, men det burde funke på alle, kanskje bortsett fra førsterevisjon av modell 1, hvor pin layouten var litt annerledes), da den bruker Pi-spesifikke bibliotek (RPi.GPIO).

Transformator.py kjøres av Pien som styrer transformatoroppgaven på innsiden av skuffen, mens Forholdsoppgave-1.py kjøres av Pien som styrer Hack-o-meteret.

Info om kobling og brukte biblioteker ligger i headeren til hver av filene, men her er en recap:
Curses (ncurses til Python) brukes til grafikk
RPi.GPIO brukes for å styre pins
Sevensegment (et bibliotek skrevet spesifikt for Adafruit i2c-skjerm-greier) brukes til de numeriske displayene https://github.com/adafruit/Adafruit_Python_LED_Backpack 
RGB LED-stripen bruker Bibliopixel oversatt til Python 3 (den klikker hvis man ikke bl.a. retter opp i noen prints som mangler parenteser) for å kommunisere over SPI https://github.com/ManiacalLabs/BiblioPixel - koden importerer alt fra "bootstrap" når den importerer Bibliopixel.

På Transformator-Pien løste vi bibliotekskaoset ved å legge alle relevante filer på skrivebordet. Det var veldig praktisk i starten, og så ble det litt for mye styr å rydde opp. Heldigvis slipper noen å se det før det ctrl+c'er seg ut av programmet og starter Raspbians GUI via terminalen. Skal noen begynne på sin egen versjon av prosjektet vil jeg kanskje anbefale å ha en litt ryddigere filstruktur fra begynnelsen av (selvom det jo fungerer fint, og man slipper å ta hensyn til paths når man importerer).

Begge kodene teller antall gale og riktige forsøk i hver sin txt-fil, så man kan bedrive litt statistikk om man ønsker. Det er særlig nyttig for å vurdere om oppgavene er passe vanskelige - vi tenker at 2-3 ganger så mange gale forsøk som riktige er ideelt, da det både er utfordrende og overkommelig.

På Transformator-Pien må config-filen til Raspbian endres til at den default sender ut et 800x480-signal over HDMI. Gjør man ikke det skjønner ikke skjermen hva som foregår, og man får snestorm v2.0.

På Hack-o-meter-Pien må man ikke endre noen oppløsning, antagelig fordi den skjermen både har litt høyere oppløsning (1024x600) og en innebygget scaler. Den må derimot roteres 90 grader i config-filen.

Begge Piene er satt til å ikke boote til skrivebordet, men rett inn i terminal, for så å kjøre scriptene automatisk.

