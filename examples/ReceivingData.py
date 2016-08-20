from moteinopy import MoteinoNetwork

"""
This is an example sketch intended to show how to receive data from a node
on the network.
If you haven't read the SendingData example I suggest you start with that one


There are three ways to receive data:

1. Using send_and_receive.
    We already covered this in the SendingData example

2. By overwriting the MoteinoNetwork.receive function

3. By writing a function and binding it to the Node

"""
# So let's keep up with the SendingData example, I suggest reading that one first, if you haven't
# already. We imagine a Node on the network called TestNode and expects a struct defined by:
#     struct def{
#         int   info;
#         int   numbers[5];
#     } Payload;


# We start by creating a our own subclass of the MoteinoNetwork. This
# allows us to overwrite the default receive, ack and no_ack functions,
# Let's call our class MyNetwork.
class MyNetwork(MoteinoNetwork):
    def __init__(self):
        # Just like all good subclasses it starts by initializing the superclass.
        # Here we'll also pass on the Serial port info
        MoteinoNetwork.__init__(self, port='COM50')

    # Here you should start thinking about what you want to do with the network.
    # There are three functions that you might want to overwrite. Those are:
    # receive() - run if something is received from the network
    # ack()     - run if Base gets an ack after sending something
    # no_ack()  - run if Base sends something but doesn't receive an ack
    # These functions will be run in a new thread that you are allowed to hijack.
    # How cool is that?! (be careful though. If you make the threads run something
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
        This function is totally unnecessary.... mostly for debugging but maybe
        it will be useful someday to overwrite this with something
        :param sender: Device
        :param last_sent_diction: dict
        """
        if self.print_when_acks_recieved:
            print(sender.Name + " responded with an ack when we sent: " + str(last_sent_diction))


# Now you might be wandering what those dictions are... diction is my made up name for python's
# dictionary or dict() datatype. But what do these dictionaries contain you might ask.
# Well, I mentioned that the Moteinos are sending and receiving a struct.
# Those dictions are the struct that you are expecting from said Moteino in the form of a dict()


# First up, instantiate your network and define our TestNode
mynetwork = MyNetwork()
TestNode = mynetwork.add_device('TestNode', 10, "int info;" + "int numbers[5];")

# By default, If a node sends something the MoteinoNetwork.receive function will be called but
# we can also define a new function for each node:


def test_node_receive(diction):
    if diction['info'] == 1234:
        # Do something with what you receive, I'll just print it here but you could do whatever
        # you want with it
        print(diction['numbers'])

# and finally we bind it to our TestNode
TestNode.bind(receive=test_node_receive)

# Now, every time TestNode sends us something, test_node_receive will be run instead of
# mynetwork.receive.



