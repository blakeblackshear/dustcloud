#!/usr/bin/env python3

import socket
import hashlib
import json
import sys
import argparse
import http.server
import socketserver
import threading
from time import sleep
import miio


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    '''
    https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/34325723#34325723
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    '''
    percent = ('{0:.' + str(decimals) + 'f}').format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Clear Line on Complete
    if iteration == total:
        print('\r' + ' ' * (len(prefix) + length + len(suffix) + 11))


def discover_devices():
    timeout = 5
    seen_addrs = []  # type: List[str]
    addr = '<broadcast>'
    # magic, length 32
    helobytes = bytes.fromhex('21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(timeout)
    s.sendto(helobytes, (addr, 54321))
    while True:
        try:
            data, addr = s.recvfrom(1024)
            if addr[0] not in seen_addrs:
                seen_addrs.append(addr[0])
        except socket.timeout:
            break  # ignore timeouts on discover
        except Exception as ex:
            print('Error while reading discover results:', ex)
            break
    return seen_addrs


def select_item(welcome_text, items):
    print(welcome_text)
    for i, item in enumerate(items):
        print('{}. {}'.format(i+1, item))
    try:
        selected = input('Please select option by typing number (1-{}): '.format(len(items)))
        result = items[int(selected)-1]
        return result
    except KeyboardInterrupt:
        print('User requested to exit')
        exit()
    except ValueError:
        print('Error! Please enter only one number')
        exit()
    except IndexError:
        print('Error! Please enter one number between 1-{}'.format(len(items)))
        exit()


def main():
    parser = argparse.ArgumentParser(description='Flasher for Xiaomi Vacuum.\nFor specific options check \'{} --help\''.format(sys.argv[0]))
    parser.add_argument('-a', '--address', dest='address', type=str, help='IP address of vacuum cleaner')
    parser.add_argument('-t', '--token', dest='token', type=str, help='Known token of vacuum')
    parser.add_argument('-f', '--firmware', dest='firmware', type=str, help='Path to firmware file')
    parser.add_argument('-m', '--md5', dest='md5', type=str, help='MD5 hash of firmware file')

    args, external = parser.parse_known_args()

    print('Flasher for Xiaomi Vacuum')

    ip_address = args.address
    known_token = args.token
    firmware = args.firmware
    md5 = args.md5

    if not args.firmware:
        print('You should specify firmware file name to install')
        exit()

    if not ip_address:
        print('Address is not set. Trying to discover.')
        seen_addrs = discover_devices()

        if len(seen_addrs) == 0:
            print('No devices discovered.')
            exit()
        elif len(seen_addrs) == 1:
            ip_address = seen_addrs[0]
        else:
            ip_address = select_item('Choose device for connection:', seen_addrs)

    print('Connecting to device {}...'.format(ip_address))
    vacuum = miio.Vacuum(ip=ip_address, token=known_token)
    if not known_token:
        print('Sending handshake to get token')
        m = vacuum.do_discover()
        vacuum.token = m.checksum

    try:
        s = vacuum.status()
        if s.state == 'Updating':
            print('Device already updating.')
            exit()
        elif s.state != 'Charging':
            print('Put device to charging station for updating firmware.')
            exit()
    except Exception as ex:
        print('error while checking device:', ex)
        exit()

    ota_params = {
        'mode': 'normal',
        'install': '1',
        'app_url': firmware,
        'file_md5': md5,
        'proc': 'dnld install'
    }
    print('Sending ota command with parameters:', json.dumps(ota_params))
    r = vacuum.send('miIO.ota', ota_params)
    if r[0] == 'ok':
        print('Ota started!')
    else:
        print('Got error response for ota command:', r)
        exit()

    ota_progress = 0
    while ota_progress < 100:
        ota_state = vacuum.send('miIO.get_ota_state')[0]
        ota_progress = vacuum.send('miIO.get_ota_progress')[0]
        printProgressBar(ota_progress, 100, prefix = 'Progress:', length = 50)
        sleep(2)
    print('Firmware downloaded successfully.')

    print('Exiting.')
    exit()


if __name__ == '__main__':
    main()
