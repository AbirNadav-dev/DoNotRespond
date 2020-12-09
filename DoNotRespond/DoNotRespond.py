import socket
import random
import string
from time import sleep
from random import randint
from select import select
from scapy.layers.llmnr import *
from scapy.layers.netbios import *
from scapy.layers.dns import DNSQR
from scapy.all import *
from smb.SMBConnection import SMBConnection
from smb.base import NotReadyError
import pyfiglet
from colorama import Fore, Back, Style


LLMNRBroadcast = "224.0.0.252"
LLMNRBroadcastPort = 5355
MULTICAST_TTL = 2

server_prefixes = ["srvdb", "srvdb-", "srvfile", "srvfile-",
                   "corpfile-", "srvweb", "srvweb-", "workstation-", "reception-"]

ascii_banner = pyfiglet.figlet_format("Abir Nadav")
print(Fore.BLUE + ascii_banner)


bait_accounts = ['ADMIN', 'sysadmin', 'Adminstrator', 'CEO', 'LOOL']
colors = ['\033[5m', '\033[101m\033[5m',
          '\033[5m\033[0;32m', '\033[5m\033[0;31m']


class args:
    delay = 10
    staysilent = 360
    domain = "CORP"


def sendSMBConnection(activeResponderIp, drive, directory, domain):
    global bait_accounts
    try:
        credidx = randint(0, len(bait_accounts)-1)
        conn = SMBConnection(bait_accounts[credidx][0], bait_accounts[credidx][1], 'connector',
                             activeResponderIp, domain=domain, use_ntlm_v2=True, is_direct_tcp=True)
        conn.connect(activeResponderIp, 445)
        conn.listPath(drive, directory)
        conn.close()
    except NotReadyError as smbex:
        pass
    except Exception as ex:
        print("Failed sending SMB Request: {}".format(ex))


def genWonderingWorkstation():
    return "{}{}".format(server_prefixes[randint(0, len(server_prefixes)-1)], appendix_gen()).upper()


def appendix_gen(size=4, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def detectLLMNRSpoof(name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    sock.setblocking(0)
    request = LLMNRQuery(id=RandShort(), qd=DNSQR(qname=name))
    sock.sendto(bytes(request), (LLMNRBroadcast, LLMNRBroadcastPort))
    try:
        (ready, ar1, ar2) = select([sock], [], [], 5)
        if len(ready) > 0:
            p = sock.recv(10240)
            response = LLMNRResponse(p)
            return response.an.rdata
    except socket.error as sox:
        print("[ERROR] "+sox)
    return None


responder_ip = None


def doDetection(detectionFunction):
    firstWorkstationName = genWonderingWorkstation()
    secondWorkstationName = genWonderingWorkstation()
    print("Started Testing for Responder.....".format(
        detectionFunction.__name__, firstWorkstationName, secondWorkstationName))
    activeResponderIp = detectionFunction(firstWorkstationName)
    if activeResponderIp:
        delay = randint(1, 3)
        sleep(delay)
        activeResponderIp = detectionFunction(secondWorkstationName)
        print(Fore.GREEN + 'FOUND! ' + activeResponderIp)
    return activeResponderIp


if __name__ == "__main__":
    strStart = ("This Script Was Created By Abir Nadav Have fun Fuggin Hackers\n\
    Version: 1.0    \
______________________________________________________________________________________________________________\n\n")
    print(strStart)
    while True:
        activeResponderIp = doDetection(detectLLMNRSpoof)
        if activeResponderIp:
            print("Spoofing Detected by IP: {}!\n".format(
                activeResponderIp, args.staysilent))
            num = 0
            while True:
                sendSMBConnection(activeResponderIp, '\e[5mYOU HAVE BEEN HACKED!',
                                  '\e[5mlol123', colors[num] + '------------------------> YOU HAVE BEEN HACKED! <----------------')
                num += 1
                if num > 3:
                    num = 0
                sleep(0.5)
                print(Fore.MAGENTA + 'Spoofed Request Sent!')
