Moteinopy
=========

Direct communication from python to node
----------------------------------------

This module was written to handle communication on a moteino network. [Moteinos] are great little arduino clones that have an onboard RFM69 which gives them wireless capabilities. This makes them great for home automation or similar situation.

This module assumes a setup of the form:

<img src="http://i.imgur.com/Ql9gJXe.png" alt="alternate text" width="300" height="300" />

BaseMoteino should be programmed with the BaseSketch that can be found on the [GitHub] site. 

I recommend reading through the examples scripts on GitHub to see how to use the module

How to install
--------------

Just use `pip install moteinopy` for the python module

Then go to the [GitHub] repository, under MoteinoSketches get the BaseSketch_v2.3.ino, download it and upload to your BaseMoteino using the arduino IDE.

You can check that it is working by opening the serial monitor (set it to 115200 baudrate) and the base should print 'moteinopy basesketch v_2.3' on startup. 

Getting started
---------------

The examples should give you some insight into the module's capabilities and syntax so I suggest reading those. If this is your first experience with moteinos then you should start by reading through the [Moteino documentation](http://lowpowerlab.com/moteino).

Included in the [GitHub] repository is an Node_Skeleton.ino sketch that is a simplified variant of the struct-receive.ino sketch from the moteino library. Feel free to use it as a starting point for your nodes.


  [Moteinos]: http://lowpowerlab.com/moteino
  [GitHub]: https://github.com/Steinarr134/moteinopy
