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
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;

public class TftpProtocol implements BidiMessagingProtocol<byte[]> {

  String filesPath = System.getProperty("user.dir") + "/" + "Files";
  String connectionName = "None";
  private int connectionId;
  private ConnectionsImpl<byte[]> connections;
  boolean shouldTerminate = false;
  boolean loggedIn;
  byte[] errorCode = { 0, 5 };
  String recentFileName = "";
  ByteBuffer data;
  short readCounter = 1;
  short writeCounter = 1;
  ConcurrentLinkedQueue<byte[]> readQueue;
  FileOutputStream fos;

  @Override
  public void start(
    int connectionIdVal,
    ConnectionsImpl<byte[]> connectionsVal
  ) {
    this.connectionId = connectionIdVal;
    this.connections = connectionsVal;
    loggedIn = false;

    readQueue = new ConcurrentLinkedQueue<>();
  }

  @Override
  public void process(byte[] message) {
    short opCode = (short) (
      ((short) message[0] & 0xff) << 8 | (short) (message[1] & 0xff)
    );
    if (opCode == 1) { // RRQ client wants to read a file
      if (!loggedIn) {
        sendError((short) 6, "User isn't logged in");
        return;
      }
      String fileName = new String(message, 2, message.length - 2);
      connections.lock.readLock().lock();
      String filePath = filesPath + File.separator + fileName;
      File file = new File(filePath);
      if (!file.exists()) {
        connections.lock.readLock().unlock();
        sendError((short) 1, "File not found");
      } else {
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
            // Calculating the BlockNumber to bytes
            byte[] blockNum = new byte[] {
              ((byte) (readCounter >> 8)),
              ((byte) (readCounter & 0xff)),
            };
            // Calculating the packetSize to bytes
            byte[] packetSize = new byte[] {
              ((byte) (bytesRead >> 8)),
              (byte) (bytesRead & 0xff),
            };
            //creating the start of the DATA Packet
            byte[] start = {
              0,
              3,
              packetSize[0],
              packetSize[1],
              blockNum[0],
              blockNum[1],
            };
            //increasing the block counter
            readCounter++;
            // Process the chunk as needed (e.g., print or save to another file)
            readQueue.add(concatenateArrays(start, chunk));
            // Clear the buffer for the next iteration
            byteBuffer.clear();
          }
          //reseting the readCounter for comparing blocks
          readCounter = 1;
          // Close the FileInputStream
          fis.close();
        } catch (IOException e) {
          e.printStackTrace();
          //Error reading file
          sendError((short) 0, "Problem reading the file");
          return;
        }
        if(readQueue.isEmpty()){
          byte[] start = {0, 3, 0, 0, 0, 1};
          readQueue.add(start);
        }
        // send the client first package
        connections.send(connectionId, readQueue.remove());
      }
    }

    if (opCode == 2) { // WRQ request client wants to upload a file
      if (!loggedIn) {
        sendError((short) 6, "User isn't logged in");
        return;
      }
      String fileName = new String(message, 2, message.length - 2);
      connections.lock.writeLock().lock();
      File file = new File(filesPath, fileName);
      if (file.exists()) {
        connections.lock.writeLock().unlock();
        sendError((short) (5), "File is already Exsists");
      } else {
        try {
          recentFileName = fileName;
          // Create the file
          boolean created = file.createNewFile();

          if (created) {
            System.out.println("File created successfully.");
          } else {
            connections.lock.writeLock().unlock();
            sendError((short) 0, "problems with creating the file");
            return;
          }
        } catch (IOException e) {
          connections.lock.writeLock().unlock();
          sendError((short) 0, "problems with creating the file");
          return;
        }

        byte[] ack = { 0, 4, 0, 0 };
        try {
          fos = new FileOutputStream(file);
        } catch (IOException e) {}

        connections.send(connectionId, ack);
      }
    }
    if (opCode == 3) { // Reciving data from client
      if (!loggedIn) {
        sendError((short) 6, "User isn't logged in");
        return;
      }
      short blockNum = (short) (
        ((short) message[4] & 0xff) << 8 | (short) (message[5] & 0xff)
      );
      short blockLength = (short) (
        ((short) message[2] & 0xff) << 8 | (short) (message[3] & 0xff)
      );
      if (blockNum != writeCounter) {
        File file = new File(filesPath, recentFileName);
        file.delete();
        connections.lock.writeLock().unlock();
        sendError((short) 0, "Got the wrong block");
      } else {
        if (blockLength > 0) {
          byte[] data = Arrays.copyOfRange(message, 6, message.length);
          try {
            fos.write(data);
          } catch (IOException e) {
            File file = new File(filesPath, recentFileName);
            file.delete();
            connections.lock.writeLock().unlock();
            sendError((short) 0, "problem with writing to the file");
          }
        }

        byte[] ack = { 0, 4, message[4], message[5] };
        writeCounter++;
        connections.send(connectionId, ack);
        if (blockLength < 512) {
          writeCounter = 1;
          byte[] bCASTStart = { 0, 9, 1 };
          String fileNameWithNullByte = recentFileName + "\0";
          connections.bCast(
            connectionId,
            concatenateArrays(bCASTStart, fileNameWithNullByte.getBytes())
          );
          connections.lock.writeLock().unlock();
        }
      }
    }
    if (opCode == 4) { // Ack from Client
      if (!loggedIn) {
        sendError((short) 6, "User isn't logged in");
        return;
      }
      short blockNum = (short) (
        ((short) message[2] & 0x00ff) << 8 | (short) (message[3] & 0x00ff)
      );
      if (blockNum != readCounter) {
        readQueue.clear();
        readCounter = 1;
        sendError((short) (0), "Got the wrong block");
        connections.lock.readLock().unlock();
        return;
      }

      if (readQueue.isEmpty()) {
        readCounter = 1;
        connections.lock.readLock().unlock();
        return;
      }
      connections.send(connectionId, readQueue.remove());
      readCounter++;
    }
    if (opCode == 5) {
      if (!loggedIn) {
        sendError((short) 6, "User isn't logged in");
        return;
      }
      System.out.println(message.length);
      String errorMsg = new String(message, 4, message.length - 4);
      short errorCode = (short) (
        ((short) message[2] & 0xff) << 8 | (short) (message[3] & 0xff)
      );
      System.err.println("Error " + errorCode + ": " + errorMsg);
      readQueue.clear();
      readCounter = 1;
    }
    if (opCode == 6) {
      if (!loggedIn) {
        sendError((short) 6, "User isn't logged in");
        return;
      }
      connections.lock.readLock().lock();
      List<String> fileNamesList = getFileNames();
      StringBuilder sb = new StringBuilder();
      for (String fileName : fileNamesList) {
        sb.append(fileName).append("\0"); // Use null byte as separator
      }

      // Convert the concatenated string to a byte array
      byte[] byteArray = sb.toString().getBytes();

      List<byte[]> splitIntoChunks = splitByteArray(byteArray);

      for (int i = 0; i < splitIntoChunks.size(); i++) {
        short packetSizeShort = (short) splitIntoChunks.get(i).length;
        byte[] packetSizeBytes = new byte[] {
          (byte) (packetSizeShort >> 8),
          (byte) (packetSizeShort & 0xff),
        };
        byte[] indexByte = new byte[] {
          (byte) ((short) i + 1 >> 8),
          (byte) (i + 1 & 0xff),
        };
        byte[] start = {
          0,
          3,
          packetSizeBytes[0],
          packetSizeBytes[1],
          indexByte[0],
          indexByte[1],
        };
        byte[] msg = concatenateArrays(start, splitIntoChunks.get(i));
        readQueue.add(msg);
      }
      connections.send(connectionId, readQueue.remove());
    }
    if (opCode == 7) { // client wants to logIn
      if (loggedIn) {
        sendError((short) 7, "User is logged in already");
        return;
      } else {
        String userName = new String(message, 2, message.length - 2); // getting the string from the message
        if (connections.checkIfLoggedin(userName) != null) {
          sendError((short) 0, "The username u gave is already loggedIn");
          return;
        } else {
          loggedIn = true;
          connections.logIn(userName, connectionId);
          connectionName = userName;
          byte[] ack = { 0, 4, 0, 0 };
          connections.send(connectionId, ack);
        }
      }
    }
    if (opCode == 8) {
      if (!loggedIn) {
        sendError((short) 6, "User isn't logged in");
        return;
      }
      connections.lock.writeLock().lock();
      String fileName = new String(message, 2, message.length - 2);
      File file = new File(filesPath, fileName);
      if (!file.exists()) {
        connections.lock.writeLock().unlock();
        sendError((short) 1, "File not found");
        return;
      } else {
        if (!file.delete()) {
          connections.lock.writeLock().unlock();
          sendError((short) (0), "Error deleting the file");
          return;
        }
        byte[] bCastStart = { 0, 9, 0 };
        String fileNameWithNullByte = fileName + "\0";
        byte[] ack = { 0, 4, 0, 0 };
        connections.send(connectionId, ack);
        connections.bCast(
          connectionId,
          concatenateArrays(bCastStart, fileNameWithNullByte.getBytes())
        );
        connections.lock.writeLock().unlock();
      }
    }
    if (opCode == 10) {
      if (!loggedIn) {
        sendError((short) (6), "User isn't logged in");
        return;
      }
      loggedIn = false;
      connections.logOut(connectionName);
      connectionName = "None";
      byte[] ack = { 0, 4, 0, 0 };
      connections.send(connectionId, ack);
      connections.disconnect(connectionId);
      shouldTerminate = true;
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

  public List<String> getFileNames() {
    List<String> fileNamesList = new ArrayList<>();
    File folder = new File(filesPath);

    // Check if the folder exists and is a directory
    if (folder.exists() && folder.isDirectory()) {
      // Get all files in the folder
      File[] files = folder.listFiles();
      if (files != null) {
        for (File file : files) {
          // Add file names to the list
          fileNamesList.add(file.getName());
        }
      }
    } else {
      System.out.println("Folder does not exist or is not a directory.");
    }
    if(fileNamesList.size() == 0){
      fileNamesList.add("No files in the server");
    }
    return fileNamesList;
  }

  public static List<byte[]> splitByteArray(byte[] byteArray) {
    int chunkSize = 512;
    int numChunks = (byteArray.length + chunkSize - 1) / chunkSize;
    List<byte[]> chunks = new ArrayList<>();

    for (int i = 0; i < numChunks - 1; i++) {
      int startIndex = i * chunkSize;
      int endIndex = startIndex + chunkSize;
      byte[] chunk = new byte[chunkSize];
      System.arraycopy(byteArray, startIndex, chunk, 0, chunkSize);
      chunks.add(chunk);
    }

    // Last chunk
    int lastChunkStart = (numChunks - 1) * chunkSize;
    int lastChunkSize = byteArray.length - lastChunkStart;
    byte[] lastChunk = new byte[lastChunkSize];
    System.arraycopy(byteArray, lastChunkStart, lastChunk, 0, lastChunkSize);
    chunks.add(lastChunk);

    return chunks;
  }
}
