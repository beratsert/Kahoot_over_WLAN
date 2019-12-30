import socket
import os
from _thread import *
import threading
import time
import sys
import struct

#CONFIGS
true_answer=''
HOST=''
USERNAME=''
friend_list= {}
online_user= {}
score_table= {}
time_question=0

def clear():

    os.system('clear')

#GETS USERNAME
def get_username():

    clear()
    global USERNAME
    print("Welcome to Kahoot over WLAN!\n\n")
    USERNAME = input("To continue, please type your username..\n")
    return USERNAME

#LEARNS USER'S IP AND CALLS LISTEN THREAD
def get_ip(USERNAME):

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        global HOST
        s.connect(('10.255.255.255', 1))
        HOST = s.getsockname()[0]
    except:
        HOST = '127.0.0.1'
    finally:
        clear()
        print("Your USERNAME : %s\n" % (USERNAME))
        print("Your IP : %s\n" % (HOST))
        s.close()
        Listener_Thread()


#STARTS THREAD FOR LISTENING PACKETS
def Listener_Thread():
    listener_UDP_thread = threading.Thread(target=listener_UDP)
    listener_UDP_thread.setDaemon(True)
    listener_UDP_thread.start()
    enter_command()

def enter_command():
    input("\nPress Enter to continue...")
    main_menu()

#SENDS ANNOUNCE PACKETS VIA OPENING A UDP SOCKET AND BROADCASTING ANNOUNCEMENT.
def Announce():

    global USERNAME
    global HOST
    PORT=12543
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.settimeout(0.05)
    server.bind(("", 5000))

    packet="["+USERNAME+ ", " + HOST +", announce]"
    while True:

        server.sendto(packet.encode('ascii', 'replace'), ('<broadcast>', PORT))
        time.sleep(1)

def show_friendlist():
    global friend_list
    clear()
    for k in friend_list.items():
        if k != None :
            print(str(k))
    tmp2=input("Type 0 to Main Menu\n")
    if tmp2=='0':
        main_menu()
    else:
        time.sleep(2)
        show_friendlist() 

#POSSIBLES TO NAVIGATE IN MAIN MENU
def Navigator():
    tmp=input("Please type your selection..")
    if tmp == '1':
        clear()
        print("You are sending announce messages..")
        Announce_thread = threading.Thread(target=Announce)
        Announce_thread.setDaemon(True)
        Announce_thread.start()
        enter_command()
    elif tmp == '2':
        show_friendlist()
    elif tmp == '3':
        packet="["+USERNAME+ ", " + HOST +", start]"
        multicast_packet(packet)
        quiz()
    else:
        clear()
        print("See you again!!")
        sys.exit(0)

def quiz():
    global online_user
    clear()
    for k in online_user.items():
        if k != None :
            print(str(k))
    tmp=input("Type 1 to refresh\nType 2 to continue\nType 3 to main_menu")
    if tmp =='1':
        quiz()
    elif tmp =='2':
        question_interface()
    else:
        main_menu()


def afterquestion():
    clear()
    Total = {}
    tmp = input("If you want to finish the quiz type 1 \n"
          "If you want to Ask another question type 2 \n"
          "If you want to scoreboard Type 3\n")
    if tmp == '1':
        print("Thank you for yout entrance here is the points \n")
        for i in score_table.items():
            print(i)
        for i in score_table:
            TotalPoint = 0
            Values = score_table[i].split(" ")
            for j in Values:
                j = j.strip()
                if j != '':
                    TotalPoint = TotalPoint + int(j)
            Total[i] = TotalPoint
        for i in Total.items():
            print(i)

        packet = "[" + USERNAME + ", " + HOST + ", exit, " + str(Total) + " " + "]"
        multicast_packet(packet)
        input("Thank you for hosting the quiz")

    elif tmp == '2':
        question_interface()
    elif tmp == '3':
        for i in score_table.items():
            print(i)
            time.sleep(3)
            afterquestion()



