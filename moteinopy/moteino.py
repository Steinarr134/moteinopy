import serial
import threading
import time
import logging
from moteinopy.DataTypes import types, Array, Byte, Char
__author__ = 'SteinarrHrafn'


# set logging configuration to DEBUG
# a python module should not do this but we are still in beta mode
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


class Struct(object):
    """
    This is a class for parsing a struct through a serial port
    example:

            mystruct = Struct(  "int a;"
                                "int b;")

            send_this_2_serial = mystruct.encode({'a': 1, 'b': 2])

            incoming = mystruct.decode(str_from_serial)

    """
    _disallowed_partnames = ['block', 'max_wait', 'expect_response', 'diction']

    def __init__(self, structstring):
        self.Parts = list()
        self.NofBytes = 0
        self.StructString = structstring
        self._disect_structstring(structstring)

    def _disect_structstring(self, structstring):
        lines = structstring.rstrip(';').split(';')  # remove the last ';' and split by the other ones
        for line in lines:
            temp = line.rsplit(' ', 1)  # split by whitespaces
            if '[' in temp[1]:  # if we are dealing with an array
                ttemp = temp[1].split('[')
                _type = Array(types[temp[0].strip()], int(ttemp[1][:-1]))
                _name = ttemp[0]
            else:
                _type = types[temp[0].strip()]
                _name = temp[1]
            if _name in self._disallowed_partnames:
                raise ValueError(_name + " is not allowed as a variable name in a struct. ")
            self.Parts.append((_type, _name))
        # also store parts as a dict
        self.Parts_dict = dict()
        for (Type, Name) in self.Parts:
            self.Parts_dict[Name] = Type

    def __str__(self):
        return "Struct(" + self.StructString + ")"

    def encode(self, values_dict):
        """
        This function will encode the struct into a HEX string.
        Not all values of the struct must be contained in values_dict,
        those that are not present will be assumed to be 0

        :param values_dict: dict
        :return: str
        """
        returner = str()
        for (Type, Name) in self.Parts:
            if Name in values_dict:
                # print(Type, Name, values_dict[Name])
                try:
                    returner += Type.hexprints(values_dict[Name])
                except ValueError as e:
                    raise ValueError(str(e) + " when parsing " + Name + "=" +
                                     values_dict[Name])
            else:
                returner += Type.hexprints()  # hexprints() assumes value is 0
        return returner

    def decode(self, s):
        """
        This function will decode the struct recieved as a HEX string and return
        a dict with the corresponding values.
        The input string must be sufficiently long to contain the entire struct

        :param s: str
        :return: dict
        """
        returner = dict()
        for (Type, Name) in self.Parts:
            returner[Name] = Type.hex2dec(s[:2*Type.NofBytes])
            s = s[2*Type.NofBytes:]
        return returner


