
from moteinopy import MoteinoNetwork

"""
This is a script intended to show the usage of the module called MoteinoBeta

The module is a my way of directly communicating from top level python scripts
to Moteinos.

The setup looks like this:

A PC (or RasPi) running a python script is connected to a BaseMoteino through
a serial port. That BaseMoteino then releys data to other Moteinos, wherever
they might be and back.

Those Moteinos should be expecting a struct. (check out the struct examples
of the moteino library) As should be expected, this script and the Moteinos
must agree on the struct that they will receive.
"""


# We start by creating a our own subclass of the MoteinoNetwork. Let's
# call our class MyNetwork. Notice that you should only make 1 instance
# of this class.
class MyNetwork(MoteinoNetwork):
    def __init__(self):
        # Just like all good subclasses it starts by initializing the superclass.
        # Here we'll also pass on the Serial port info
        MoteinoNetwork.__init__(self, port='COM51', baudrate=115200)

    # Here you should start thinking about what you want to do with the network.
    # There are three functions that you might want to overwrite. Those are:
    # receive() - run if something is received from the network
    # ack()     - run if Base gets an ack after sending something
    # no_ack()  - run if Base sends something but doesn't receive an ack
    # These functions will be run in a new thread that you are allowed to hijack.
    # How cool is that?! (be carefull though. If you make the threads run something
    # time consuming you could end up with too many threads running and some nasty
    # stuff might happen, or not.... I'm no expert. But they probably do
    # implement thread pools for a reason....)

    # Here are those functions as they look by default in the source code:

    def receive(self, sender, diction):
        """
        User should overwrite this function
        :param sender: Device
        :param diction: dict
        """
        print("MoteinoNetwork received: " + str(diction) + " from " + sender.Name)

    def no_ack(self, sender, last_sent_diction):
        """
        User might want to overwrite this function
        :param sender: Device
        :param last_sent_diction: dict
        """
        print("Oh no! We didn't recieve an ACK from " + sender.Name + " when we sent " + str(last_sent_diction))

    def ack(self, sender, last_sent_diction):
        """
        This funcion is totally unnecessary.... mostly for debugging but maybe
        it will be usefull someday to overwrite this with something
        :param sender: Device
        :param last_sent_diction: dict
        """
        if self.print_when_acks_recieved:
            print(sender.Name + " responded with an ack when we sent: " + str(last_sent_diction))


# Now you might be wandering what those dictions are... diction is my made up name for python's
# dictionary or dict() datatype. But what do these dictionaries contain you might ask. Well, in
# the introductary docstring I mentioned that the Moteinos are sending and receiving a struct.
# Those dictions are the struct that you are expecting from said Moteino in the form of a dict()

if __name__ == "__main__":

    # Alright! Now for some interfacing examples. I'll split this into some groubs using if and elif
    # so they can still be run individually.

    # First let's instantiate our network:
    mynetwork = MyNetwork()

    # For the sake of this example I am imagining a device called TestNode.
    # It is on the network and it has NODEID=10. It is expecting a struct
    # that in the arduino code is defined as:
    #     struct def{
    #         int   info;
    #         int   numbers[5];
    #     } Payload;

    example = 1

    if example == 1:
        # scenario::    We want to send info=5 and numbers = {1,2,3,4,5}

        # First we add the device to the network, like so:
        mynetwork.add_device(name='TestNode',
                             _id=10,  # I had to underscore id to prevent naming conflict :/
                             structstring="int info;" + "int numbers[5];")

        mynetwork.send('TestNode', {'info': 5, 'numbers': [1, 2, 3, 4, 5]})

    elif example == 2:
        # scenario:     We want to send info=5 and numbers = {1,2,3,4,5} (alternetive)

        # We can also add to network and get a handle to the node.
        TestNode = mynetwork.add_device('TestNode', 10, "int info;" + "int numbers[5];")

        TestNode.send({'info': 5, 'numbers': [1, 2, 3, 4, 5]})

    elif example == 3:
        # Scenario:     We want to receive some info from TestNode. This means that we
        # must send it a request and then wait while the Node gathers that info and
        # sends it to us.

        TestNode = mynetwork.add_device('TestNode', 10, "int info;" + "int numbers[5];")

        # For this we can use the send_and_receive function. This function sends the data
        # just like send does but then waits for the node to respond. When the node responds
        # this function will return the diction instead of mynetwork calling the receive method

        Response = TestNode.send_and_receive({'info': 123}, max_wait=2000)

        # Btw, you may have noticed that we didn't specify 'numbers'. That is ok, the module will
        # assume that it is zero. We also specified the max wait time (in milliseonds) if this is
        # not specified the default wait time will be used. You can adjust the default with
        # mynetwork.max_wait

        # If something fails and we don't get a response then Response will be None
        if Response:
            print(Response['numbers'])
        else:
            print("It didn't work, we got nothing :(")


#     That's all for now folks, I'll add some more examples if requested

