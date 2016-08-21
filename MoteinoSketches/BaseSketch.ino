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

byte self_id = 0;

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
byte DataLen = sizeof(OutgoingData); // = 61

byte NoAck = 1;

void setup() 
{ // Setup runs once
  Serial.begin(115200);
  delay(10);
  Serial.println("moteinopy basesketch v2.2");
  byte buff[50] = {0};
  byte i = 0;
  bool first_hex_done = false;
  char first_hex = 0;
  while (i < 50)
  {
    if (Serial.available())
    {
      byte in = Serial.read();
      if (in == '\n')
      {
        //Serial.println("newline received");
        i = 100;
      }
      else
      {
        if (first_hex_done)
        {
          buff[i] = first_hex*16 + hexval(in);
          i++;
        }
        else
        {
          first_hex = hexval(in);
        }
        first_hex_done = !first_hex_done;
      }
    }
  }
  typedef struct {
    byte frequency;
    byte base_id;
    byte network_id;
    bool high_power;
    char encryption_key[16];
  } init_struct;
  init_struct init_info = *(init_struct*)buff;
//  Serial.print("freq\t");
//  Serial.print(init_info.frequency);
//  Serial.print("\t");
//  Serial.println(RF69_433MHZ);
//  Serial.print("b_id\t");
//  Serial.println(init_info.base_id);
//  Serial.print("n_id\t");
//  Serial.println(init_info.network_id);
//  Serial.print("encrypkey\t");
//  Serial.println(init_info.encryption_key);

  self_id = init_info.base_id;
  
  radio.initialize(init_info.frequency, init_info.base_id, init_info.network_id);
  if (init_info.high_power)
  {
      radio.setHighPower(); //only for RFM69HW!

  }
  radio.encrypt(init_info.encryption_key);
  radio.promiscuous(promiscuousMode);
  digitalWrite(9, HIGH);
  delay(25);
  Serial.println("Ready");
  digitalWrite(9, LOW);
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
    else if (incoming == 'X')
    {
      //Serial.println("RESTART");
      //delay(50);
      asm volatile ("  jmp 0");
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
  hexprint(self_id);
  hexprint(Send2ID);
  hexprint(success);
  hexprint((byte)(radio.RSSI + 0x7F));
  Serial.println();
  
}
