package bgu.spl.net.impl.tftp;

import bgu.spl.net.api.BidiMessagingProtocol;
import bgu.spl.net.srv.ConnectionsImpl;
import java.io.FileInputStream;
import java.nio.ByteBuffer;

public class TftpProtocol implements BidiMessagingProtocol<byte[]> {

  String filesPath = "./Files";
  private int connectionId;
  private ConnectionsImpl<byte[]> connections;
  boolean shouldTerminate = false;
  boolean loggedIn;
  short recentOpCode;

  @Override
  public void start(
    int connectionIdVal,
    ConnectionsImpl<byte[]> connectionsVal
  ) {
    this.connectionId = connectionIdVal;
    this.connections = connectionsVal;
    loggedIn = false;
    recentOpCode = 0;
  }

  @Override
  public void process(byte[] message) {
    short opCode = (short) (
      ((short) message[0] & 0xFF) << 8 | (short) (message[1] & 0xFF)
    );
    if (opCode == 7) {
      if (loggedIn) {
        //retrurn Error user is already loggedIn
      } else {
        String userName = new String(message, 2, message.length - 1);
        if (connections.checkIfLoggedin(userName) != null) {
          // send error response to user that some other user is logged in on this username
        } else {
          connections.logIn(userName, connectionId);
          // send Ack to the client with block 0
        }
      }
    }
    if (opCode == 1) {
      if (!loggedIn) {
        // send error pack with user isnt logged in
      }
      String fileName = new String(message, 2, message.length - 1);
      connections.lock.readLock();
      // check if filename is in the Files directory if not send error pack else start sending data pack with the file content
      // save opCode for acks
      // read the file frrom the file system and create a queue with all data separated to 512bytes

    }

    if (opCode == 2) {
      if (!loggedIn) {
        //send error pack with user inst logged in
      }
      String fileName = new String(message, 2, message.length - 1);
      // checks if the file exsists in the file system if so return error else send ack to client and wait for data
      //save opCode for acks

    }
    if (opCode == 3) {
      //read the file from the client if the length of the data is less than 512 so this is the last chuck of data
      // get the fos and write the bytes if message is less than 512 then we close the channel
    }
  }

  @Override
  public boolean shouldTerminate() {
    return shouldTerminate;
  }
}
