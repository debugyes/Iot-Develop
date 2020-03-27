# 使用灯的接口上传常量
import socket
import time
import json
import Adafruit_DHT
from gpiozero import LED

# must be modified===
DEVICEID = '17081'
APIKEY = '3ad293dfc'
# modify end=========
led = LED(17)
host = "www.bigiot.net"
port = 8181

# connect bigiot
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(0)
while True:
    try:
        s.connect((host, port))
        break
    except:
        print('waiting for connect bigiot.net...')
        time.sleep(2)

# check in bigiot
checkinBytes = bytes('{\"M\":\"checkin\",\"ID\":\"' + DEVICEID + '\",\"K\":\"' + APIKEY + '\"}\n', encoding='utf8')
s.sendall(checkinBytes)

# keep online with bigiot function
data = b''
flag = 1
t = time.time()


def keepOnline(t):
    if time.time() - t > 40:
        s.sendall(b'{\"M\":\"status\"}\n')
        print('check status')
        return time.time()
    else:
        return t


# say something to other device function
def say(s, id, content):
    sayBytes = bytes('{\"M\":\"say\",\"ID\":\"' + id + '\",\"C\":\"' + content + '\"}\n', encoding='utf8')
    s.sendall(sayBytes)


# deal with message coming in
def process(msg, s, checkinBytes):
    msg = json.loads(msg)
    if msg['M'] == 'connected':
        s.sendall(checkinBytes)
    if msg['M'] == 'login':
        say(s, msg['ID'], 'Welcome! Your public ID is ' + msg['ID'])
    if msg['M'] == 'say':
        say(s, msg['ID'], 'You have send to me:{' + msg['C'] + '}')
        """
        if msg['C'] == "play":
            led.on()
            say(s, msg['ID'], 'LED turns on!')
        if msg['C'] == "stop":
            led.off()
            say(s, msg['ID'], 'LED turns off!')
        """


'''
DHT测温说明

Python 库
    DHT11 的读取需要遵循特定的信号协议完成，使用Adafruit DHT 库。
软件安装
    开始之前需要更新软件包：
        sudo apt-get update
        sudo apt-get install build-essential python-dev
    从 GitHub 获取 Adafruit 库：
        sudo git clone https://github.com/adafruit/Adafruit_Python_DHT.git
        cd Adafruit_Python_DHT
    给Python2和Python3安装该库：
        sudo python setup.py install
        sudo python3 setup.py install
示例程序
Adafruit 提供了示例程序，运行下面的命令测试。
    cd ~
    cd Adafruit_Python_DHT
    cd examples
    python AdafruitDHT.py 11 17
    这两个参数分别表示 DHT11 和数据引脚所接的树莓派 GPIO 编号。成功的话会输出：
    Temp=22.0* Humidity=68.0%
'''
def temp():
    # Set sensor type : Options are DHT11,DHT22 or AM2302
    sensor = Adafruit_DHT.DHT11

    # Set GPIO sensor is connected to
    gpio = 27

    # Use read_retry method. This will retry up to 15 times to
    # get a sensor reading (waiting 2 seconds between each retry).

    humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)

    # Reading the DHT11 is very sensitive to timings and occasionally
    # the Pi might fail to get a valid reading. So check if readings are valid.
    if humidity is not None and temperature is not None:
        # print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
        return temperature, humidity
    else:
        print('Failed to get reading. Try again!')
        return 0


# for key in msg:
# print(key,msg[key])
# print('msg',type(msg))

# main while


while True:
    try:
        d = s.recv(1)
        flag = True
    except:
        flag = False
        time.sleep(1)
        t = keepOnline(t)
    if flag:
        if d != b'\n':
            data += d
        else:
            msg = str(data, encoding='utf-8')
            process(msg, s, checkinBytes)
            print(msg)
            data = b''

    temperature, humidity = temp()
    # words=bytes('{"M":"update","ID":"16704","V":{"14986":"1.1"}}\n', encoding='utf8')
    words = bytes('{"M":"update","ID":"17081","V":{"15234":' + str(temperature) + ', \
    "15275":' + str(humidity) + '}}\n', encoding='utf8')
    s.sendall(words)
    print("messages have been sent!")
    time.sleep(6)
