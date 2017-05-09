'''
INFO OM KOBLING:
Transformatoren:
Venstre side bruker GPIO-pin 04, 27, 17 og 22 og 09 (de øverste brukbare nedover på Piens venstreside)
Høyreside bruker GPIO-pin 18, 23, 24, 25 og 08 (de øverste brukbare nedover på høyresiden)
De fungerer som inputs, og får strøm fra pin 17; 3,3V DC Power.

Numeriske Displays:
Bruker I2C-protokollen.
Pin GPIO02, SDA1, kobles på input D på et av de numeriske displayene.
Pin GPIO03, SCL1, kobles på input C på det samme numeriske displayet.
Displayene kobles etter hverandre, så de har felles D, felles C, felles + og felles -.
De klarer både 5V og 3,3V, men vi valgte det siste for at de ikke skal lyse distraherende sterkt (pluss at 5 kan være litt på kanten for den røde)

Venstre display har adresse 70
Høyre display har adresse 71

LED-strip:
Bruker SPI-protokoll.
Pin GPIO10, SPI_MOSI, kobles til D på stripen
Pin GPIO11, SPI_CLK, kobles til C på stripen
Den trenger 5V, og ca 2A per meter (visstnok). Hvertfall 6 leds funker uten ekstern strømforsyning

Power om-tasten bruker pin GPIO20
Enter-tasten bruker GPIO21
Begge brukes også som spenning inn.

HIGH-signalet ut, for å signalisere at oppgaven er løst, kommer fra pin GPIO26.

'''
import curses #for "GUI"
import random
import time

from bootstrap import * #for LED-stripe

import SevenSegment #for numerisk display
import RPi.GPIO as GPIO #for å bruke GPIO-pins

led = LEDStrip(6) #antall leds på stripen


#initierer numeriske diplays:
right = SevenSegment.SevenSegment(address=0x71) 
left = SevenSegment.SevenSegment(address=0x70)
right.begin()
left.begin()

#initierer GPIO-porter for input:
GPIO.setmode(GPIO.BCM)


GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(26, GPIO.OUT)

#initierer curses for å manipulere terminal til et ønsket GUI:
stdscr = curses.initscr()
curses.start_color()
curses.init_pair(1,curses.COLOR_GREEN,curses.COLOR_BLACK)
curses.init_pair(2,curses.COLOR_RED,curses.COLOR_BLACK)
curses.init_pair(3,curses.COLOR_WHITE,curses.COLOR_BLUE)
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
stdscr.scrollok(True)
curses.curs_set(0)

from curses import wrapper #skaper et "trygt" miljø å kjøre curses i


def buttons(): #tar inn input fra transformatoren
    inn = [] #venstre side
    ut = [] #høyre side
    inn.append(GPIO.input(4))
    inn.append(GPIO.input(17))
    inn.append(GPIO.input(27))
    inn.append(GPIO.input(22))
    inn.append(GPIO.input(9))

    ut.append(GPIO.input(18))
    ut.append(GPIO.input(23))
    ut.append(GPIO.input(24))
    ut.append(GPIO.input(25))
    ut.append(GPIO.input(8))
    inn_val = inn.count(True)
    ut_val = ut.count(True)
    return(inn_val,ut_val)






def numbers(): #lager tall til oppgaven
    a = random.randint(1,5) # Antall spoler på venstre side. Gir et tall fra 1 til og med 5, da Python ikke teller med det siste tallet
    b = random.randint(1,5) # Antall spoler på høyre side. Samme her
    while a == b:
        b = random.randint(1, 5)
    forhold = b/a #Forholdet
    inVolt = a*(random.randint(1,50)*5) #Tallet som skal vises på inn-displayet
    utVolt = float(inVolt*forhold) # Tallet som skal vises på ut-displayet.
    while (utVolt != float(int(utVolt))): #Siden tilfeldige tall som regel betyr stygge tall, sikrer denne for at det hvertfall kun er heltall som slipper gjennom
        inVolt = a * random.randint(1, 50)*5
        utVolt = inVolt * forhold
    return(inVolt,int(utVolt),forhold)



def suksess(stdscr, dims): #kalles hvis brukeren får til oppgaven
    #oppdaterer led-lysene:
    led.fillRGB(0,255,0)
    led.update()
    
    with open('Stats/ant_suksess.txt','r+') as f:
        num_str = f.read()
        num_str = num_str.strip()
        try:
            num = int(num_str)
        except:
            num = 0
        num += 1
        f.seek(0)
        f.write(str(num))

        
        
    curses.noecho() #tastetrykk vises ikke på skjermen
    #diverse linjer tekst:
    yay = 'SUCCESS!'
    slett_filer = 'Vil du slette informasjonsarkivet?'
    enter_forts = 'Trykk enter for å fortsette'
    gratz = 'Filer slettet'
    lukk_safe = 'Du kan nå ta ut viklingene, lukke safedøren og fortsette til neste skuff.'
    
    stdscr.clear() #tøm skjermen
    
    for i in range(0,3): #Blinker skriften, fordi "BLINK" ikke funker på linux
        stdscr.addstr(int(dims[0]/2), int(dims[1]/2-3),yay,curses.color_pair(1))
        stdscr.refresh()
        time.sleep(0.8)
        stdscr.clear()
        stdscr.refresh()
        time.sleep(0.8)
        i+=1
    #mer tekst:
    stdscr.addstr(3,5,slett_filer,curses.color_pair(1))
    stdscr.addstr(4,5,enter_forts,curses.color_pair(1))
    pos = stdscr.getyx()
    key = -1
    stdscr.nodelay(1)
    timeout = time.time()+180 #timeout for når oppgaven resettes
    
    while True: #litt stygg måte å blinke understreken på, og samtidig sjekke om noen trykker enter uten for mye forsinkelse
        if GPIO.input(21): #enter-tasten blir trykket
            break
        stdscr.addstr(pos[0],pos[1],'_')
        stdscr.refresh()
        if GPIO.input(21):
            break
        time.sleep(0.8)
        stdscr.addstr(pos[0], pos[1], ' ')
        stdscr.refresh()
        if GPIO.input(21):
            break
        time.sleep(0.8)

        if GPIO.input(21):
            break
        if time.time() > timeout:
            return
    #ny tekst dukker opp:
    stdscr.nodelay(0)
    stdscr.clear()
    stdscr.addstr(int(dims[0] / 2 - 1), int(dims[1] / 2 - 6), gratz, curses.color_pair(1))
    stdscr.refresh()
    time.sleep(1)
    stdscr.addstr(int(dims[0] / 2) + 1, int(dims[1] / 2 - 30), lukk_safe, curses.color_pair(1))
    stdscr.refresh()
    GPIO.output(26, 1)

    time.sleep(10)


