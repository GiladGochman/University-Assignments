package bgu.spl.net.impl.tftp;

import bgu.spl.net.api.MessageEncoderDecoder;

public class TftpEncoderDecoder implements MessageEncoderDecoder<byte[]> {

  private byte[] bytes = new byte[1 << 10]; //start with 1k
  private int len = 0;
  private short opCode;

  @Override
  public byte[] decodeNextByte(byte nextByte) {
    byte[] bytesToReturn;
    if (len < 2) { // Reading the opcode:
      bytes[len] = nextByte;
      len++;
      if (len == 2) { // Save the opcode as short:
        opCode =
          (short) (((short) bytes[0] & 0xff) << 8 | (short) (bytes[1] & 0xff));
          System.out.println(opCode);
        if(opCode==6 || opCode == 10){
          len=0;
          bytesToReturn=bytes;
          bytes=new byte[1 << 10];
          return bytesToReturn;
        }
      }
    } else { // finnished reading opcode
      if (
        opCode == 1 || //Read request
        opCode == 2 || //Write request
        opCode == 5 || //Error
        opCode == 7 || //Login request
        opCode == 8 //Delete file request
      ) {
        if (nextByte == 0) {
          len = 0;
          bytesToReturn=bytes;
          bytes=new byte[1 << 10];
          return bytesToReturn;
        }
        bytes[len] = nextByte;
        len++;
      }
      if (opCode == 4) {
        bytes[len] = nextByte;
        len++;
        if (len == 4) {
          len = 0;
          bytesToReturn=bytes;
          bytes=new byte[1 << 10];
          return bytesToReturn;
        }
      }
      if (opCode == 3) { // Data
        bytes[len] = nextByte;
        len++;

        if (len >= 6) {
          short packetSize = (short) (
            ((short) bytes[2]) << 8 | (short) (bytes[3] & 0xff)
          );
          if (len == 6 + packetSize) {
            len = 0;
            bytesToReturn=bytes;
          bytes=new byte[1 << 10];
          return bytesToReturn;
          }
        }
      }
      if (opCode == 9) { // BCAST
        if (nextByte == 0 && len != 2) {
          len = 0;
          bytesToReturn=bytes;
          bytes=new byte[1 << 10];
          return bytesToReturn;
        }
        bytes[len] = nextByte;
        len++;
      }
    }

    return null;
  }

  @Override
  public byte[] encode(byte[] message) {
    return message;
  }
}
