from moteinopy import MoteinoNetwork
import logging

logging.basicConfig(level=logging.DEBUG)

mynetwork = MoteinoNetwork('Com50', init_base=False)

# old: add translation to a single node
node0 = mynetwork.add_node(10, "int Command;", "node0")
node0.add_translation("Command", ("zero", 0), ("minusOne", -1))
node0.send("zero")


# new:  add global translation that will be added to all nodes,
#       regardless of when thay are added (before or after the
#       global translation)

mynetwork.add_global_translation('Command', ('one', 1), ('two', 2))

node2 = mynetwork.add_node(2, "int Command;", "node1")

mynetwork.add_global_translation('Command', ('three', 3), ('four', 4))

node3 = mynetwork.add_node(3, 'int Command;', 'node2')

node2.send("one")
node3.send("one")
node2.send("three")
node3.send("four")


# Also test that translations don't inverse when they shouldn't
node3.send(1)
