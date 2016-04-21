
=========
Moteinopy
=========
****************************************
Direct communication from python to node
****************************************
 This module was written to handle communication on a moteino network. `Moteinos <http://lowpowerlab.com/moteino>`_
 are great little arduino clones that have an onboard RFM69 which gives them wireless  capabilities. This makes them great for home automation or similar situation.

This module assumes a setup of the form:

.. image:: http://i.imgur.com/F4kzhbd.png
    :width: 300px
    :align: center
    :height: 300px
    :alt: alternate text

BaseMoteino should be programmed with the BaseSketch that can be found on the `GitHub <https://github.com/Steinarr134/moteinopy>`_
site. Note that you will have to edit it to match your radio settings.
I recommend reading through the examples scripts on GitHub to see how to use the module

**************
How to install
**************
Just use  ``pip install moteinopy``