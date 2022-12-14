from netmiko import ConnectHandler, ssh_exception
import json
import re
import sys
import getpass
# Function to find mac address from all access devices
def FIND_MAC_L2(FOUNDED_MAC,HOST,DEV_VARS):
    try:
        # add device parametter to var(device) for connecthandler
        DEV_VARS['host'] = HOST
        Connect_to_l2device = ConnectHandler(**DEV_VARS)
        get_hostname = Connect_to_l2device.send_command(
            f'show version | in uptime')
        #Get hostname with show version command, split with space and get first item in list
        print(f'--- Hostname: {get_hostname.split(" ")[0]} ---')
        #Find Mac address using Regular Expression
        MAC_L2 = Connect_to_l2device.send_command(
            f'show mac address-table address {FOUNDED_MAC}')
        get_interface_name = re.search(r"\bFa.+[0-9]\b|\bGi.+[0-9]\b", MAC_L2)
        if get_interface_name:
            #Connected switches receive MAC addresses from their trunk ports!
            check_trunk = Connect_to_l2device.send_command(
                f'show running-config interface {get_interface_name.group()}')
            get_description = Connect_to_l2device.send_command(
                f'show interface {get_interface_name.group()} description')
            if 'trunk' not in check_trunk:
                print('----------------------------------------------------------------------------')
                print(get_description)
                print('----------------------------------------------------------------------------')
                sys.exit('END')
            else:
                print('MAC address on this device received via trunk port!')
                print('show interface description: ')
                print('----------------------------------------------------------------------------')
                print(get_description)
                print('----------------------------------------------------------------------------')                   
        else:
            print('Mac address not found in this device!')
    except (ssh_exception.AuthenticationException, EOFError):
        print(f'Authentication Error')
    except ssh_exception.NetmikoTimeoutException:
        print(f'Connection Timeout')    
    except:
        raise
#Open JSON file to get list of network devices
with open('hosts.json','rt') as FILE:
    NETWORK_DEVICES = json.load(FILE)
print('Username: ')
USERNAME = (str(input()))
PASSWORD = getpass.getpass(prompt='Password: ', stream=None)
L3_SWITCH = '172.16.1.1'
IOS_VARS = {'username': USERNAME,'password': PASSWORD , 'device_type': 'cisco_ios'}
print('Enter IP to find location:')
TARGET_IP = (str(input()))
try:
    try:
        print('Connecting to the device: ' + L3_SWITCH)
        IOS_VARS['host'] = L3_SWITCH
        Connect_To_Device = ConnectHandler(**IOS_VARS)
        Connect_To_Device.enable()
        GET_ARP_RESULT = Connect_To_Device.send_command(
            'sh ip arp ' + TARGET_IP)
        if FOUNDED_MAC := re.search("[0-9a-fA-F]{4}[.][0-9a-fA-F]{4}[.][0-9a-fA-F]{4}", GET_ARP_RESULT):
            print(f'Mac address of {TARGET_IP} is {FOUNDED_MAC.group()}')
            for HOST in NETWORK_DEVICES:
                print('Connecting to the device: ' + HOST)
                FIND_MAC_L2(FOUNDED_MAC.group(), HOST,IOS_VARS)

    except (ssh_exception.AuthenticationException, EOFError):
        print(f'Authentication Error')
    except ssh_exception.NetmikoTimeoutException:
        print(f'Connection Timeout')
except IndexError:
    pass
FILE.close()
