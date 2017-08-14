"""
This script is to intoduce the user to the syntax and:

How do define the nodes
How to send data

"""

from moteinopy import MoteinoNetwork
import logging

# let's set the logging level to debug, this way we can better see what is happening during runtime.
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":

    # Alright! Now for some interfacing examples. I'll split this into some groups using if and elif
    # so they can still be run individually.

    # First let's instantiate our network:
    # Check out the InitiatingNetwork example for more on this.

    # Passing '' or False will make the module skip the base connection,
    # this will of course provide no functionality but is useful for running these
    # examples if you don't have a base present. Anything you throw at a node will
    # just come right back at you, 50ms later.
    mynetwork = MoteinoNetwork(False)

    # For the sake of this example I am imagining a device called TestNode.
    # It is on the network and it has NODEID=10. It is expecting a struct
    # that in the arduino code is defined as:
    #     struct def{
    #         int   info;
    #         int   numbers[5];
    #     } Payload;

    example = 1

    if example == 1:  # starting off easy
        # scenario:    We want to send info=5 and numbers={1,2,3,4,5}

        # First we add the device to the network, like so:
        mynetwork.add_node(_id=10,  # I had to underscore id to prevent naming conflict :/
                           structstring="int info;" + "int numbers[5];",
                           name='TestNode',)

        # Now we can send data using the send method, you can for example pass
        # keyword arguments matching what you defined in the structstring (case sensitive)
        mynetwork.send('TestNode', info=5, numbers=[1, 2, 3, 4, 5])

    elif example == 2:  # using the Device class and *args

        # scenario:     We want to send info=5 and numbers={1,2,3,4,5} (alternative)

        # We can also add to network and get a handle to the node.
        TestNode = mynetwork.add_node(10, "int info;" + "int numbers[5];", 'TestNode')

        # We can also pass it arguments in the same order as the structstring
        TestNode.send(5, [1, 2, 3, 4, 5])

    elif example == 3:  # using send_and_receive
        # Scenario:  We want to receive some info from TestNode. This means that we
        # must send it a request and then wait while the Node gathers that info and
        # sends it to us.

        TestNode = mynetwork.add_node(10, "int info;" + "int numbers[5];")
        # by skipping the name parameter the module will assign a default name: Node-(id)
        # in this case: Node-10

        # For this we can use the send_and_receive function. This function sends the data
        # just like send does but then waits for the node to respond. When the node responds
        # this function will return the diction instead of mynetwork calling the receive method

        Response = TestNode.send_and_receive(info=123, max_wait=2000)

        # Btw, you may have noticed that we didn't specify 'numbers'. That is ok, the module will
        # assume that it is zero. We also specified the max wait time (in milliseonds) if this is
        # not specified the default wait time (500ms) will be used. You can adjust the default with
        # mynetwork.max_wait

        # If something fails and we don't get a response then Response will be None
        if Response:
            print(Response['numbers'])
        else:
            print("It didn't work, we got nothing :(")

    elif example == 4:  # using the translation service to make code more readable

        TestNode = mynetwork.add_node(10, "int info;" + "int numbers[5];", 'TestNode')

        # The module has a built in translation service, let's redo our example number 3
        # using the translation service.

        TestNode.add_translation('info',
                                 ('SendMeNumbers', 123),
                                 ('HereAreTheNumbers', 124))
        # The syntax is add_translation(part, *args) where args are tuples of what should be
        # translated into what

        # And now we can use :
        Response = TestNode.send_and_receive('SendNumbers')

        if not Response:
            print("Oh, no!, no Response :( ")
        else:
            if Response['info'] == "HereAreTheNumbers":
                print(Response["numbers"])

        # The only purpose for this translation service is making your code more readable,
        # If it is confusing you then you can safely just not use it.


# That's all for now folks, I'll add some more examples if requested

