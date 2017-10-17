from moteinopy import MoteinoNetwork as MN
import logging
import time

logging.basicConfig(level=logging.DEBUG)


mn = MN("/dev/ttyUSB1")

time.sleep(2)

print "shutting network down..."
mn.shut_down()