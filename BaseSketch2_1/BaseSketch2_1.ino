// This is a sketch written for a base. The base is a moteino that acts as a gateway between 
// a PC and other moteinos. It is connected to the PC through a serial port and relays info
// to and from the radio network.

// The sketch is a mash up between the gateway, struct send and the struct recieve sketches 
// of the moteino library.

// Written by Steinarr
////////////////////////////////////////////////////////////////////////////////////////////

// our includes:
#include <RFM69.h>    
#include <SPI.h>

// our defines
#define NODEID        1    // Unique for each node on same network, this is the base and it 
                           // gets to have the ID of 1  
#define NETWORKID     7    //the same on all nodes that talk to each other
//Match frequency to the hardware version of the radio on your Moteino:
#define FREQUENCY     RF69_433MHZ
#define ENCRYPTKEY    "HugiBogiHugiBogi" //exactly the same 16 characters/bytes on all nodes!
#define SERIAL_BAUD   115200
RFM69 radio;
bool promiscuousMode = false; // set to 'true' to sniff all packets on the same network


// Here we are defining "Payload" as a type of struct, in our case it contains an array of 11 ints
typedef struct{byte N[61]; } Payload; 

// and here we define "OutgoingData" as a Payload. Most people are more familiar with seeing something
// like: "int A" where we define A as an int. In the same way ae are defining OutgoingData as a Payload.
// Remember we just defined "Payload" as a type of structure.
Payload OutgoingData;  
Payload IncomingData; // Same goes for IncomingData

// In order to do less calculating at runtime i figured i would define a global variable to hold the size
// (Because this base will always be sending and recieving the same structure)
byte DataLen = sizeof(OutgoingData);

byte NoAck = 1;

void setup() 
{ // Setup runs once
  Serial.begin(SERIAL_BAUD);
  delay(10);
  radio.initialize(FREQUENCY,NODEID,NETWORKID);
  radio.setHighPower(); //only for RFM69HW! (all of ours are HW)
  radio.encrypt(ENCRYPTKEY);
  radio.promiscuous(promiscuousMode);
  Serial.println("Ready");
}
// Global variables to recieve incoming serial messages
char FirstHex; // Temp will hold our string that contains the number
int Send2ID = 0;
boolean FirstHexDone = 0;  // TempLen will keep track of how long Temp is
byte Counter = 0; // Counter keeps count of how many numbers have been recieved.
boolean Send2IDDone = 0;


void loop() 
{  //loop runs over and over forever
   // we want to do 2 thing at once, Listen to the Serial port and the radio. We can't 
   // actually do both at the 'same' time but we can do one and then the other, extremely fast.
  
  // So, lets first process any serial input:
  if (Serial.available() > 0)
  {
    // The string will be on the form (Send2ID)#(number1):(number2):    with up to 10 numbers.
    // every number will be 'terminated' by a ':'
    char incoming = Serial.read(); // reads one char from the buffer
    if (incoming == '\n')
    { // if the line is over
      sendTheStuff();
      Send2IDDone = 0;
      Counter = 0;
    }
    else
    {
      if (FirstHexDone)
      {
        FirstHexDone = 0;
        if (Send2IDDone)
        {
          OutgoingData.N[Counter] = FirstHex*16+hexval(incoming);
          Counter++;
        }
        else
        {
          Send2IDDone = 1;
          Send2ID = FirstHex*16 + hexval(incoming);
        }
      }
      else
      {
        FirstHex = hexval(incoming);
        FirstHexDone = 1;
      }
    }
  }
  
  // and then check on the radio:
  
  // The radio is always listening and recieving but doesn't respond on its own,
  // We have to constantly check if something has been recieved and answer with an ACK
  if (radio.receiveDone())
  {
    // First lets put what we recieved into IncomingData. We have to do this before we 
    // send the ACK because the radio.DATA cache will be overwritten when sending the ACK.
    IncomingData = *(Payload*)radio.DATA;
    hexprint(radio.SENDERID); // radio.SENDERID will also be overwritten so let's print it now
    if (radio.ACKRequested())
    {
      radio.sendACK();
    }
    for (byte i = 0; i < 61; i++)
    {
      hexprint(IncomingData.N[i]);
    }
    Serial.println();
  }
}

void hexprint(byte b)
{
  if (b<16)
  {
    Serial.print('0');
  }
  Serial.print(b, HEX);
}

byte hexval(char c)
{
  if (c <= '9')
  {
    return c - '0';
  }
  else if (c <= 'F')
  {
    return 10 + c - 'A';
  }
  else
  {
    return 10 + c - 'a';
  }
}

void sendTheStuff()
{
  /*Serial.print("sending stuff to: ");
  Serial.println(Send2ID);
  for (byte i = 0; i<7; i++)
  {
    Serial.print(OutgoingData.N[i]);
    Serial.print(", ");
  }*/
  bool success = radio.sendWithRetry(Send2ID,(const void*)(&OutgoingData),sizeof(OutgoingData));
  if (success)
  {
    Serial.print("FF");
    hexprint(Send2ID);
    Serial.println("01");
  }
  else
  {
    Serial.print("FF");
    hexprint(Send2ID);
    Serial.println("00");
  }
}
