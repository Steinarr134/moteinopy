from moteinopyCode import MoteinoNetwork
import logging
from time import sleep

logging.basicConfig(level=logging.DEBUG)

mynetwork = MoteinoNetwork('Com50', init_base=False)

node = mynetwork.add_node(10, "int Command", "node1")

sleep(3)
print("now")
sleep(0.2)
print(node.send(123))