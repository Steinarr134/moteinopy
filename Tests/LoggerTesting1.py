import logging
from moteinopy import MoteinoNetwork

# logging.basicConfig(level=logging.INFO)
moteinologger = logging.getLogger('moteinopy')
moteinologger.setLevel(logging.DEBUG)
moteinologger.debug("sadfsf")


mn = MoteinoNetwork(False)
node1 = mn.add_node(10, "int bla;")
print(node1.Name)
mn.shut_down()