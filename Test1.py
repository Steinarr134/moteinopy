import logging
from moteinopy import MoteinoNetwork
import serial
import threading
import time
# logging.basicConfig(level=logging.DEBUG)


try:
    unicode
except (NameError, AttributeError):
    unicode = str


class MySerial(object):
    # A custom serial class only to encode unicode into ascii before writing
    def __init__(self, **kwargs):
        self.Serial = serial.Serial(**kwargs)
        self.read = self.Serial.read
        self.readline = self.Serial.readline
        self.isOpen = self.Serial.isOpen
        self.open = self.Serial.open
        self.close = self.Serial.close

    def write(self, s):
        if isinstance(s, unicode):
            self.Serial.write(s.encode('ascii'))
        else:
            self.Serial.write(s)


ser = MySerial(port='Com53')

receivingEvent = threading.Event()
serlock = threading.Lock()

def readline(ser):
    ret = b""
    while True:
        c = ser.read(1)
        # print(c)
        if c == b"X":
            return c
        elif c == b"\n":
            return ret
        else:
            ret += c


class RecThread(threading.Thread):
    def __init__(self, serial, event):
        threading.Thread.__init__(self)
        self.Serial = serial
        self.E = event
        self.LastReceived = None

    def run(self):
        counter = 0
        while True:
            counter += 1
            # print("listening...")
            line = readline(self.Serial)
            # print(line)

            # Handling the initiation
            if line == b"X":
                time.sleep(0.5)
                self.Serial.write("moteinopy basesketch v2.2\n")
            elif line == b"2b01010130313233343536373839616263646566":
                self.Serial.write("Ready\n")

            else:
                self.LastReceived = line
                with serlock:
                    time.sleep(0.1)
                    self.Serial.write("01" + "0a" + "0" + str(counter % 2) + "\n")


recthread = RecThread(ser, receivingEvent)

recthread.start()

# .........................................  testing starts here  ......................................

print("Initiating....")
time.sleep(0.5)
mynetwork = MoteinoNetwork('Com52')

node1 = mynetwork.add_node(10, "byte B;"
                               "char C;"
                               "int I;"
                               "long L;"
                               "char CA[8];"
                               "int IA[10]", "node1")

node1.add_translation("B", ("one", 1), ("two", 2))


def node1receive(d):
    print(d)


def node1ack(last_d):
    print("node1 ack received")


def node1noack(last_d):
    print("node1 no ack received")


mynetwork.max_wait = 5000

node1.bind(receive=node1receive, ack=node1ack, no_ack=node1noack)

print("Initiation successfull!\n\n Testing sending data....")

time.sleep(2)

node1.send("one", "a", 1234, 123456, "whatsup?", [1, 2, 3, 4, 5, 6, 7, 8])

time.sleep(0.1)
print("..... another sending test ........")

node1.send(B="two", C="\n", CA="abcd")

time.sleep(0.1)
print("Sending has been succcessfull! \n\n Testing receiving data.....")
time.sleep(1)

with serlock:
    ser.write("0a0161d20440e20100776861747375703f0100020003000400050006000700080000000000\n")

time.sleep(0.1)
print("looks like everything works")

print("Made it to the end!!")
