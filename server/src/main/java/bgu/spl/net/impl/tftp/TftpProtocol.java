package bgu.spl.net.impl.tftp;

import bgu.spl.net.api.BidiMessagingProtocol;
import bgu.spl.net.srv.BlockingConnectionHandler;
import bgu.spl.net.srv.ConnectionsImpl;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.util.concurrent.ConcurrentLinkedQueue;

public class TftpProtocol implements BidiMessagingProtocol<byte[]> {

  String filesPath = "./Files";
  private int connectionId;
  private ConnectionsImpl<byte[]> connections;
  boolean shouldTerminate = false;
  boolean loggedIn;
  byte[] errorCode = { 0, 5 };
  short recentOpCode = 0;
  ByteBuffer data;
  short readCounter = 1;
  short writeCounter = 1;
  ConcurrentLinkedQueue<byte[]> fileReadQueue;

  @Override
  public void start(
    int connectionIdVal,
    ConnectionsImpl<byte[]> connectionsVal
  ) {
    this.connectionId = connectionIdVal;
    this.connections = connectionsVal;
    loggedIn = false;
    recentOpCode = 0;
    fileReadQueue = new ConcurrentLinkedQueue<>();
  }

  @Override
  public void process(byte[] message) {
    short opCode = (short) (
      ((short) message[0] & 0xFF) << 8 | (short) (message[1] & 0xFF)
    );
    if (opCode == 7) {
      if (loggedIn) {
        sendError((short) 7, "User is logged in already");
      } else {
        String userName = new String(message, 2, message.length - 1);
        if (connections.checkIfLoggedin(userName) != null) {
          sendError((short) 0, "The username u gave is already loggedIn");
        } else {
          connections.logIn(userName, connectionId);
          BlockingConnectionHandler<byte[]> myConnectionHandler = connections.getConnectionHandler(
            connectionId
          );
          byte[] ack = { 0, 4, 0, 0 };
          myConnectionHandler.send(ack);
        }
      }
    }
    if (opCode == 1) {
      if (!loggedIn) {
        sendError((short) 6, "User isn't logged in");
      }
      String fileName = new String(message, 2, message.length - 1);
      connections.lock.readLock();
      File file = new File(filesPath, fileName);
      if (!file.exists()) {
        // sends error
      } else {
        String filePath = filesPath + fileName;
        try {
          FileInputStream fis = new FileInputStream(filePath);
          FileChannel channel = fis.getChannel();
          ByteBuffer byteBuffer = ByteBuffer.allocate(512);

          // Read the file in chunks
          int bytesRead;
          while ((bytesRead = channel.read(byteBuffer)) != -1) {
            // Rewind the buffer before reading
            byteBuffer.rewind();

            // Read bytes from the buffer
            byte[] chunk = new byte[bytesRead];
            byteBuffer.get(chunk);
            int[] blockNum = { readCounter / 256, readCounter % 256 };
            byte[] start = { 0, 3, (byte) blockNum[0], (byte) blockNum[1] };
            readCounter++;
            // Process the chunk as needed (e.g., print or save to another file)
            fileReadQueue.add(concatenateArrays(start, chunk));
            // Clear the buffer for the next iteration
            byteBuffer.clear();
          }
          readCounter = 1;
          // Close the FileInputStream
          fis.close();
        } catch (IOException e) {
          e.printStackTrace();
          //Error reading file
          sendError((short) 0, "Problem reading the file");
        }
        BlockingConnectionHandler<byte[]> myConnectionHandler = connections.getConnectionHandler(
          connectionId
        );
        recentOpCode = opCode;
        myConnectionHandler.send(fileReadQueue.remove());
      }
    }

    if (opCode == 2) {
      if (!loggedIn) {
        sendError((short) 6, "User isn't logged in");
      }
      String fileName = new String(message, 2, message.length - 1);
      connections.lock.readLock().lock();
      File file = new File(filesPath, fileName);
      if (file.exists()) {
        connections.lock.readLock().unlock();
        sendError((short) (5), "File is already Exsists");
      } else {
        try {
          connections.lock.readLock().unlock();
          connections.lock.writeLock().lock();
          // Create the file
          boolean created = file.createNewFile();

          if (created) {
            System.out.println("File created successfully.");
          } else {
            connections.lock.writeLock().unlock();
            sendError((short) 0, "problems with creating the file");
          }
        } catch (IOException e) {
          connections.lock.writeLock().unlock();
          sendError((short) 0, "problems with creating the file");
        }
        BlockingConnectionHandler<byte[]> myConnectionHandler = connections.getConnectionHandler(
          connectionId
        );
        byte[] ack = { 0, 4, 0, 0 };
        recentOpCode = 2;
        myConnectionHandler.send(ack);
      }
    }
    if (opCode == 3) {}
  }

  @Override
  public boolean shouldTerminate() {
    return shouldTerminate;
  }

  public static byte[] concatenateArrays(byte[] array1, byte[] array2) {
    // Calculate the size of the concatenated array
    int totalLength = array1.length + array2.length;

    // Create a new byte array to hold the concatenated data
    byte[] result = new byte[totalLength];

    // Copy the contents of the first array into the result array
    System.arraycopy(array1, 0, result, 0, array1.length);

    // Copy the contents of the second array into the result array
    System.arraycopy(array2, 0, result, array1.length, array2.length);

    return result;
  }

  // functions that sends Errors to users
  public void sendError(short opCode, String message) {
    BlockingConnectionHandler<byte[]> myConnectionHandler = connections.getConnectionHandler(
      connectionId
    );
    byte[] opCodeByteArray = new byte[] {
      (byte) (opCode >> 8),
      (byte) (opCode & 0xff),
    };
    byte[] errorStart = concatenateArrays(errorCode, opCodeByteArray);
    byte[] errorMsg = new String(message + new String(new byte[] { 0 }))
      .getBytes();
    myConnectionHandler.send(concatenateArrays(errorStart, errorMsg));
  }
}
