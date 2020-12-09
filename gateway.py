import os
import subprocess
import requests
from requests.auth import HTTPBasicAuth
import sys


# Address of the node we are connecting to
node_addr = "**:**:**:**:**:**"


# Characteristics handle specifiers
TEMP = 'a'
PRESS = 'e'
HUM = 'c'


# Get hex string with measurement from node
node_connect = 'gatttool -i hcio0 -b ' + node_addr
get_meas1 = ' --char-read --handle=0x002'
get_meas2 = ' | awk \'{print $6$5$4$3}\''
get_press = node_connect + get_meas1 + PRESS + get_meas2
get_temp = node_connect + get_meas1 + TEMP + get_meas2
get_hum = node_connect + get_meas1 + HUM + get_meas2


# Listen for notifications from node
node_listen = ' --listen --char-read --handle=0x002c'
listen_cmd = node_connect + node_listen


# Request parts
db = "*"
db_server = "*"
port = ":8086/"
write = "write?db="
loc = "*\,pl"
typ = "indoor"
host = "*"
meas = "*,"


# Super-Safe hardcoded credentials
user = "*"
passwd = "*"


# Get single measurement as floating point variable
def get_measurement(cmd, divider):
    stream = os.popen(cmd)
    output = stream.read()
    result = int(output, 16)
    meas = result / divider
    return meas


# Get temperature, humidity, pressure
def read_all():
    temp = get_measurement(get_temp, 100)
    hum = get_measurement(get_hum, 100)
    press = get_measurement(get_press, 1000)
    
    return temp, hum, press


# Read consecutive measurement as they approach with notifications
def stream_read():
    execute(listen_cmd)


def build_request(temp, hum, press):
    tag_loc = "location=" + loc + ","
    tag_type = "type=" + typ + ","
    tag_host = "host=" + host + " "
    temperature = "temperature=" + str(temp) + ","
    humidity = "humidity=" + str(hum) + ","
    pressure = "pressure=" + str(press)

    url = db_server + port + write + db
    data = meas + tag_loc + tag_type + tag_host + temperature + humidity + pressure

    return url, data


def send_request(url, data, user, passwd):
    r = requests.post(url, auth=HTTPBasicAuth(user, passwd), data=data.encode("utf-8"))
    print("result: {}".format(r))


# Get 3 measuremnts in BLE ESS format
def process_line(process):
    for i in range(3):
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() is not None:
            break
        line = nextline.split()
        handle = line[3]
        hexstr = line[8]
        hexstr += line[7]
        hexstr += line[6]
        hexstr += line[5]

        intvar = int(hexstr, 16)
        meas_type = handle[-1]

        if(meas_type == TEMP):
            temp = intvar / 100
        elif(meas_type == HUM):
            hum = intvar / 100
        elif(meas_type == PRESS):
            press = intvar / 1000

    print("T:{} H:{} P:{}".format(temp, hum, press))

    return temp, hum, press


# Process listener stdout
def execute(command):
    # Spawn listener
    process = subprocess.Popen(command, shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True)

    # Ignore first line with garbage
    nextline = process.stdout.readline()

    # Poll process for new output
    while True:
        temp, hum, press = process_line(process)
        url, data = build_request(temp, hum, press)
        send_request(url, data, user, passwd)
        sys.stdout.flush()

    output = process.communicate()[0]
    exitCode = process.returncode

    if (exitCode == 0):
       return output
    else:
       raise ProcessException(command, exitCode, output)


def main():
    while(1):
        stream_read()

if __name__ == "__main__":
    main()
