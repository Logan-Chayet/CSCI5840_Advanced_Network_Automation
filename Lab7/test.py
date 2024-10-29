import csv
from netmiko import ConnectHandler
import subprocess
import re
def cpu_test():
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
    print(CPU_num)
cpu_test()
