from moteinopy import MoteinoNetwork
import logging
from time import sleep

logging.basicConfig(level=logging.DEBUG)

mynetwork = MoteinoNetwork(port='COM11')

sleep(1)
print("network initiated")
sleep(4)

mynetwork.shut_down()
sleep(1)
print("network shut down")
sleep(2)


print("starting it up again")
sleep(1)
mynetwork = MoteinoNetwork('COM11', encryption_key="HugiBogiHugiBogi")

sleep(1)
print("done")

