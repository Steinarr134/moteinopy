// This is a sketch written for a base. The base is a moteino that acts as a gateway between
// a PC and other moteinos. It is connected to the PC through a serial port and relays info
// to and from the radio network.

// The sketch is a mash up between the gateway, struct send and the struct recieve sketches
// of the moteino library.

// Written by Steinarr
////////////////////////////////////////////////////////////////////////////////////////////

#include <RFM69.h>
#include <SPI.h>
byte self_id = 0xff; // default but changable through python
RFM69 radio;
bool promiscuousMode = true; // set to 'true' to sniff all packets on the same network

// Incoming and Outgoing buffers:
typedef struct {byte x[61];} Payload;
Payload RadioBuffer;
byte SerialBuffer[63];

typedef struct{
  byte sender;
  byte send2;
  byte rssi;
} RadioStruct;

typedef struct{
  byte send2id;
  bool ack_requested;
  byte buffer[61];
} SerialStruct;

SerialStruct s;
RadioStruct r;

void setup()
{ // Setup runs once
  Serial.begin(115200);
  delay(10);
  Serial.println("moteinopy basesketch v2.3");
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
char FirstHex;
boolean FirstHexDone = 0;
byte SerialCounter = 0; // Counter keeps count of how many bytes have been recieved.
byte SerialBufferLen = 0;
byte datalen = 0;


void loop()
{  //loop runs over and over forever
   // we want to do 2 thing at once, Listen to the Serial port and the radio. We can't
   // actually do both at the 'same' time but we can do one and then the other, extremely fast.

  // So, lets first process any serial input:
  checkOnSerial();

  // and then check on the radio:
  // The radio is always listening and recieving but doesn't respond on its own,
  // We have to constantly check if something has been recieved and answer with an ACK
  checkOnRadio();
}

void checkOnSerial()
{
if (Serial.available() > 0)
  {
    char incoming = Serial.read(); // reads one char from the buffer
    if (incoming == '\n')
    { // if the line is over
      sendTheStuff();
      SerialBufferLen = SerialCounter;
      SerialCounter = 0;
    }
    else if (incoming == 'X')
    {
      //Serial.println("RESTART");
      //delay(50);
      asm volatile ("  jmp 0");
    }
    else
    {
      // each byte is represented as 2 hex characters
      if (FirstHexDone)
      {
        FirstHexDone = false;
        SerialBuffer[SerialCounter] = (FirstHex<<4) & hexval(incoming);
        SerialCounter++;
      }
      else
      {
        FirstHex = hexval(incoming);
        FirstHexDone = true;
      }
    }
  }
}

void checkOnRadio()
{
  if (radio.receiveDone())
  {
    // First lets put what we recieved into IncomingData. We have to do this before we
    // send the ACK because the radio.DATA cache will be overwritten when sending the ACK.
    RadioBuffer = *(Payload*)radio.DATA;
    r.sender = radio.SENDERID;
    r.send2 = radio.TARGETID;
    r.rssi = rssi();
    datalen = radio.DATALEN;
    if (radio.ACKRequested())
    {
      radio.sendACK();
    }
    printTheStuff();
  }
}

void printTheStuff()
{
  hexprint(self_id);
  hexprint(r.sender);
  hexprint(r.send2);
  hexprint(r.rssi);
  for (int i = 0; i < datalen, i++;)
  {
    hexprint(RadioBuffer.x[i]);
  }
  Serial.println();
}

void sendTheStuff()
{
  SerialStruct s = *(SerialStruct*)(SerialBuffer);

  if (s.ack_requested)
  {
    bool success = radio.sendWithRetry(s.send2id,(const void*)(&s.buffer), SerialBufferLen-2);
    hexprint(self_id);
    hexprint(s.send2id);
    hexprint(success);
    hexprint(rssi());
    Serial.println();
  }
  else
  {
    radio.send(s.send2id,(const void*)(&s.buffer),sizeof(s.buffer));
  }
}



byte rssi()
{
  return radio.RSSI + 0x7F;
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

