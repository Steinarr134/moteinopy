from moteinopy import MoteinoNetwork

mynetwork = MoteinoNetwork('COM50')

mynode = mynetwork.add_device(10, "int command", "TestNode")

mynode.send(Command=1234)