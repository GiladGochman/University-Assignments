package bgu.spl.net.impl.tftp;

import bgu.spl.net.api.BidiMessagingProtocol;
import bgu.spl.net.srv.BlockingConnectionHandler;
import bgu.spl.net.srv.ConnectionsImpl;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.util.Arrays;
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
  FileOutputStream fos;

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
    if (opCode == 7) { // client wants to logIn
      if (loggedIn) {
        sendError((short) 7, "User is logged in already");
      } else {
        String userName = new String(message, 2, message.length - 1); // getting the string from the message
        if (connections.checkIfLoggedin(userName) != null) {
          sendError((short) 0, "The username u gave is already loggedIn");
        } else {
          connections.logIn(userName, connectionId);

          byte[] ack = { 0, 4, 0, 0 };
          connections.send(connectionId, ack);
        }
      }
    }
    if (opCode == 1) { // RRQ client wants to read a file
      if (!loggedIn) {
        sendError((short) 6, "User isn't logged in");
      }
      String fileName = new String(message, 2, message.length - 1);
      connections.lock.readLock().lock();
      File file = new File(filesPath, fileName);
      if (!file.exists()) {
        sendError((short) 1, "File not found");
      } else {
        String filePath = filesPath + "/" + fileName;
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
        connections.send(connectionId, fileReadQueue.remove());
      }
    }

    if (opCode == 2) { // WRQ request client wants to upload a file
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

        byte[] ack = { 0, 4, 0, 0 };
        try {
          fos = new FileOutputStream(file);
        } catch (IOException e) {}
        recentOpCode = 2;
        connections.send(connectionId, ack);
      }
    }
    if (opCode == 3) { // Sending data from client
      short blockNum = (short) (
        ((short) message[4] & 0xFF) << 8 | (short) (message[5] & 0xFF)
      );
      short blockLength = (short) (
        ((short) message[2] & 0xFF) << 8 | (short) (message[3] & 0xFF)
      );
      if (blockNum != readCounter) {
        connections.lock.writeLock().unlock();
        sendError((short) 0, "Got the wrong block");
      } else {
        byte[] data = Arrays.copyOfRange(message, 6, message.length);
        try {
          fos.write(data);
        } catch (IOException e) {
          connections.lock.writeLock().unlock();
          sendError((short) 0, "problem with writing to the file");
        }

        byte[] ack = { 0, 4, message[2], message[3] };
        readCounter++;
        connections.send(connectionId, ack);
        if (blockLength < 512) {
          connections.lock.writeLock().unlock();
          readCounter = 1;
          //send BCAST
        }
      }
    }
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
    byte[] opCodeByteArray = new byte[] {
      (byte) (opCode >> 8),
      (byte) (opCode & 0xff),
    };
    byte[] errorStart = concatenateArrays(errorCode, opCodeByteArray);
    byte[] errorMsg = new String(message + new String(new byte[] { 0 }))
      .getBytes();
    connections.send(connectionId, concatenateArrays(errorStart, errorMsg));
  }
}
