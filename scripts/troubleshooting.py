import os
import re
import pyshark
from csv import DictWriter
import subprocess
import time
import csv
from netmiko import ConnectHandler

def getSyslog():
    file = "traps.pcap"
    cap = pyshark.FileCapture(file)
    traps = []
    i = 1
    field_names = ['ID', 'Router', 'Message', 'Level']
    with open('Syslog.csv', 'w') as f_object:
        for packet in cap:
            dictwriter_object = DictWriter(f_object, field_names)
            if 'Syslog' in packet and packet.Syslog.level <= "5":
                traps.append(str(packet.Syslog))
                #match = re.search(r'Syslog message id:\s*(.*)', str(packet.Syslog))
                match = re.search(r'%(.*)', str(packet.Syslog))
                if not match:
                    continue
                result = match.group(1)
                syslog_dict = {'ID':i, 'Router': packet.Syslog.hostname, 'Message':result, 'Level': packet.Syslog.level}
                dictwriter_object.writerow(syslog_dict)
            i+=1

#getSyslog()

def extract_interface_states(csv_file):
    extracted_data = []  # List to store extracted interface and state
    interface_pattern = re.compile(r'Interface Ethernet(\S+),', re.IGNORECASE)
    state_pattern = re.compile(r'state\s+to\s+(up|down)', re.IGNORECASE)
    
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 3:  # Skip rows without enough data
                continue
            
            # Extract the message field from the row
            message = row[2]
            
            # Search for the interface and state
            interface_match = interface_pattern.search(message)
            state_match = state_pattern.search(message)
            
            if interface_match:
                interface = interface_match.group(1)
                state = state_match.group(1) if state_match else "unknown"
                extracted_data.append({"Interface": interface, "State": state, "Hostname": row[1]})
    
    return extracted_data


def sshInfo():
    csv_file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/devices.csv"
    data = {}

    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            router_name = row["hostname"]
            router_data = {
                "device_type": row["device_type"],
                "ip": row["ip"],
                "username": row["username"],
                "password": row["password"]
            }
            data[router_name] = router_data

    return data

def config_interface(ip, user, password, interface):

    arista_device = {
        'device_type': "arista_eos",
        'host': ip,  # Replace with the device IP address
        'username': user,    # Replace with your username
        'password': password, # Replace with your password
    }

    try:
        # Establish the connection
        connection = ConnectHandler(**arista_device)
        print(f"Connected to {arista_device['host']}")

        # Enter enable mode (if required)
        if connection.check_enable_mode() is False:
            connection.enable()

        # Send the command to configure the interface
        commands = [
            'interface ethernet'+interface,  # Enter interface configuration mode
            'no shutdown'           # Bring up the interface
        ]
        output = connection.send_config_set(commands)

        # Print the command output
        print("Configuration output:")
        print(output)

        # Close the connection
        connection.disconnect()
        print("Connection closed.")

    except Exception as e:
        print(f"An error occurred: {e}")

def interface_no_shut(interface, hostname):
    routers = sshInfo()
    extract_interface_states("Syslog.csv")
    for i in routers:
        if hostname == i:
            config_interface(routers[i]['ip'], routers[i]['username'], routers[i]['password'], interface)

def find_dst_ip(hostname, interface):
    csv_file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/devices.csv"

    routers = sshInfo()
    for i in routers:
        if hostname == i:
            ip = routers[i]['ip']
            username = routers[i]['username']
            password = routers[i]['password']

    device = {
        'device_type': "arista_eos",
        'host': ip,
        'username': username,
        'password': password
    }

    command = "show ip int br"

    with ConnectHandler(**device) as net_connect:
        net_connect.enable()
        output = net_connect.send_command(command)
        print(output)

    match = re.search(r"Ethernet"+interface+"\s+(\S+)", output)

    if match:
        ip_address_with_subnet = match.group(1)
        ip_address = ip_address_with_subnet.split('/')[0]  # Split and get only the IP address
        print(f"The IP address for Ethernet1.10 is: {ip_address}")
        return ip_address
    else:
        print("Ethernet1.10 not found")


def get_ip_connectivity(hostname, interface):
    csv_file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/devices.csv"
    dst_ip = find_dst_ip(hostname, interface)
    devices = ["R1", "R2", "R3", "R4"]
    routers = sshInfo()
    ping_success = {}
    for i in devices:
        if hostname != i:
            ip = routers[i]['ip']
            username = routers[i]['username']
            password = routers[i]['password']

            device = {
                'device_type': "arista_eos",
                'host': ip,
                'username': username,
                'password': password
            }

            command = "ping "+str(dst_ip)

            with ConnectHandler(**device) as net_connect:
                net_connect.enable()
                output = net_connect.send_command(command)

            match = re.search(r'(\d+) packets transmitted, (\d+) received', output)
            
            if match:
                packets_transmitted = int(match.group(1))
                packets_received = int(match.group(2))
                if packets_transmitted == packets_received:
                    ping_success[i] = "True"
                else:
                    ping_success[i] = "False"
            else:
                ping_success[i] = "False"
    return ping_success


def fix_interface_state():
    getSyslog()
    seen = set()
    data = extract_interface_states("Syslog.csv")

    logs = []

    logs.append("Checking for down interfaces\n")
    for entry in data:
        if entry['State'] == "down":
            if entry['Interface'] in seen:
                continue
            seen.add(entry['Interface'])
            logs.append("Found Interface: "+entry['Interface']+" to be down\n")
            logs.append("Now doing a no shutdown on Interface: "+entry['Interface']+"\n")
            interface_no_shut(entry['Interface'], entry['Hostname'])
    time.sleep(1)
    getSyslog()

    data_after = extract_interface_states("Syslog.csv")
    seen_after = set()
    logs.append("Now checking in Syslogs that interface is up\n")
    for entry in data_after:
        if entry['State'] == "up":
            if entry['Interface'] in seen_after:
                continue
            seen_after.add(entry['Interface'])
            logs.append("Interface: "+entry['Interface']+ " is now up\n")
    
    logs.append("Now checking IP connectivity from other devices\n")

    seen_ip = set()
    for entry in data_after:
        if entry['State'] == "up":
            if entry['Interface'] in seen_ip:
                continue
            seen_ip.add(entry['Interface'])
            pings = get_ip_connectivity(entry['Hostname'], entry['Interface'])

            for i in pings:
                if pings[i] == "True":
                    logs.append(i+" ping PASSED for device: "+entry['Hostname']+" at interface: "+entry['Interface']+"\n")
                else:
                    logs.append(i+ " ping FAILED for device: "+entry['Hostname']+" at interface: "+entry['Interface']+"\n")
    
    #subprocess.run(["git", "add", "."], check=True)
    #subprocess.run(["git", "commit", "-m", "Troubleshooting Commit"], check=True)
    return logs

