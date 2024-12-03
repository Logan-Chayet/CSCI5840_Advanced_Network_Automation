from flask import Flask,render_template,request
import yaml, datetime, csv, os, subprocess, re
from netmiko import ConnectHandler
from napalm import get_network_driver


def createAccess():
    # Extract form data
    hostname = request.form.get('hostname')
    mgmt_ip = request.form.get('mgmt_ip')
    username = request.form.get('username')
    password = request.form.get('password')

    # Extract interface data
    interfaces = []
    interface_names = request.form.getlist('interface_name[]')
    port_types = request.form.getlist('port_type[]')
    vlan_ids = request.form.getlist('vlan_id[]')
    vlan_names = request.form.getlist('vlan_name[]')

    # Combine interface data into a list of dictionaries
    for i in range(len(interface_names)):
        interface_data = {
            'interface_name': interface_names[i],
            'port_type': port_types[i],
            'Access': port_types[i] == 'access'  # Add access port status
        }
        if port_types[i] == 'access':  # Include VLAN data only for access ports
            interface_data['vlan_id'] = vlan_ids[i]
            interface_data['vlan_name'] = vlan_names[i]
        
        interfaces.append(interface_data)

    # Create a data dictionary for YAML
    config_data = {
        'devices': {
            'hostname': hostname,
            'mgmt_ip': mgmt_ip,
            'username': username,
            'password': password,
            'interfaces': interfaces,
        }
    }
    # Convert data to YAML and write to a file
    yaml_output = yaml.dump(config_data, default_flow_style=False)
    with open('/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/ANSIBLE/roles/access/vars/main.yaml', 'w') as yaml_file:
        yaml_file.write(yaml_output)
    return yaml_output

def createCore():
    # Collect OSPF information
    ospf_enabled = request.form.get('ospf') == 'on'
    interface_enabled = request.form.get('interface') == 'on'
    ospf_process_id = request.form.get('ospf_process')
    ospf_router_id = request.form.get('ospf_router_id')
    ospf_area = request.form.get('ospf_area')
    ospf_networks = []
    if ospf_enabled:
        ospf_network_list = request.form.getlist('ospf_network[]')
        for network in ospf_network_list:
            ospf_networks.append({'network': network})
    interface_names = request.form.getlist('interface_name[]')
    ip_addresses = request.form.getlist('ip_address[]')
    ipv6_addresses = request.form.getlist('ipv6_address[]')
    # Collect RIP information
    rip_enabled = request.form.get('rip') == 'on'
    rip_networks = []
    if rip_enabled:
        rip_network_list = request.form.getlist('rip_network[]')
        for network in rip_network_list:
            rip_networks.append({'network': network})
    # Collect Interface information
    interfaces = []
    interface_names = request.form.getlist('interface_name[]')
    ip_addresses = request.form.getlist('ip_address[]')
    ipv6_addresses = request.form.getlist('ipv6_address[]')
    for i in range(len(interface_names)):
        sub_intf = False
        base_name = ""
        sub_interface = ""
        if '.' in interface_names[i]:
            base_name, sub_interface = interface_names[i].split('.')
            sub_intf = True
        interfaces.append({
            'name': interface_names[i],
            'ip_address': ip_addresses[i],
            'ipv6_address': ipv6_addresses[i],
            'sub_intf': sub_intf,
            'vlan': sub_interface
        })
    # Collect Device Info
    hostname = request.form.get('hostname')
    mgmt_ip = request.form.get('mgmt_ip')
    username = request.form.get('username')
    password = request.form.get('password')
                                                                                                                                              # Prepare data for YAML generation
    config_data = {
        'devices': {
            'device_info':{
                'hostname': hostname,
                'mgmt_ip': mgmt_ip,
                'username': username,
                'password': password
            },
            'ospf': {
                'enabled': ospf_enabled,
                'ospf_process': ospf_process_id,
                'ospf_router_id': ospf_router_id,
                'ospf_area': ospf_area,
                'networks': ospf_networks
            },
            'rip': {
                'enabled': rip_enabled,
                'networks': rip_networks,
            },
            'interfaces': interfaces,
            'interface_enabled': interface_enabled
        }
    }

    # Convert to YAML
    yaml_output = yaml.dump(config_data, default_flow_style=False)
    with open('/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/ANSIBLE/roles/core/vars/main.yaml', 'w') as yaml_file:
        yaml_file.write(yaml_output)
    return yaml_output

