package bgu.spl.net.impl.tftp;

import java.util.Arrays;

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
          bytesToReturn=Arrays.copyOfRange(bytes, 0, len);
          bytes=new byte[1 << 10];
          len=0;
          return bytesToReturn;
        }
      }
    } else { // finnished reading opcode
      if (
        opCode == 1 || //Read request
        opCode == 2 || //Write request
        opCode == 7 || //Login request
        opCode == 8 //Delete file request
      ) {
        if (nextByte == 0) {
          bytesToReturn=Arrays.copyOfRange(bytes, 0, len);
          bytes=new byte[1 << 10];
          len=0;
          return bytesToReturn;
        }
        bytes[len] = nextByte;
        len++;
      }
      if (opCode == 4) {
        bytes[len] = nextByte;
        len++;
        if (len == 4) {
          bytesToReturn=Arrays.copyOfRange(bytes, 0, len);
          bytes=new byte[1 << 10];
          len=0;
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
            bytesToReturn=Arrays.copyOfRange(bytes, 0, len);
            bytes=new byte[1 << 10];
            len=0;
            return bytesToReturn;
          }
        }
      }
      if (opCode == 9) { // BCAST
        if (nextByte == 0 && len != 2) {
          bytesToReturn=Arrays.copyOfRange(bytes, 0, len);
          bytes=new byte[1 << 10];
          len=0;
          return bytesToReturn;
        }
        bytes[len] = nextByte;
        len++;
      }
      if(opCode ==5){
        if(len<4){
          bytes[len]=nextByte;
          len++;
        }else{
          if(nextByte == 0){
          bytesToReturn=Arrays.copyOfRange(bytes, 0, len);
          bytes=new byte[1 << 10];
          len=0;
          return bytesToReturn;
          }
          bytes[len] = nextByte;
           len++;
        }

      }
    }

    return null;
  }

  @Override
  public byte[] encode(byte[] message) {
    return message;
  }
}
