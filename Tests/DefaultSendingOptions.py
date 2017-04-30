from moteinopy import MoteinoNetwork
import logging

logging.basicConfig(level=logging.DEBUG)

mn = MoteinoNetwork("", init_base=False, base_id=100)

n1 = mn.add_node(1, "int a;")