def question_interface():
    
    global true_answer
    clear()
    question=input("Please type your question..\n")
    choice_a=input("Please type the choice A..\n")
    choice_b=input("Please type the choice B..\n")
    choice_c=input("Please type the choice C..\n")
    choice_d=input("Please type the choice D..\n")
    true_answer=input("Please type the answer (A,B,C,D)\n")
    tmp=input("Type 1 to continue or any key to type again or 0 to go back")
    if tmp =='1':
        packet="["+USERNAME+ ", " + HOST +", question, "+ question+", "+choice_a+", "+choice_b+", "+choice_c+", "+choice_d+"]"
        multicast_packet(packet)
        afterquestion()
    elif tmp =='0':
        quiz()
    else:
        question_interface()

#MAIN MENU FUNCTION
def main_menu():
    
    clear()
    print("You are in the main menu!")
    print("You are automatically responding announce messages!\n")
    print("If you want to send announce messages, please type 1")
    print("If you want to see Friend List, please type 2")
    print("If you want to start the quiz, please type 3")
    print("You can exit by typing 0")
    Navigator()

#MAIN FUNCTION
def main():
    USERNAME = get_username()
    get_ip(USERNAME)

#TAKES HOST, PORTS AND PACKET INFO AND BY OPENING PORT SENDS MESSAGES
def send_packet(host, port, packet):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(1)
            s.sendto(packet.encode('ascii', 'replace'),(host,port))
            s.close()
    except:
        pass

def multicast_packet(packet):
    global time_question
    multicast_group = ('224.3.29.71', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.2)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    time_question = round(time.monotonic() * 1000)
    try:

        sent = sock.sendto(packet.encode('ascii','replace'), multicast_group)
        print(packet)
    finally:

        sock.close()


def friend_log(name,ip):

    PORT=12543    
    global friend_list
    if ('%s' %(name)) not in friend_list:
        friend_list['%s' %(name)] = ip
    else:
        packet="["+USERNAME+ ", " + HOST +", error, Change your nickname!]"
        start_new_thread(send_packet, (ip, PORT, packet))

def onlineuser_log(name,ip):

    global online_user
    if ('%s' %(name)) not in online_user:
        online_user['%s' %(name)] = ip

def scoretable_log(name,ip,answer=None):
    global score_table
    global true_answer
    global time_question
    if not bool(answer):
        if ('%s, %s' %(name,ip)) not in score_table:
            score_table['%s, %s' %(name,ip)] = 0
    else :
        if true_answer == answer:
            tmp_time=round(time.monotonic() * 1000)
            point=1000-(time_question-tmp_time)
        else:
            point = '0'

        if ('%s, %s' %(name,ip)) not in score_table:
            score_table['%s, %s' %(name,ip)] = f'{point} '
        elif not bool(score_table['%s, %s' %(name,ip)]) :
            score_table['%s, %s' %(name,ip)] = score_table['%s, %s' %(name,ip)] = f"{point} "
        else:
            score_table['%s, %s' %(name,ip)] = score_table['%s, %s' %(name,ip)] + (f"{point} ")
        return point

#PARSER FOR INCOMING PACKETS AND STARTS NEW THREAD FOR RESPONSE MESSAGES
def parser(data):
    
    if len(data) > 5 :
        data=data.strip()
        data=data[1:-1]
        data=data.decode('ascii','replace')
        target_name, target_ip, target_type, *etc = data.split(',',4)
        if target_type.strip() == 'response' :        
            friend_log(target_name.strip(), target_ip.strip())
        elif target_type.strip() == 'ready' : 
            onlineuser_log(target_name.strip(), target_ip.strip())
        elif target_type.strip() == 'answer' :
            point = scoretable_log(target_name.strip(), target_ip.strip(), str(*etc).strip())
            packettosent = "[" + USERNAME+ ", " + HOST + ", " + "trueanswer" + ", " + f"Answer was {true_answer} You gain {point} point " + "]"
            send_packet(target_ip.strip(),12543,packettosent)

def listener_UDP():
    PORT = 54321
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    client.bind((HOST, PORT))
    while True:
        data, addr = client.recvfrom(2048)
        parser(data)
        print(data)

def listener_multicast():
    multicast_group = '224.3.29.71'
    server_address = ('', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server_address)
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(
        socket.IPPROTO_IP,
        socket.IP_ADD_MEMBERSHIP,
        mreq)
    while True:
        data, address = sock.recvfrom(2048)
        parser(data)
    

main()

