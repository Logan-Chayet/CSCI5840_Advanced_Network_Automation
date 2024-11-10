import secrets
import subprocess
import string
import unittest
import re
import os
import pyshark
import ipaddress
import json
from napalm import get_network_driver
from netmiko import ConnectHandler
from ncclient import manager
from csv import DictWriter
import csv
import ast
#from count_functions import count_functions_in_file

NETCONF_count = 0
SNMP_count = 0
passwords_count = 0
playbookCreation_count = 0

def count_functions_in_file(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())

    # Count the number of function definitions in the file
    function_count = sum(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))

    return function_count

def getconfig(IP, user, password):

    driver = get_network_driver('eos')
    iosv12 = driver(IP, user, password)

    iosv12.open()

    ios_output = iosv12.get_config(retrieve='running')

    iosv12.close()

    return ios_output['running']

#Lab2/NETCONF.py
NETCONF_count+=1
def netconf_test():
    try:
        # Cisco device details
        host = '10.200.0.1'  # Replace with your device IP address
        port = 830             # Default NETCONF port
        username = 'admin'
        password = 'admin'

        # Define the NETCONF filter for retrieving interface information
        netconf_filter = '''
        <filter>
            <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    <interface>
                        <name>Ethernet1</name>
                    </interface>
            </interfaces>
        </filter>
        '''

        # Connect to the device
        with manager.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            hostkey_verify=False
        ) as m:

            # Send NETCONF request to get interface data
            response = m.get(netconf_filter)

            # Print or process the response
            return True
    except:
        print("NETCONF did not connect")
        return False

#Lab2/SNMP.py

