from flask import Flask
from flask_restful import Api, Resource, reqparse

# !/usr/bin/env python3

# This script demonstrates the usage, capability and features of the library.

import argparse

from bluepy.btle import BTLEDisconnectError
from cursesmenu import *
from cursesmenu.items import *
from miband import miband

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mac', required=False, help='Set mac address of the device')
parser.add_argument('-k', '--authkey', required=False, help='Set Auth Key for the device')
args = parser.parse_args()

# Try to obtain MAC from the file
try:
    with open("mac.txt", "r") as f:
        mac_from_file = f.read().strip()
except FileNotFoundError:
    mac_from_file = None

# Use appropriate MAC
if args.mac:
    MAC_ADDR = args.mac
elif mac_from_file:
    MAC_ADDR = mac_from_file
else:
    print("Error:")
    print("  Please specify MAC address of the MiBand")
    print("  Pass the --mac option with MAC address or put your MAC to 'mac.txt' file")
    print("  Example of the MAC: a1:c2:3d:4e:f5:6a")
    exit(1)

# Validate MAC address
if 1 < len(MAC_ADDR) != 17:
    print("Error:")
    print("  Your MAC length is not 17, please check the format")
    print("  Example of the MAC: a1:c2:3d:4e:f5:6a")
    exit(1)

# Try to obtain Auth Key from file
try:
    with open("auth_key.txt", "r") as f:
        auth_key_from_file = f.read().strip()
except FileNotFoundError:
    auth_key_from_file = None

# Use appropriate Auth Key
if args.authkey:
    AUTH_KEY = args.authkey
elif auth_key_from_file:
    AUTH_KEY = auth_key_from_file
else:
    print("Warning:")
    print(
        "  To use additional features of this script please put your Auth Key to 'auth_key.txt' or pass the --authkey option with your Auth Key")
    print()
    AUTH_KEY = None

# Validate Auth Key
if AUTH_KEY:
    if 1 < len(AUTH_KEY) != 32:
        print("Error:")
        print("  Your AUTH KEY length is not 32, please check the format")
        print("  Example of the Auth Key: 8fa9b42078627a654d22beff985655db")
        exit(1)

# Convert Auth Key from hex to byte format
if AUTH_KEY:
    AUTH_KEY = bytes.fromhex(AUTH_KEY)


class MiBand4_Http_Api(Resource):
    def get(self):
        global band
        result = ''
        success = False
        while not success:
            try:
                if (AUTH_KEY):
                    band = miband(MAC_ADDR, AUTH_KEY, debug=True)
                    success = band.initialize()
                else:
                    band = miband(MAC_ADDR, debug=True)
                    success = True
                break
            except BTLEDisconnectError:
                result = '主人不在家，无法捕获身体数据(?д?；)'
                return result, 200

        if success:
            binfo = band.get_steps()
            result += '截止当前: ' + binfo['steps'] + '步'
            result += '消耗: ' + binfo['fat_burned'] + 'Cal'
            result += '今日移动距离: ' + binfo['meters'] + 'M'
            return result, 200


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(MiBand4_Http_Api, "/getMiBandStat")

    app.run(
        host='0.0.0.0',
        port=88,
        debug=True)