def blueScreen(stdscr,dims): #kalles hvis man har koblet feil
    stdscr.clear()
    stdscr.bkgd(curses.color_pair(3)) #setter bakgrunn blå og tekst hvit, ref initieringen

    with open('Stats/ant_feil.txt','r+') as f:
        num_str = f.read()
        num_str = num_str.strip()
        try:
            num = int(num_str)
        except:
            num = 0
        num += 1
        f.seek(0)
        f.write(str(num))

    
    error = 'VOLTAGE ERROR '
    shutDown = 'Feil spenning'
    
    for i in range(0,3): #mer blinking
        led.fillRGB(0,0,255)
        led.update()
        stdscr.addstr(int(dims[0]/2), int(dims[1]/2-6), error, curses.color_pair(3))
        stdscr.refresh()
        time.sleep(1)
        led.fillRGB(255,0,0)
        led.update()
        stdscr.clear()
        stdscr.refresh()
        time.sleep(0.5)
    led.fillRGB(0,0,255)
    led.update()
    line_num = 0
    char_num = 5
    init_time = time.perf_counter()
    duration = 3
    
    while time.perf_counter()-init_time <=duration: #Teller ned fra duration med tekst som dekker hele skjermen

        #stdscr.addstr(line_num,char_num,error,curses.color_pair(3))
        stdscr.addstr(line_num, 5, 'Feil spenning. Maskinen skrur seg av om ', curses.color_pair(3))
        stdscr.addstr(str(duration-int(time.perf_counter()-init_time)),curses.color_pair(3))
        stdscr.refresh()
        time.sleep(0.01)
        line_num += 1
        if line_num == dims[0]:
            line_num = 0
    stdscr.clear()
    stdscr.addstr(int(dims[0]/2),int(dims[1]/2-5),'PRØV IGJEN',curses.color_pair(3))
    stdscr.refresh()
    time.sleep(2)



def updateDisplay(tall): #oppdaterer numeriske displays
    right.clear()
    left.clear()
    left.print_number_str(str(tall[0]))
    right.print_number_str(str(tall[1]))
    left.write_display()
    right.write_display()



def main(stdscr): #inneholder hovedprogrammet
    curses.echo()
    while True:
        '''
        led.fillRGB(255,0,0)
        led.update()'''
        GPIO.output(26, 0)
        tall = numbers()
        dims = stdscr.getmaxyx()
        power_on = 'Powering on...'
        while True:
            led.fillRGB(255,0,0)
            led.update()
            stdscr.bkgd(curses.color_pair(1))
            stdscr.clear()
            stdscr.refresh()
            #stdscr.addstr('Volt inn: '+str(tall[0])+' Volt ut: '+str(tall[1])+'\n'+'Forhold: '+str(tall[2])) #Brukes til debug for å vise tall og forhold på skjermen i tilleg til numeriske displays
            #stdscr.refresh()

            updateDisplay(tall)
            
            #inn = int(stdscr.getstr()) #brukes til debug der man bruker tastatur som input
            #ut = int(stdscr.getstr())

            if GPIO.input(20): #brukeren trykker "power on"
                inn,ut = buttons()
                if inn != 0 and ut != 0: #det er satt i viklinger på begge sider
                    stdscr.move(int(dims[0] / 2), int(dims[1] / 2 - 7))
                    for letter in power_on: #liten animasjon
                        stdscr.addstr(letter)
                        stdscr.refresh()
                        time.sleep(0.1)
                    if ut/inn == tall[2]: #brukeren har satt inn riktig forhold (forholdet, ikke antallet, er det som sjekkes. Da funker f.eks. 2:1 likt som 4:2)
                        suksess(stdscr,dims) 
                        break #når suksess() har kjørt resettes programmet
                    else: #brukeren har ikke fått til oppgaven, og må prøve på nytt med samme tall
                        blueScreen(stdscr,dims) #etter denne animasjonen
                    time.sleep(1)
                else: #om det ikke er satt i viklinger på begge sider kommer feilmelding
                    stdscr.addstr(int(dims[0] / 2), int(dims[1] / 2-25),'Det blir ikke veldig spennende med null viklinger', curses.color_pair(1))
                    stdscr.refresh()
                    time.sleep(3)









wrapper(main) #curses burde kjøres i wrapper() for å ikke gjøre terminalen for ødelagt om det crasher
