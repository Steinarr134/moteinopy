from moteinopy import MoteinoNetwork

"""
This is an example sketch intended to show how to receive data from a node
on the network.
If you haven't read the SendingData example I suggest you start with that one


There are three ways to receive data:

1. Using send_and_receive.
    We already covered this in the SendingData example

2. By creating a dedicated receive function for each node and binding it

3. By writing a default receive function and overwriting the network's default receiving function.

"""
# So let's keep up with the SendingData example, I suggest reading that one first, if you haven't
# already. We imagine a Node on the network called TestNode and expects a struct defined by:
#     struct def{
#         int   info;
#         int   numbers[5];
#     } Payload;


# Here you should start thinking about what you want to do with the network.
# There are three functions that you might want to overwrite. Those are:
# receive() - run if something is received from the network
# ack()     - run if Base gets an ack after sending something
# no_ack()  - run if Base sends something but doesn't receive an ack
# These functions will be run in a new thread that you are allowed to hijack.
# How cool is that?!

# Here are those functions as they look by default in the source code:

def default_receive(diction):
    """
    The default fucntion called when network receives something
    :param diction: dict
    """
    print("MoteinoNetwork received: " + str(diction) + " from " + diction['SenderName'])


def default_no_ack(last_sent_diction):
    """
    The default fucntion called when network receives no ack after sending something
    :param last_sent_diction: dict
    """
    sender = last_sent_diction['Sender']
    print("Oh no! We didn't recieve an ACK from " + sender.Name + " when we sent " + str(last_sent_diction))


def default_ack(last_sent_diction):
    """
    The default fucntion called when network receives an ack after sending something.
    This function is essentially unnecessary.... mostly for debugging but maybe
    it will be useful someday to overwrite this with something
    :param last_sent_diction: dict
    """
    pass


# Now you might be wandering what those dictions are... diction is my made up name for python's
# dictionary or dict() datatype. But what do these dictionaries contain you might ask.
# Well, I mentioned that the Moteinos are sending and receiving a struct.
# Those dictions are the struct that you are expecting from said Moteino in the form of a dict()


# First up, instantiate your network and define our TestNode
mynetwork = MoteinoNetwork(False)
TestNode = mynetwork.add_node(10, "int info;" + "int numbers[5];", 'TestNode')

# By default, If a node sends something the default_receive function will be called but
# we can also define a new function for each node:


def test_node_receive(diction):
    if diction['info'] == 1234:
        # Do something with what you receive, I'll just print it here but you could do whatever
        # you want with it
        print(diction['numbers'])

# and finally we bind it to our TestNode
TestNode.bind(receive=test_node_receive)

# Now, every time TestNode sends us something, test_node_receive will be run instead of
# default_receive

# We can also change the default functions:


def my_no_ack(last_sent_diction):
    print("No ack when sending: " + str(last_sent_diction))

mynetwork.bind_default(no_ack=my_no_ack)