def createEdge():
    # Collect OSPF information
    ospf_enabled = request.form.get('ospf') == 'on'
    ospf_process_id = request.form.get('ospf_process')
    ospf_router_id = request.form.get('ospf_router_id')
    ospf_area = request.form.get('ospf_area')
    ospf_networks = []
    if ospf_enabled:
        ospf_network_list = request.form.getlist('ospf_network[]')
        #ospf_area_list = request.form.getlist('ospf_network_area[]')
        for network in ospf_network_list:
            ospf_networks.append({'network': network})
    # Collect BGP details
    bgp_enabled = 'bgp' in request.form
    bgp_as_number = request.form.get('bgp_as_number')
    bgp_router_id = request.form.get('bgp_router_id')
    bgp_neighbor_ipv4 = request.form.get('bgp_neighbor_ipv4')
    bgp_neighbor_ipv6 = request.form.get('bgp_neighbor_ipv6')
    bgp_network_ipv4 = request.form.get('bgp_network_ipv4')
    bgp_network_ipv6 = request.form.get('bgp_network_ipv6')
    bgp_neighbor_remote_as = request.form.get('bgp_neighbor_remote_as')
    # Collect Interface details
    interfaces = []
    interface_names = request.form.getlist('interface_name[]')
    ip_addresses = request.form.getlist('ip_address[]')
    ipv6_addresses = request.form.getlist('ipv6_address[]')
    #ospf_processes = request.form.getlist('ipv6_process[]')
    #ospf_areas = request.form.getlist('ipv6_area[]')

    for i in range(len(interface_names)):
        sub_intf = False
        base_name = ""
        sub_interface = ""
        if '.' in interface_names[i]:
            base_name, sub_interface = interface_names[i].split('.')
            sub_intf = True
        interfaces.append({
            'name': interface_names[i],
            'ip_address': ip_addresses[i],
            'ipv6_address': ipv6_addresses[i],
            'sub_intf': sub_intf,
            'vlan': sub_interface
        })
    # Collect Device Info
    hostname = request.form.get('hostname')
    mgmt_ip = request.form.get('mgmt_ip')
    username = request.form.get('username')
    password = request.form.get('password')

    # Prepare data for YAML generation
    config_data = {
        'devices': {
            'device_info':{
                'hostname': hostname,
                'mgmt_ip': mgmt_ip,
                'username': username,
                'password': password
            },
            'ospf': {
                'enabled': ospf_enabled,
                'ospf_process': ospf_process_id,
                'ospf_router_id': ospf_router_id,
                'ospf_area': ospf_area,
                'networks': ospf_networks
            },
            'bgp': {
                'enabled': bgp_enabled,
                'bgp_as_number': bgp_as_number,
                'bgp_router_id': bgp_router_id,
                'neighbor_ipv4': bgp_neighbor_ipv4,
                'neighbor_ipv6': bgp_neighbor_ipv6,
                'remote_as': bgp_neighbor_remote_as,
                #'neighbors': [
                #    {'neighbor_ipv4': bgp_neighbor_ipv4, 'remote_as': bgp_neighbor_remote_as},
                #    {'neighbor_ipv6': bgp_neighbor_ipv6, 'remote_as': bgp_neighbor_remote_as}
                #],
                'network_ipv4': bgp_network_ipv4,
                'network_ipv6': bgp_network_ipv6
            },
            'interfaces': interfaces
        }
    }

    # Convert to YAML
    yaml_output = yaml.dump(config_data, default_flow_style=False)
    with open('/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/ANSIBLE/roles/edge/vars/main.yaml', 'w') as yaml_file:
        yaml_file.write(yaml_output)
    return yaml_output

