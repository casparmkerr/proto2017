'''
Dette programmet hører til "HACK-O-METERET" på safens utside, hvor den skal forberede
brukerne på forholdsoppgaven som kommer på innsiden av døren (i form av en transformator).

Elektromagnetene i dørlåsen aktiveres med pin GPIO04
Rød LED får strøm fra GPIO17
Grønn LED får strøm fra GPIO18

Numpaden tar inn signal på pins GPIO05, 06, 13, 19, 26, 12, 16, 20 og 21 (de nederste brukbare)

Jeg anbefaler å google Python curses for detaljer om de forskjellige kommandoene for å vise tekst/manipulere skjermbildet

'''

#!/usr/bin/python3
import curses
import random
import time

import RPi.GPIO as GPIO

#setup GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
#GPIO setup for solenoid locks
GPIO.setup(4, GPIO.OUT)

#GPIO setup for red/green LED
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

#GPIO setup for numpad, in rising order 1-9
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#initiates curses with correct settings and suitable color palette:
stdscr = curses.initscr()
curses.start_color()
curses.init_pair(1,curses.COLOR_GREEN,curses.COLOR_BLACK)
curses.init_pair(2,curses.COLOR_RED,curses.COLOR_BLACK)
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
curses.curs_set(0)
from curses import wrapper

GPIO.output(4,GPIO.LOW) #Electromagnet is off - door is locked

check = 0 #for checking whether too much time has passed, so that the system can be reset for the next user

def input_number(): #reads data from numpad
    end_time = int(time.time())+300 #Sets a time limit for the user, before resetting progress
    while True:
        if int(time.time()) == end_time: #checks if user has reached time limit
                global check
                check = 1 #tells system time limit is reached
                return 10 #returning something to make sure the program doesn't crash
        if GPIO.input(5):
            return 1
        elif GPIO.input(6):
            return 2
        elif GPIO.input(13):
            return 3
        elif GPIO.input(19):
            return 4
        elif GPIO.input(26):
            return 5
        elif GPIO.input(12):
            return 6
        elif GPIO.input(16):
            return 7
        elif GPIO.input(20):
            return 8
        elif GPIO.input(21):
            return 9
        time.sleep(0.05) #always add some delay in infinite loops

def number_pair_gen(): #Generates a set of 4 corresponding numbers
    while True:
        a= random.randint(1,12)
        forhold = random.randint(2,9)
        b = a*forhold
        c = random.randint(1,8)
        while c == a:
            c = random.randint(1,8)
        d = c*forhold
        if d < 10:
            return (a,b,c,d)
        elif c <10 and random.randint(1,6)==1: #c<10 happens with a far frequency than d<10, so to balance it out a bit, I added the second, random term
            return (b,a,d,c)


def text_gen(stdscr,num_list): #Displays a task on screen
    tries = 0
    curses.echo()
    stdscr.clear()
    stdscr.addstr(1,5,'  Forholdet mellom '+str(num_list[0])+' og '+str(num_list[1]),curses.color_pair(1))
    stdscr.addstr(2,5,'= Forholdet mellom '+str(num_list[2])+ ' og ',curses.color_pair(1))
    coord = stdscr.getyx()
    while True:
        #end_time = int(time.time())+30
        
        stdscr.addstr(coord[0],coord[1],'_', curses.color_pair(1) | curses.A_BLINK)

        stdscr.refresh()
        val = 0
        while True:
            stdscr.clrtoeol()


            #number = int(stdscr.getch(coord[0],coord[1])-48) #used when debugging with proper keyboard
            number = int(input_number())
            global check
            if check == 1: #breaks out of this function if time limit is reached
                return
            stdscr.addstr(coord[0],coord[1],str(number),curses.color_pair(1))
            stdscr.refresh()
            time.sleep(0.5)

            if number <0 or number >=10:
                a = 1/0
            stdscr.move(3, 0)
            stdscr.clrtoeol()
            break


        stdscr.addstr(coord[0],coord[1],str(number), curses.color_pair(1))
        stdscr.refresh()
        if number == num_list[3]:
            with open('/home/pi/Desktop/ant_suksess_ute.txt','r+') as f:
                num_str = f.read()
                num_str.strip()
                try:
                    num = int(num_str)
                except:
                    num = 0
                num +=1
                f.seek(0)
                f.write(str(num))
            stdscr.clrtoeol()
            stdscr.move(4,0)
            stdscr.clrtoeol()
            stdscr.move(5,0)
            stdscr.clrtoeol()
            stdscr.refresh()
            break
        else:
            with open('/home/pi/Desktop/ant_feil_ute.txt','r+') as f:
                num_str = f.read()
                num_str.strip()
                try:
                    num = int(num_str)
                except:
                    num = 0
                num +=1
                f.seek(0)
                f.write(str(num))
            stdscr.addstr(3,5,'ERROR, prøv igjen.',curses.color_pair(1))
            time.sleep(0.1)
            if tries != 0:
                stdscr.addstr(4,5,'HINT: Se for deg tallene i brøker :)',curses.color_pair(1))
            tries +=1
            
            #stdscr.addstr(coord[0],coord[1],'_', curses.color_pair(1) | curses.A_BLINK)



