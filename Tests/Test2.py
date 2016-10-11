from moteinopyCode import MoteinoNetwork23 as MN
import logging

logging.basicConfig(level=logging.DEBUG)

# mynetwork = MN('COM50', network_id=7, encryption_key="HugiBogiHugiBogi", )
mynetwork = MN('COM50', init_base=False)

mynetwork.add_global_translation('Command',
                                 ('Status', 99),
                                 ('Reset', 98))

GreenDude = mynetwork.add_node(11, "unsigned int Command;"
                                   "byte Lights[7];"
                                   "byte Temperature;", "GreenDude")

GreenDude.add_translation('Command',
                          ('Disp', 1101),
                          ('SetPasscode', 1102),
                          ('CorrectPasscode', 1103))