class Node(object):  # maybe rename this to Node?..... Finally done! :D

    def __init__(self, network, _id, structstring, name=None):
        self.ID = _id
        self.Struct = Struct(structstring)
        self.LastSent = dict()
        self.Network = network
        self.Name = 'Node-' + str(network.NodeCounter) if name is None else name
        network.NodeCounter += 1
        self.Translations = dict()
        self.ReceiveFunction = lambda d: network.receive(self, d)
        self.AckFunction = lambda d: network.ack(self, d)
        self.NoAckFunction = lambda d: network.no_ack(self, d)

    def __str__(self):
        return "Node(" + self.Name + ") with id(" + str(self.ID) \
               + ") and " + str(self.Struct)

    def bind(self, receive=None, ack=None, no_ack=None):
        """
        Use this method to bind your own functions to be run when
        * receiving data
        * no ack was received
        * ack was received
        :param receive: function
        :param ack: function
        :param no_ack: function
        :return: None
        """
        if receive is not None:
            self.ReceiveFunction = receive
        if ack is not None:
            self.AckFunction = ack
        if no_ack is not None:
            self.NoAckFunction = no_ack

    def _translate(self, part, key):
        """
        Looks for a translation, returns the key if no translation is found
        :param part: string
        :param key: object
        :return: object
        """
        if part in self.Translations:
            # print "key is in Translations"
            if key in self.Translations[part]:
                # print "value is in Translations[key], returning: " + str(self.Translations[key][value])
                return self.Translations[part][key]
        # print "no translation, just returning value: " + str(value)
        return key

    def add_translation(self, part, *args):
        """
        Use this method to add a translation

        First arguement should be a string matching a part of the nodes struct,
        following arguements should be tuples with a translation.

        Translations go both ways, that is, data is translated when sent and received.

        example:

        node = mynetwork.add_node(_id=10,
                                  structsring="int a; byte[8] b;",
                                  name="node1")

        node.add_translation("a", ("hello", 15), ("goodbye", 16))

        def recfunc(d):
            print d['a']

        node.bind(receive=recfunc)

        node.send("hello") # this will now send a=15

        # and if we would receive a=16 from the node it would not print 16
        # it would print 'goodbye'

        :param part: str
        :param args: tuple
        :return:
        """

        if part not in self.Struct.Parts_dict:
            logging.warning("Translation %s regarding part %s was added to %s. "
                            "However, the Node's struct doesn't contain such a part, "
                            "I doubt you wanted to do this (P.S part names are case sensitive)")
        if part not in self.Translations:
            self.Translations[part] = dict()
        for (key, value) in args:
            self.Translations[part][key] = value
            self.Translations[part][value] = key

    def send(self, *args, **kwargs):
        """
        This is the method to use when sending something.

        data can be passed in multiple ways:

        lets say: node = mynetwork.add_node(_id=10,
                                            structsring="int a; byte[8] b;",
                                            name="node1")

        option1) Passing arguements in the correct order:
            node.send(100, [1, 2, 3, 4, 5, 6, 7, 8])

        option2) Using the parts as keyword arguements:
            node.send(b=[1, 2, 3, 4, 5, 6, 7, 8]) # a will be assumed to be 0

        option3) Creating your own diction and passing that:
            what2send = {'a': 100, 'b' = [1, 2, 3, 4, 5, 6, 7, 8]}
            node.send(diction=what2send)

        :return: None
        """
        if 'expect_response' in kwargs:
            self.Network.ResponseExpected = kwargs['expect_response']
        else:
            self.Network.ResponseExpected = False

        if 'max_wait' in kwargs:
            max_wait = kwargs['max_wait']
        else:
            max_wait = None

        if 'diction' in kwargs:
            diction = kwargs['diction']
        else:
            diction = dict()

        for i, arg in enumerate(args):
            part = self.Struct.Parts[i][1]
            diction[part] = self._translate(part, arg)

        for (key, value) in kwargs.items():
            if key in self.Struct.Parts_dict:
                diction[key] = self._translate(key, value)

        logging.info("sending: " + str(diction))

        self.LastSent = diction
        self.Network.send2base(send2id=self.ID, payload=self.Struct.encode(diction), max_wait=max_wait)

    def send2parent(self, payload):
        """
        :param payload: string
        :return: None
        """
        d = self.Struct.decode(payload)
        logging.info(str(d) + " received from " + str(self))
        d['SenderID'] = self.ID
        d['SenderName'] = self.Name
        d['Sender'] = self

        if not self.Network.ReceiveWithSendAndReceive:
            self.Network.stop_waiting_for_radio()
            self.ReceiveFunction(d)
        else:
            self.Network.LastReceived = d
            self.Network.ReceiveWithSendAndReceive = False
            self.Network.stop_waiting_for_radio()

    def send_and_receive(self, *args, **kwargs):
        self.Network.ReceiveWithSendAndReceive = True
        temp = id(self.Network.LastReceived)
        self.send(*args, **kwargs)
        if id(self.Network.LastReceived) != temp:
            return self.Network.LastReceived
        else:
            return None


class BaseMoteino(Node):
    def __init__(self, network, _id):
        Node.__init__(self, network, _id, "byte Sender;bool AckReceived;", 'BaseMoteino')

    def send2parent(self, payload):
        d = self.Struct.decode(payload)
        if d['Sender'] not in self.Network.nodes:
            raise ValueError("Sender not in known nodes")
        sender = self.Network.nodes[d['Sender']]
        if d['AckReceived']:
            logging.info("Ack received when " + str(sender.LastSent) + " was sent")
            if not self.Network.ResponseExpected:
                self.Network.stop_waiting_for_radio()
            sender.AckFunction(dict(sender.LastSent))
        else:
            logging.warning("No ack received when " + str(sender.LastSent) + " was sent")
            self.Network.stop_waiting_for_radio()
            sender.NoAckFunction(dict(sender.LastSent))