def main(stdscr): #Main function mainly calls other functions in order
    while True:
        GPIO.output(4,GPIO.LOW) #lock locked
        GPIO.output(17,GPIO.HIGH) #red led on
        GPIO.output(18,GPIO.LOW) #green led off
        #curses.curs_set(0)
        #pwm.ChangeDutyCycle(0)
        # Clear screen
        i = 0
        tuple_1 = stdscr.getmaxyx()
        totY = tuple_1[0]
        totX = tuple_1[1]

        global check 
        check = 0 #resets check to 0, meaning time limit is not reached

        
        stdscr.addstr(2,3,"Ved hjelp av avansert teknologi lar dette hack-o-meteret\n   deg åpne hvilken som helst elektronisk kodelås,\n   "
                          "for eksempel den som er festet på safen her.\n   Tast tallene inn på safen",curses.color_pair(2))

        stdscr.refresh()
        ant_oppgaver = 3

        for i in range(0,ant_oppgaver):
            begin_x = 0; begin_y = int((totY/4)*(i+0.9))
            height = int((totY/4)); width = totX
            win = curses.newwin(height, width, begin_y, begin_x) #creates a new window for each task
            text_gen(win,number_pair_gen()) #displays the task
            if check == 1: #if time limit is reached; clear screen and start main function from beginning
                stdscr.clear()
                break

        curses.noecho() #characters are not shown on screen when typed
        '''
        while enter != 10:
            enter = stdscr.getch()
        '''
        if check == 0: #if time limit is not reached, the taskes are solved and the door opens
            stdscr.clear()
            time.sleep(0.5)
            GPIO.output(4,GPIO.HIGH) #lock open
            GPIO.output(17,GPIO.LOW) #red led off
            GPIO.output(18,GPIO.HIGH) #green led on
            
            a = 0
            count = 0
            while a != 10 and count < 20: #Makes the screen blink SYSTEM HACKED for some time
                stdscr.nodelay(1)
                stdscr.addstr(int(tuple_1[0]/2),int(tuple_1[1]/2-7),'SYSTEM HACKED',curses.color_pair(2))
                stdscr.refresh()
                time.sleep(1)
                stdscr.clear()
                stdscr.refresh()
                time.sleep(1)
                count +=1
                a = stdscr.getch()

        
        
        




wrapper(main) #Contains the main program, so that a crash doesn't mess up the terminal

#Notes for using the terminal:
# go to folder name
# $ cd folder_name
# go to home
# $ cd
# go to folder above
# $ cd ..
# go to the proto folder
# $ cd /Users/Caspar/Google\ Drive/NTNU/Proto
# run the program filename.py as a python program
# $ python3.4 filename.py
# se innhold
# $ ls
# terminer program
# ctrl c