def sendConfig():
    # Collect Device Info
    hostname = request.form.get('hostname')
    mgmt_ip = request.form.get('mgmt_ip')
    username = request.form.get('username')
    password = request.form.get('password')

    device = {
        'device_type': "arista_eos",
        'host': mgmt_ip,
        'username': username,
        'password': password
    }
    cfg_file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/ANSIBLE/CFGS/"+hostname+".txt"
    with ConnectHandler(**device) as connection:
        connection.enable()
        output = connection.send_config_from_file(cfg_file)
    print(output)
    return output

def sendConfig_ztp():
    # Collect Device Info
    hostname = request.form.get('hostname')
    mgmt_ip = request.form.get('mgmt_ip')
    username = request.form.get('username')
    password = request.form.get('password')

    device = {
        'device_type': "arista_eos",
        'host': mgmt_ip,
        'username': username,
        'password': password
    }
    cfg_file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab8/ZTP_cfgs/"+hostname+".txt"
    with ConnectHandler(**device) as connection:
        connection.enable()
        output = connection.send_config_from_file(cfg_file)
    print(output)
    return output


def ping(host):
    # Use the ping command; '-c 1' sends one packet, works on Unix-based systems.
    response = os.system(f"ping -c 1 {host} > /dev/null 2>&1")
    return response == 0

def get_ztp():
    ip = request.form.get('mgmt_ip')
    if ping(ip):
        return sendConfig_ztp()
    else:
        return "Host was not reached, check connectivity and try again." 

def get_neighborships():
    csv_file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/devices.csv"
    hostname = request.form.get('hostname')
    protocol = request.form.get('protocol')
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
    # Show command that we execute.
    if protocol == "BGP":
        command = "show ip bgp"
    elif protocol == "OSPF":
        command = "show ip ospf neighbor"

    with ConnectHandler(**device) as net_connect:
        output = net_connect.send_command(command)

    return output

def get_route_table():
    csv_file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/devices.csv"
    hostname = request.form.get('hostname')
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

    with ConnectHandler(**device) as net_connect:
        output = net_connect.send_command(command)

    return output

def get_cpu():
    csv_file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/devices.csv"
    hostname = request.form.get('hostname')
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
    for i in range(8):
        command = subprocess.run(["gnmic", "-a", mgmt_ip+":6030", "-u", username, "-p", password, "--insecure", "get", "--path", "/components/component[name=CPU"+str(i)+"]/cpu/utilization/state/instant/", "\get", "--values-only"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = command.stdout.decode('utf-8')
        output = output.strip()
        output = output.strip('[]')
        lines = output.split('\n')
        number = lines[1].strip()
        values += "CPU"+str(i)+": "+number+"\n"
    print(values)

    return values

def get_ip_connectivity():
    csv_file = "/home/student/Documents/CSCI5840_Advanced_Network_Automation/Lab4/devices.csv"
    hostname = request.form.get('hostname')
    src_ip = request.form.get('src_ip')
    dst_ip = request.form.get('dst_ip')
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

    print(output)

    match = re.search(r'(\d+) packets transmitted, (\d+) received', output)

    if match:
        packets_transmitted = int(match.group(1))
        packets_received = int(match.group(2))
        if packets_transmitted == packets_received:
            return "Ping Sucessful!"
        else:
            return "Ping Failed!"
    else:
        return "Invalid Source/Destination Address"
                

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

def getconfig(device_type, ip, user, password):
    driver = get_network_driver(device_type)
    eos = driver(ip, user, password)

    eos.open()

    eos_output = eos.get_config(retrieve='running')

    eos.close()

    return eos_output['running']

def getGoldenConfig():
    return_info = []
    routers = sshInfo()
    
    for i in routers:
        output = getconfig(routers[i]['device_type'], routers[i]['ip'], routers[i]['username'], routers[i]['password'])
        
        now = datetime.datetime.now()
        iso_timestamp = now.isoformat()

        #Name the config
        fileName = i+"_"+iso_timestamp+".txt"

        #Write the configs to a new file
        with open("golden_configs/"+fileName, 'w') as file:
            file.write(output)

        print(fileName)
        return_info.append(fileName)
    return "\n".join(return_info)

