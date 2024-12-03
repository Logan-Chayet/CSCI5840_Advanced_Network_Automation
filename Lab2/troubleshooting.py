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


def fix_interface_state():
    getSyslog()
    seen = set()
    data = extract_interface_states("Syslog.csv")
    for entry in data:
        if entry['State'] == "down":
            if entry['Interface'] in seen:
                continue
            seen.add(entry['Interface'])
            interface_no_shut(entry['Interface'], entry['Hostname'])
    time.sleep(1)
    getSyslog()

    data_after = extract_interface_states("Syslog.csv")
    seen_after = set()
    for entry in data_after:
        if entry['State'] == "up":
            if entry['Interface'] in seen_after:
                continue
            seen_after.add(entry['Interface'])
            print(entry['Interface'])


fix_interface_state()

#csv_file = "Syslog.csv"  # Replace with the path to your CSV file
#interface_states = extract_interface_states(csv_file)

#for entry in interface_states:
#    print(f"Interface: {entry['Interface']}, State: {entry['State']}")

def tshark_run():
    command = [
        "tshark",
        "-a", "duration:20",
        "-w", "traps.pcap",
        "-i", "CR_e1-1",
        "-q"
    ]

    try:
        # Run the tshark command in the background
        process = subprocess.Popen(command)
        print(f"tshark is running in the background with PID: {process.pid}")

        # Run other functions while tshark is running
        for i in range(10):
            print(f"Doing other work... {i}")
            time.sleep(1)  # Simulate work

        # Optionally, wait for tshark to complete
        process.terminate()
        print("tshark process has completed.")

    except FileNotFoundError:
        print("tshark command not found. Ensure tshark is installed and in your PATH.")
    except Exception as e:
        print(f"An error occurred: {e}")
#tshark_run()

