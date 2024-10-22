import secrets
import string
import csv
from napalm import get_network_driver
from netmiko import ConnectHandler

def create_user_pass():
    alphabet = string.ascii_letters + string.digits
    username = ''.join(secrets.choice(alphabet) for i in range(10))
    password = ''.join(secrets.choice(alphabet) for i in range(10))
    return [username, password]

def update_router_credentials(csv_filename, router_hostname, new_username, new_password):
    updated_rows = []
    
    # Read the CSV file
    with open(csv_filename, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Save the header row
        updated_rows.append(header)

        # Iterate through each row in the CSV
        for row in reader:
            if row[0] == router_hostname:
                # Update username and password if hostname matches
                row[3] = new_username
                row[4] = new_password
            updated_rows.append(row)

    # Write the updated rows back to the CSV file
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)

def configure_arista_device(hostname, username, password, ip, config_commands):
    try:
        # Define the device details for Netmiko
        device = {
            'device_type': 'arista_eos',  # Device type for Cisco IOS
            'host': ip,                  # IP address of the device
            'username': username,        # Username for authentication
            'password': password,        # Password for authentication
            'secret': password,          # Enable password (using same password for simplicity)
        }

        # Establish the connection
        print(f"Connecting to device {hostname}...")
        connection = ConnectHandler(**device)

        # Enter enable mode (if applicable)
        connection.enable()

        # Send configuration commands
        print(f"Sending configuration commands to {hostname}...")
        output = connection.send_config_set(config_commands)

        # Display the output of the commands
        print(f"Configuration output from {hostname}:\n{output}")

        # Save the configuration
        connection.save_config()

        # Close the connection
        connection.disconnect()
        print(f"Connection to {hostname} closed.")
    
    except Exception as e:
        print(f"Failed to configure the device {hostname}: {e}")

def change_passwords(devices):
    for i in devices:
        user_pass = create_user_pass()
        update_router_credentials("pass_file.csv", i, user_pass[0], user_pass[1])
    
        with open("devices.csv", mode='r') as file:
            reader = csv.reader(file)

            # Iterate through each row in the CSV
            for row in reader:
                if row[0] == i:
                    # Update username and password if hostname matches
                    configure_arista_device(row[0], row[3], row[4], row[2], "username "+user_pass[0]+" privilege 15 secret "+user_pass[1])

devices = ["R1", "R2", "R3", "R4", "S1", "S2", "S3", "S4"]
change_passwords(devices)
#update_router_credentials("devices.csv", "R2", "test", "test_password")
