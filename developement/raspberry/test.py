import os
import json
import time
import requests
import base64
from phpserialize import dumps  # pip install phpserialize
from Crypto.Cipher import AES  # pip install pycrypto
import hmac
import hashlib
from threading import Thread

key = base64.b64decode("fmDdWI3mPwzB/g5SrKmZileMX6dUarf7t5wx+MKb8Fk=")
token = None


def save_operation(cat=-1):
    global token
    t = round(time.time())
    secret = '{"' + str(t) + '":"' + str(token) + '"}'
    encrypted = encrypt(secret)
    x = Thread(target=postRequest,
               args=("http://backup.sendatrack.com/iosen/api/session/operation/" + str(cat),  encrypted))
    x.start()


def open_session():
    # print(encrypted)
    is_ok = False
    attempts = 0
    while attempts < 2 and is_ok is False:
        attempts += 1
        t = round(time.time())
        secret = '{"' + str(t) + '":"72f8a748e12daa6b9816ac9cae5ab52"}'
        encrypted = encrypt(secret)
        is_ok = postRequest("http://backup.sendatrack.com/iosen/api/session/open",
                            # '{"data" : ' +
                            encrypted
                            # + '}'
                            )
    return is_ok


def postRequest(url, data):
    global key
    global token
    r = requests.post(url, data={"data":data},headers={"Accept":"application/json"})
    print(r.text)
    print(r.status_code)
    if r.status_code == 490:
        key = base64.b64decode(r.text)
        return False
    elif r.status_code == 201:
        token = r.text
        return True
    else:
        return False

    # pass


def aesEncrypterCBC(value, iv):
    global key
    crypter = AES.new(key=key, mode=AES.MODE_CBC, IV=iv)
    return crypter.encrypt(value)


def encrypt(data):
    global key
    iv = os.urandom(16)
    data = dumps(data)
    padding = 16 - len(data) % 16
    data += bytes(chr(padding) * padding, 'utf-8')
    value = base64.b64encode(aesEncrypterCBC(data, iv))
    iv = base64.b64encode(iv)
    mac = hmac.new(key, iv + value, hashlib.sha256).hexdigest()
    dic = {'iv': iv.decode(), 'value': value.decode(), 'mac': mac}
    return base64.b64encode(bytes(json.dumps(dic), 'utf-8')).decode()


open_session()
save_operation(2)
save_operation(1)