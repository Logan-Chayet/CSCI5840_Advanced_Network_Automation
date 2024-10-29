from ncclient import manager

def NETCONF():
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
            print(response)
            return True
    except:
        print("NETCONF did not connect")
        return False
NETCONF()
