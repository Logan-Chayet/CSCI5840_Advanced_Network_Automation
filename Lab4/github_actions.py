import unittest
import re
import ipaddress
import json
from napalm import get_network_driver

def getconfig(IP, user, password):


    driver = get_network_driver('eos')
    iosv12 = driver(IP, user, password)

    iosv12.open()

    ios_output = iosv12.get_config(retrieve='running')

    iosv12.close()

    return ios_output['running']
def testLoopback():
    config = getconfig('10.100.0.6', 'admin', 'admin')
    loopback_pattern = r"interface Loopback0\s+.*\s+ip address (\d+\.\d+\.\d+\.\d+/\d+)"
    loopback_match = re.search(loopback_pattern, config)
    ip = loopback_match.group(1)
    return ip

def testAreas():
    config = getconfig('10.100.0.7', 'admin', 'admin')
    area_pattern = r'area.\d+'
    area_matches = re.findall(area_pattern, config)
    areas = set(area_matches)
    if len(areas) == 1:
        return True
    else:
        return False

def pingTest():
    driver = get_network_driver('eos')
    iosv12 = driver('10.100.0.6', 'admin', 'admin')

    iosv12.open()

    ios_output = iosv12.ping('1.1.1.2')
    iosv12.close() 
    if isinstance(ios_output, dict):
        return True
    else:
        return False
class routerTests(unittest.TestCase):
    
    def test_loopbackTest(self):
        self.assertEqual(testLoopback(), '10.40.1.1/32')
    def test_areas(self):
        self.assertTrue(testAreas())
    def test_ping(self):
        self.assertTrue(pingTest())
if __name__ == '__main__':
    unittest.main()

