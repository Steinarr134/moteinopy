from moteinopy import MoteinoNetwork
import logging

logging.basicConfig(level=logging.DEBUG)


def r1(d):
    print("r1 receive function: \t" + str(d))


def r2(d):
    print("r2 receive function: \t" + str(d))


def r3(d):
    print("r3 receive function: \t" + str(d))

# Initialize network, using FakeSerial
mn = MoteinoNetwork("", init_base=False, base_id=100)

# add node 1
node1 = mn.add_node(1, "int a;")
node1.send()

# r1 to default
mn.bind_default(receive=r1)
node1.send(10)  # should print with r1 as that is default

node2 = mn.add_node(2, "int a;")
node2.send(10)  # should also print with r1 as that is default

node2.bind(receive=r2)
node2.send(10)  # should print with r2

mn.shut_down()