class Send2ParentThread(threading.Thread):
    """
    This is the thread that interprets the struct recieved by the moteino network
    and runs the recieve, no_ack or ack function. The user is allowed to hijack this
    thread from the recieve, no_ack or ack functions.
    """
    def __init__(self, network, incoming):
        threading.Thread.__init__(self)
        self.Incoming = incoming
        self.Network = network

    def run(self):
        # dprint("Recieved from BaseMoteino:  " + self.Incoming)

        # The first byte from the hex string is the sender ID.
        # We use that to get a pointer to the sender (an instance of the Node class)

        sender_id = Byte.hex2dec(self.Incoming[:2])
        if sender_id not in self.Network.nodes:
            logging.warning("Something must be wrong because BaseMoteino just recieved a message "
                            "from moteino with ID: " + str(sender_id) + " but no such node has "
                            "been registered to the network. Btw the raw data was: " + self.Incoming)
        else:
            sender = self.Network.nodes[sender_id]
            sender.send2parent(self.Incoming[2:])


class ListeningThread(threading.Thread):
    """
    A thread that listens to the Serial port. When something (that ends with a newline) is recieved
    the thread will start up a Send2Parent thread and go back to listening to the Serial port
    """
    def __init__(self, network, listen2):
        threading.Thread.__init__(self)
        self.Network = network
        self.Listen2 = listen2

    def stop(self):
        self.Listen2.close()

    def run(self):
        logging.debug("Serial listening thread started")
        while True:
            try:
                incoming = self.Listen2.readline()
            except serial.SerialException as e:
                logging.warning("serial exception ocuurred: " + str(e))
                break
            incoming.rstrip(b'\n')  # use [:-1]?
            logging.debug("Serial port said: " + str(incoming))
            fire = Send2ParentThread(self.Network, incoming)
            fire.start()
        logging.info("Serial listening thread shutting down")

RF69_315MHZ = 31
RF69_433MHZ = 43
RF69_868MHZ = 86
RF69_915MHZ = 91


