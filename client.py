import socket
import os
from _thread import *
import threading
import time
import sys
import struct

# CONFIGS
HOST = ''
USERNAME = ''
isanswed = False
host_list = {}


def clear():
    os.system('clear')


# GETS USERNAME
def get_username():
    clear()
    global USERNAME
    print("Welcome to Kahoot over WLAN!\n\n")
    USERNAME = input("To continue, please type your username..\n")
    return USERNAME


# LEARNS USER'S IP AND CALLS LISTEN THREAD
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


# STARTS THREAD FOR LISTENING PACKETS
def Listener_Thread():
    listener_UDP_thread = threading.Thread(target=listener_UDP)
    listener_UDP_thread.setDaemon(True)
    listener_UDP_thread.start()
    listener_multicast_thread = threading.Thread(target=listener_multicast)
    listener_multicast_thread.setDaemon(True)
    listener_multicast_thread.start()
    enter_command()
    listener_UDP_thread.join()


def enter_command():
    input("\nPress Enter to continue...")
    main_menu()


def quiz_interface():
    clear()
    print("You are waiting new question..")


# POSSIBLES TO NAVIGATE IN MAIN MENU
def Navigator():
    tmp = input("")
    if tmp == '0':
        clear()
        print("See you again!!")
        sys.exit(0)
    elif tmp == '1':
        show_hostlist()


# MAIN MENU FUNCTION
def main_menu():
    clear()
    print("You are in the main menu\n")
    print("You are automatically responding announce messages!\n")
    print("You can exit by typing 0\n")
    print("You can see the hosts by typing 1\n")
    print("Enter to continue...")
    Navigator()


# MAIN FUNCTION
def main():
    USERNAME = get_username()
    get_ip(USERNAME)


# TAKES HOST, PORTS AND PACKET INFO AND BY OPENING PORT SENDS MESSAGES
def send_packet(host, port, packet):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(1)
            s.sendto(packet.encode('ascii', 'replace'), (host, port))
            s.close()
            print(packet)
    except:
        pass


def sentready(packet, target_ip):
    clear()
    send_packet(target_ip, 54321, packet)


def answerquestion(target_ip, question, A_choice, B_choice, C_choice, D_choice):
    print("\nQuestion: ")
    print(question)
    print("\nA. ")
    print(A_choice)
    print("\nB. ")
    print(B_choice)
    print("\nC. ")
    print(C_choice)
    print("\nD. ")
    print(D_choice + "\n")
    Answer = input("Type your choice!!\n")
    Sendingpacket = "[" + USERNAME + ", " + HOST + ", answer, " + Answer + "]"
    send_packet(target_ip, 54321, Sendingpacket)
    quiz_interface()


def hostlist_log(name, ip):
    global host_list
    if ('%s' % (name)) not in host_list:
        host_list['%s' % (name)] = ip


def show_hostlist():
    global host_list
    clear()
    for k in host_list.items():
        if k != None:
            print(str(k))
    tmp2 = input("Type 0 to Main Menu\n")
    if tmp2 == '0':
        main_menu()
    else:
        time.sleep(2)
        show_hostlist()


def quiz_permission(packet, target_ip, target_name):
    print(target_name + "has sent you an invite to quiz..\n")
    tmp = input("[Y/N]?\n")
    if tmp == 'Y':
        sentready(packet, target_ip.strip())
        clear()
        quiz_interface()

    else:
        main_menu()


# PARSER FOR INCOMING PACKETS AND STARTS NEW THREAD FOR RESPONSE MESSAGES
def parser(data):
    global isanswed
    PORT = 54321

    if len(data) > 5:
        data = data.strip()
        data = data[1:-1]
        data = data.decode('ascii', 'replace')
        target_name, target_ip, target_type, *etc = data.split(',', 4)
        if target_type.strip() == 'announce' and isanswed == False:
            isanswed = True
            packet = "[" + USERNAME + ", " + HOST + ", response]"
            send_packet(target_ip.strip(), PORT, packet)
            hostlist_log(target_name.strip(), target_ip.strip())
        elif target_type.strip() == 'error':
            clear()
            print(str(*etc).strip())
            enter_command()
        elif target_type.strip() == 'start':
            packet = "[" + USERNAME + ", " + HOST + ", ready]"
            quiz_permission(packet, target_ip, target_name)

        elif target_type.strip() == 'question':
            target_name, target_ip, target_type, question, A_choice, B_choice, C_choice, D_choice = data.split(',', 8)
            answerquestion(target_ip.strip(), question.strip(), A_choice.strip(), B_choice.strip(), C_choice.strip(),
                           D_choice.strip())
        elif target_type.strip() == 'exit':
            print(etc)
            input("See u soon")
            sys.exit(0)
        elif target_type.strip() == "trueanswer":
            print(etc)


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
        data, address = sock.recvfrom(1024)
        print(data)
        parser(data)


def listener_UDP():
    PORT = 12543
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", PORT))
    while True:
        data, addr = client.recvfrom(2048)
        # print(data)
        parser(data)


main()

