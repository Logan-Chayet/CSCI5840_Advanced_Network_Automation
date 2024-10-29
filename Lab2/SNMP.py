import os
import re
import pyshark
from csv import DictWriter

devices = {"R1": "10.100.0.6","R2": "10.100.0.7","R3": "10.100.0.8","R4": "10.100.0.9","S1": "10.200.0.1","S2": "10.200.0.2", "S3": "10.100.0.3","S4": "10.100.0.4"}

def getCPU():
    for i in devices.items():
        # Assigning variables to devices and OIDs
        hostname = i[0]
        ip = i[1]
        CPUpkg = "iso.3.6.1.2.1.25.3.3.1.2.1"
        #Command to get CPUpkg
        output = os.popen(f'snmpget -v 2c -c NMAS {ip} {CPUpkg}').read()
        # Parse integer
        match = re.search(r'INTEGER: (\d+)', output)
        CPU_num = match.group(1)
        print(hostname+" CPU%: "+CPU_num)
# tshark command to get pcap info: sudo tshark -a duration:10 -w traps.pcap -i CR_e1-1
def getTraps():
    file = "traps.pcap"
    cap = pyshark.FileCapture(file)
    traps = []
    for packet in cap:
        if 'SNMP' in packet:
            traps.append(str(packet.snmp))
    for i in traps:
        print(i)
    file1 = open("SNMP_traps.txt", "w")
    file1.writelines(traps)
    file1.close()

def getSyslog():
    file = "traps.pcap"
    cap = pyshark.FileCapture(file)
    traps = []
    i = 1
    for packet in cap:
        if 'Syslog' in packet and packet.Syslog.level == "5":
            traps.append(str(packet.Syslog))
            #match = re.search(r'Syslog message id:\s*(.*)', str(packet.Syslog))
            match = re.search(r'%(.*)', str(packet.Syslog))
            result = match.group(1)
            syslog_dict = {'ID':i, 'Router': packet.Syslog.hostname, 'Message':result}
            field_names = ['ID', 'Router', 'Message']
            with open('Syslog.csv', 'a') as f_object:
                dictwriter_object = DictWriter(f_object, field_names)
                dictwriter_object.writerow(syslog_dict)
                f_object.close()
        i+=1

getCPU()
#getTraps()
#getSyslog()