class MoteinoNetwork(object):
    """
    This is the class that user should inteface with. It is a module that
    ables the user to communicate with moteinos through a top level script.

    """

    RF69_315MHZ = 31
    RF69_433MHZ = 43
    RF69_868MHZ = 86
    RF69_915MHZ = 91

    def __init__(self,
                 port,
                 frequency=RF69_433MHZ,
                 high_power=True,
                 network_id=1,
                 base_id=1,
                 encryption_key="0123456789abcdef"):

        # initiate serial port and base
        self._Serial = MySerial(port=port,
                                baudrate=115200)
        self._initiate_base(frequency, high_power, network_id, base_id, encryption_key)

        # threading objects
        self._SerialLock = threading.Lock()
        self._WaitForRadioEvent = threading.Event()

        # operating variables
        self.ReceiveWithSendAndReceive = False
        self.print_when_acks_recieved = False

        self.nodes = dict()
        self._serial_listening_thread = None
        self._serial_listening_thread_is_active = False
        self.max_wait = 500
        self.LastReceived = None
        self.NodeCounter = 0

        # Base is technically a node on the network that informs us of wheter or not ACKs are
        # received and hopefully someday the RSSI and such.
        self.BaseMoteino = BaseMoteino(self, base_id)
        self._add_node(self.BaseMoteino)
        self.start_listening()

    def _initiate_base(self,
                       frequency=RF69_433MHZ,
                       high_power=True,
                       network_id=1,
                       base_id=1,
                       encryption_key="0123456789abcdef"):
        self._Serial.write('X')     # send reset sign
        logging.debug("Restarting base")
        time.sleep(0.6)  # sleep  for 0.6 seconds, bootloader uses 0.5 seconds
        logging.debug("Waiting for wakeup sign from base...")
        incoming = self._Serial.readline().rstrip()
        assert incoming == b"moteinopy basesketch v2.2"
        logging.debug("... got it, base with " + str(incoming) + " seems to be present, sending operating values...")
        encryption_key_hex = ""
        for x in encryption_key:
            encryption_key_hex += Char.hex(x)
        self._Serial.write(Byte.hex(frequency) +
                           Byte.hex(base_id) +
                           Byte.hex(network_id) +
                           Byte.hex(high_power) +
                           encryption_key_hex + "\n")
        logging.debug("waiting for ready sign from base...")
        incoming = self._Serial.readline().rstrip()
        assert incoming == b"Ready"
        logging.debug("... got it, base is ready!")

    def _wait_for_radio(self, max_wait=None):
        """
        There are two reasons for waiting for radio.
            1 - When the base sends a packet and waits for an ACK
                it is not processing from the serial port. If we would
                just keep printing more and more packets to send, it
                might fill the buffer on the BaseMoteino's serial port
                and cause lost data.
            2 - It is preferable that nodes on the network act mostly
                like slaves, that is, don't talk much unless asked to.
                Most tyoes of information should therefore be requested
                by the master (the users python script). In this case
                the user should call mynetwork.send() with expect_response
                as True. This will cause the module to wait until it
                recieves a packet or the max_wait period expires.

        :param max_wait: int
        """
        if max_wait is None:
            max_wait = self.max_wait
        logging.debug("waiting for radio....")
        t = time.time()
        self._WaitForRadioEvent.wait(max_wait/float(1000))
        logging.debug("I waited for radio for " + str((time.time() - t)*1000) + " ms")

    def stop_waiting_for_radio(self):
        """
        pretty obvious....
        :return:
        """
        self._WaitForRadioEvent.set()

    def send2base(self, send2id, payload, max_wait=None):
        """
        To prevent multiple threads from printing to the Serial port at the same time
        all printing is done through this function and using the threading.Lock() module
        :param send2id: int
        :param payload: str
        :param max_wait: int
        """
        with self._SerialLock:
            self._Serial.write(Byte.hex(send2id) + payload + '\n')
            logging.debug("we sent: " + Byte.hex(send2id) + payload + "  to the serial port")
            self._WaitForRadioEvent.clear()
            self._wait_for_radio(max_wait=max_wait)

    def _add_node(self, node):
        """
        A private method that adds node to the networks list of nodes
        :param node: Node
        :return:
        """
        self.nodes[node.Name] = node
        self.nodes[node.ID] = node
        logging.info(str(node) + " added to the network.")

    def add_node(self, _id, structstring, name=''):
        """
        This function defines a node on the network
        :param name: str
        :param _id: int
        :param structstring: str
        """
        if _id == 0xFF:
            raise ValueError("Node ID can't be 255 (0xFF) because that " +
                             "is reserved for the base")

        d = Node(network=self,
                 _id=_id,
                 structstring=structstring,
                 name=name)
        self._add_node(d)

        return d

    def send_and_receive(self, send2, *args, **kwargs):
        """
        This function can be called from top level script. It sends the
        information found in diction to the node specified with send2.
        It will then wait until the network received something and return
        what was received. This will prevent the receive() function from
        being called.

        :param send2: str or Node
        :return: dict
        """
        if type(send2) is str or type(send2) is int:
            return self.nodes[send2].send_and_receive(*args, **kwargs)
        elif type(send2) is Node:
            return send2.send_and_receive(*args, **kwargs)
        else:
            raise ValueError("send2 must be string, int or Node but was " + str(type(send2)))

    def send(self, send2, *args, **kwargs):
        """
        This function should be called from top level script to send someting.
        Input parameter diction is a dict that contains what should be sent.
        The structure of diction depends on the struct that the node expects.
        Any parameter missing in diction will be assumed to be 0

        :param send2: str or Node
        """
        if type(send2) is str or type(send2) is int:
            self.nodes[send2].send(*args, **kwargs)
        elif type(send2) is Node:
            send2.send(*args, **kwargs)
        else:
            raise ValueError("send2 must be string, int or Node but was " + str(type(send2)))

    def start_listening(self):  # starts a thread that listens to the serial port
        if not self._serial_listening_thread_is_active:
            self._serial_listening_thread = ListeningThread(network=self, listen2=self._Serial)
            if not self._Serial.isOpen():
                self._Serial.open()
            self._serial_listening_thread.start()
            self._serial_listening_thread_is_active = True

    def stop_listening(self):
        self._serial_listening_thread.stop()
        self._Serial.close()
        self._serial_listening_thread_is_active = False

    def receive(self, sender, diction):
        """
        User should overwrite this function
        :param sender: Node
        :param diction: dict
        """
        print("MoteinoNetwork received: " + str(diction) + "from" + sender.Name)

    def no_ack(self, sender, last_sent_diction):
        """
        User might want to overwrite this function
        :param sender: Node
        :param last_sent_diction: dict
        """
        print("Oh no! We didn't recieve an ACK from " + sender.Name + " when we sent " + str(last_sent_diction))

    def ack(self, sender, last_sent_diction):
        """
        This function is totally unnecessary.... mostly for debugging but maybe
        it will be useful someday to overwrite this with something
        :param sender: Node
        :param last_sent_diction: dict
        """
        if self.print_when_acks_recieved:
            print(sender.Name + " responded with an ack when we sent: " + str(last_sent_diction))