#getCPU()
SNMP_count+=1
def cpu_test():
    try:
        hostname = "R1"
        ip = "10.100.0.6"
        CPUpkg = "iso.3.6.1.2.1.25.3.3.1.2.1"
        #Command to get CPUpkg
        command = subprocess.run(["snmpget", "-v", "2c", "-c", "NMAS", ip, CPUpkg], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = command.stdout.decode('utf-8') 
        #command = os.popen(f'snmpget -v 2c -c NMAS {ip} {CPUpkg}')
        #output = command.read()
        # Parse integer
        match = re.search(r'INTEGER: (\d+)', output)
        CPU_num = match.group(1)
        return True
    except:
        print("SNMP Not working")
        return False

#getTraps()
SNMP_count +=1
def traps_test():
    path = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab2/traps.pcap"

    check_file = os.path.isfile(path)

    if check_file:
        return True
    else:
        return False

#getSyslog()
SNMP_count +=1
def syslog_test():
    file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab2/traps.pcap"
    cap = pyshark.FileCapture(file)
    traps = []
    i = 1
    for packet in cap:
        if 'Syslog' in packet and packet.Syslog.level == "5":
            if packet:
                return True
            else:
                return False

#Lab4/passwords.py
passwords_count +=1
def create_user_pass_test():
    alphabet = string.ascii_letters + string.digits
    username = ''.join(secrets.choice(alphabet) for i in range(10))
    password = ''.join(secrets.choice(alphabet) for i in range(10))
    
    if len(username) == 10 and len(password) == 10:
        return True
    else:
        return False

passwords_count +=1
def update_router_credentials_test():
    path = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/pass_file.csv"

    check_file = os.path.isfile(path)

    if check_file:
        return True
    else:
        return False

passwords_count +=1
def configure_arista_device_test():
    router_hostname = "R3"
    username = ""
    password = ""
    ip = ""
    csv_filename = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/pass_file.csv"
    with open(csv_filename, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Save the header row

        # Iterate through each row in the CSV
        for row in reader:
            if row[0] == router_hostname:
                # Update username and password if hostname matches
                ip = row[2]
                username = row[3]
                password = row[4]
    try:
        getconfig(ip, username, password)
        return True
    except Exception as e:
        print(f"Failed to configure the device {router_hostname}: {e}")
        return False

passwords_count +=1
def change_passwords_test():
    path = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/pass_file.csv"

    check_file = os.path.isfile(path)

    if check_file:
        return True
    else:
        return False

#Lab4/playbookCreation.py
playbookCreation_count +=1
def createAccess_test():
    path = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/ANSIBLE/roles/access/vars/main.yaml"

    check_file = os.path.isfile(path)

    if check_file:
        return True
    else:
        return False

playbookCreation_count +=1
def createAccess_test():
    path = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/ANSIBLE/roles/access/vars/main.yaml"

    check_file = os.path.isfile(path)

    if check_file:
        return True
    else:
        return False

playbookCreation_count +=1
def createCore_test():
    path = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/ANSIBLE/roles/core/vars/main.yaml"

    check_file = os.path.isfile(path)

    if check_file:
        return True
    else:
        return False

playbookCreation_count +=1
def createEdge_test():
    path = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/ANSIBLE/roles/edge/vars/main.yaml"

    check_file = os.path.isfile(path)

    if check_file:
        return True
    else:
        return False

playbookCreation_count +=1
def get_neighborships_test():
    csv_file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/devices.csv"
    hostname = "R4"
    command = "show ip bgp"
    mgmt_ip = ""
    username = ""
    password = ""

    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if hostname == row["hostname"]:
                mgmt_ip = row["ip"]
                username = row["username"]
                password = row["password"]

    device = {
        'device_type': "arista_eos",
        'host': mgmt_ip,
        'username': username,
        'password': password
    }
    try:
        with ConnectHandler(**device) as net_connect:
            output = net_connect.send_command(command)
        return True
    except Exception as e:
        print(f"Failed to get {hostname} neighborships: {e}")
        return False

playbookCreation_count +=1
def get_route_table_test():
    csv_file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/devices.csv"
    hostname = "S3"
    mgmt_ip = ""
    username = ""
    password = ""

    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if hostname == row["hostname"]:
                mgmt_ip = row["ip"]
                username = row["username"]
                password = row["password"]

    device = {
        'device_type': "arista_eos",
        'host': mgmt_ip,
        'username': username,
        'password': password
    }

    command = "show ip route"

    try:
        with ConnectHandler(**device) as net_connect:
            output = net_connect.send_command(command)
        return True
    except Exception as e:
        print(f"Failed to get {hostname} route table: {e}")
        return False

playbookCreation_count +=1
def get_cpu_test():
    csv_file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/devices.csv"
    hostname = "R1"
    mgmt_ip = ""
    username = ""
    password = ""
    values = ""
    number = ""
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if hostname == row["hostname"]:
                mgmt_ip = row["ip"]
                username = row["username"]
                password = row["password"]
    try: 
        for i in range(8):
            command = subprocess.run(["gnmic", "-a", mgmt_ip+":6030", "-u", username, "-p", password, "--insecure", "get", "--path", "/components/component[name=CPU"+str(i)+"]/cpu/utilization/state/instant/", "\get", "--values-only"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = command.stdout.decode('utf-8')
            output = output.strip()
            output = output.strip('[]')
            lines = output.split('\n')
            number = lines[1].strip()
            values += "CPU"+str(i)+": "+number+"\n"
        return True
    except Exception as e:
        print(f"Failed to get {hostname} CPU info: {e}")
        return False

playbookCreation_count +=1
def get_ip_connectivity_test():
    csv_file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/devices.csv"
    hostname = "R1"
    src_ip = "21.0.0.2"
    dst_ip = "1.1.1.2"
    mgmt_ip = ""
    username = ""
    password = ""

    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if hostname == row["hostname"]:
                mgmt_ip = row["ip"]
                username = row["username"]
                password = row["password"]

    device = {
        'device_type': "arista_eos",
        'host': mgmt_ip,
        'username': username,
        'password': password
    }

    command = "ping "+dst_ip+" source "+src_ip

    with ConnectHandler(**device) as net_connect:
        net_connect.enable()
        output = net_connect.send_command(command)
    
    match = re.search(r'(\d+) packets transmitted, (\d+) received', output)

    if match:
        packets_transmitted = int(match.group(1))
        packets_received = int(match.group(2))
        if packets_transmitted == packets_received:
            return True
        else:
            return False

playbookCreation_count +=1
def sshInfo_test():
    path = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/devices.csv"

    check_file = os.path.isfile(path)

    if check_file:
        return True
    else:
        return False

def ping_test(host):
    try:
        # Run the ping command with 4 packets
        output = subprocess.check_output(["ping", "-c", "1", host], universal_newlines=True)
        return "Success"
    except subprocess.CalledProcessError:
        return "Failure"

def network_ping_test():
    ping_dict = {}
    fail=0
    csv_file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/devices.csv"
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if ping_test(row["ip"]) == "Success":
                ping_dict[row["hostname"]] = "Success"
                print(row["hostname"]+":"+row["ip"]+" Success")
            else:
                ping_dict[row["hostname"]] = "Failure"
                print(row["hostname"]+":"+row["ip"]+" Failure")
    for i in ping_dict.values():
        if i == "Failure":
            print("Connectivity fails for: "+row["hostname"]+":"+row["ip"])
            fail+=1
    if fail > 0:
        return False
    else:
        return True


class routerTests(unittest.TestCase):

    def test_network_ping_test(self):
        self.assertTrue(network_ping_test())
    def test_netconf(self):
        self.assertTrue(netconf_test())
    def test_snmp_cpu(self):
        self.assertTrue(cpu_test())
    def test_snmp_traps(self):
        self.assertTrue(traps_test())
    def test_snmp_syslog(self):
        self.assertTrue(syslog_test())
    def test_create_user_pass(self):
        self.assertTrue(create_user_pass_test())
    def test_update_router_credentials(self):
        self.assertTrue(update_router_credentials_test())
    def test_configure_arista_device(self):
        self.assertTrue(configure_arista_device_test())
    def test_change_passwords(self):
        self.assertTrue(change_passwords_test())
    def test_createAccess(self):
        self.assertTrue(createAccess_test())
    def test_createCore(self):
        self.assertTrue(createCore_test())
    def test_createEdge(self):
        self.assertTrue(createEdge_test())
    def test_get_neighborships(self):
        self.assertTrue(get_neighborships_test())
    def test_get_route_table(self):
        self.assertTrue(get_route_table_test())
    def test_get_cpu(self):
        self.assertTrue(get_cpu_test())
    def test_get_ip_connectivity(self):
        self.assertTrue(get_ip_connectivity_test())
    def test_sshInfo(self):
        self.assertTrue(sshInfo_test())

if __name__ == '__main__':
    data = [
            {"name": "SNMP.py", "count": SNMP_count, "total": count_functions_in_file("/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab2/SNMP.py")},
            {"name": "NETCONF.py", "count": NETCONF_count, "total": count_functions_in_file("/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab2/NETCONF.py")},
            {"name": "passwords.py", "count": passwords_count, "total": count_functions_in_file("/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/passwords.py")},
            {"name": "playbookCreation.py", "count": playbookCreation_count, "total": count_functions_in_file("/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/playbookCreation.py")}

        ]
    with open("/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab7/counts.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "count", "total"])
        writer.writeheader()  # Write the header row
        writer.writerows(data)  # Write data rows
    unittest.main()
