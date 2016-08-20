"""
This is a script intended to show the usage of the module called Moteinopy

The module is a my way of directly communicating from top level python scripts
to Moteinos.

The setup looks like this:

A PC (or RasPi) running a python script is connected to a BaseMoteino through
a serial port. That BaseMoteino then relays data to other Moteinos ( also called nodes),
wherever they might be and back.

Those Moteinos (nodes) should be expecting a struct. (check out the struct examples
of the moteino library to familiarize yourself with the concept) As should be expected,
this script and the nodes must agree on the struct that they will receive.

Thus far this module only supports one type of struct per node.
"""

# let's start by importing the MoteinoNetwork class.
from moteinopy import MoteinoNetwork

# To make things more plug-and-play the network parameters are passed
# to the base from this script. So we'll have to parse them in here

mynetwork = MoteinoNetwork(port='COM50',
                           frequency=MoteinoNetwork.RF69_433MHZ,
                           high_power=True,
                           network_id=1,
                           base_id=1,
                           encryption_key='0123456789ABCDEF')

# Those are the default values but selecting other ones is pretty straight forward

