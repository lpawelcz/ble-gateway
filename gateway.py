import os
import subprocess
import requests
from requests.auth import HTTPBasicAuth
import sys

get_press = 'sudo gatttool -i hcio0 -b **:**:**:**:**:** --char-read --handle=0x002e | awk \'{print $6$5$4$3}\''
get_temp = 'sudo gatttool -i hcio0 -b **:**:**:**:**:** --char-read --handle=0x002a | awk \'{print $6$5$4$3}\''
get_hum = 'sudo gatttool -i hcio0 -b **:**:**:**:**:** --char-read --handle=0x002c | awk \'{print $6$5$4$3}\''

TEMP = 'a'
PRESS = 'e'
HUM = 'c'

def get_measurement(cmd, divider):
    stream = os.popen(cmd)
    output = stream.read()
    result = int(output, 16)
    meas = result / divider
    print(meas)
    return meas


def read_all():
    temp = get_measurement(get_temp, 100)
    hum = get_measurement(get_hum, 100)
    press = get_measurement(get_press, 1000)
    
    return temp, hum, press


def stream_read():
    execute("gatttool -i hcio0 -b **:**:**:**:**:** --listen --char-read --handle=0x002c")

    
def execute(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    # don't check first line
    nextline = process.stdout.readline()

    # Poll process for new output until finished
    while True:
        temp = 0.0
        hum = 0.0
        press = 0.0

        for i in range(4):
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
        print("temp: {}".format(temp))
        print("hum: {}".format(hum))
        print("press: {}".format(press))
        db = "*"
        db_server = "*"
        port = ":8086/"
        write = "write?db="
        loc = "*\,pl"
        typ = "indoor"
        host = "*"
        tag_loc = "location=" + loc + ","
        tag_type = "type=" + typ + ","
        tag_host = "host=" + host + " "
        meas = "*,"
        temperature = "temperature=" + str(temp) + ","
        humidity = "humidity=" + str(hum) + ","
        pressure = "pressure=" + str(press)

        url = db_server + port + write + db 
        data = meas + tag_loc + tag_type + tag_host + temperature + humidity + pressure
        print(url)
        print(data)
        r = requests.post(url, auth=HTTPBasicAuth("*", "*"), data=data.encode("utf-8"))
        print("result: {}".format(r))


    #   sys.stdout.write(nextline)
        sys.stdout.flush()

    output = process.communicate()[0]
    exitCode = process.returncode

    if (exitCode == 0):
       return output
    else:
       raise ProcessException(command, exitCode, output)


def main():
    #read_all()
    stream_read()

if __name__ == "__main__":
    main()
