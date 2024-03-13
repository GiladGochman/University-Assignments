package bgu.spl.net.impl.tftp;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;

public class TftpClient {

  //TODO: implement the main logic of the client, when using a thread per client the main logic goes here
  public static void main(String[] args) throws IOException {
    if (args.length == 0) {
      args = new String[] { "localhost", "7777" };
    }
    if (args.length < 2) {
      System.out.println("you must supply two arguments: host, message");
      System.exit(1);
    }

    //BufferedReader and BufferedWriter automatically using UTF-8 encoding
    try {
      Socket sock = new Socket(args[0], Integer.valueOf(args[1]));
      BufferedInputStream in = new BufferedInputStream(sock.getInputStream());

      BufferedOutputStream out = new BufferedOutputStream(
        sock.getOutputStream()
      );
      ClientConnectionHandler clientConnection = new ClientConnectionHandler(
        in,
        out
      );

      Thread listenerThread = new Thread(() -> {
        System.out.println("start listening");
        int bytes;
        try {
          while (
            (bytes = in.read()) >= 0 && !clientConnection.shouldTerminate
          ) {
            byte[] ans = clientConnection.encdec.decodeNextByte((byte) bytes);
            if (ans != null) {
              handleAns(ans, clientConnection);
            }
          }
        } catch (IOException e) {
          e.printStackTrace();
        }
      });
      listenerThread.start();
      Thread keyBoardThread = new Thread(() -> {
        System.out.println("keyBoard started");
        BufferedReader keyBoardInput = new BufferedReader(
          new InputStreamReader(System.in)
        );
        String message;
        try {
          while (
            !clientConnection.shouldTerminate &&
            (message = keyBoardInput.readLine()) != null
          ) {
            if (clientConnection.waitingForResponse) {
              continue;
            }
            if (!isCommandValid(message)) {
              System.out.println("Invalid command");
              continue;
            } else {
              String[] cmd = { message, "" };
              int indexOfSpace = message.indexOf(' ', 0);
              if (indexOfSpace != -1) {
                cmd[0] = message.substring(0, indexOfSpace);
                cmd[1] = message.substring(indexOfSpace + 1, message.length());
              }
              handleCommand(cmd, clientConnection);
            }
          }
        } catch (IOException e) {
          e.printStackTrace();
        }
      });
      keyBoardThread.start();
      keyBoardThread.join();
      sock.close();
    } catch (IOException | InterruptedException e) {
      e.printStackTrace();
    }
  }

  public static void handleAns(byte[] ans, ClientConnectionHandler clientC) {
    short opCode = (short) (
      ((short) ans[0] & 0xff) << 8 | (short) (ans[1] & 0xff)
    );
    if (opCode == 3) {
      short blockNum = (short) (
        ((short) ans[4] & 0xff) << 8 | (short) (ans[5] & 0xff)
      );
      short blockLength = (short) (
        ((short) ans[2] & 0xff) << 8 | (short) (ans[3] & 0xff)
      );
      if (blockNum != clientC.ansQueue.size() + 1) {
        byte[] error = sendError((short) 0, "got the wrong block");
        try {
          clientC.out.write(error);
          clientC.out.flush();
        } catch (IOException e) {
          e.printStackTrace();
        }
        clientC.ansQueue.clear();
        clientC.waitingForResponse = false;
        return;
      }
      if (ans.length > 6) {
        clientC.ansQueue.add(Arrays.copyOfRange(ans, 6, ans.length));
      }
      if (blockLength < 512) {
        if (clientC.recentRequestOpCode == 1) {
          File newFile = new File(
            System.getProperty("user.dir"),
            clientC.workingFileName
          );
          if (newFile.exists()) {
            newFile.delete();
          }
          try {
            newFile.createNewFile();
            FileOutputStream fos = new FileOutputStream(newFile);
            while (!clientC.ansQueue.isEmpty()) {
              fos.write(clientC.ansQueue.remove());
            }
            clientC.recentRequestOpCode = 0;
            clientC.waitingForResponse = false;
            System.out.println("file has been written");
            fos.close();
          } catch (IOException e) {
            e.printStackTrace();
            clientC.ansQueue.clear();
            clientC.recentRequestOpCode = 0;
            clientC.waitingForResponse = false;
          }
        } else if (clientC.recentRequestOpCode == 6) {
          System.out.println(clientC.ansQueue.size());
          List<String> fileNames = getAllFileNames(clientC.ansQueue);
          for (String fileName : fileNames) {
            System.out.println(fileName);
          }
          clientC.waitingForResponse = false;
          clientC.recentRequestOpCode = 0;
          clientC.ansQueue.clear();
        }
      }
      byte[] ack = { 0, 4, ans[4], ans[5] };
      try {
        clientC.out.write((clientC.encdec.encode(ack)));
        clientC.out.flush();
      } catch (IOException e) {
        e.printStackTrace();
      }
    }
    if (opCode == 4) {
      if (
        clientC.recentRequestOpCode != 2 & clientC.recentRequestOpCode != 10
      ) {
        System.out.println("< ACK  0");
        clientC.recentRequestOpCode = 0;
        clientC.waitingForResponse = false;
        return;
      }
      if (clientC.recentRequestOpCode == 2) {
        short blockNum = (short) (
          ((short) ans[2] & 0xff) << 8 | (short) (ans[3] & 0xff)
        );
        if (clientC.writeCounter != blockNum) {
          clientC.sendQueue.clear();
          clientC.recentRequestOpCode = 0;
          clientC.waitingForResponse = false;
          return;
        }
        if (blockNum == 0) {
          String filePath =
            System.getProperty("user.dir") + "/" + clientC.workingFileName;
          try {
            FileInputStream fis = new FileInputStream(filePath);
            FileChannel channel = fis.getChannel();
            ByteBuffer byteBuffer = ByteBuffer.allocate(512);

            // Read the file in chunks
            int bytesRead;
            while ((bytesRead = channel.read(byteBuffer)) != -1) {
              // Rewind the buffer before reading
              byteBuffer.rewind();
              //increasing the block counter
              clientC.writeCounter++;
              // Read bytes from the buffer
              byte[] chunk = new byte[bytesRead];
              byteBuffer.get(chunk);
              // Calculating the BlockNumber to bytes
              byte[] blockNumForSend = new byte[] {
                ((byte) (clientC.writeCounter >> 8)),
                ((byte) (clientC.writeCounter & 0xff)),
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
                blockNumForSend[0],
                blockNumForSend[1],
              };

              // Process the chunk as needed (e.g., print or save to another file)
              clientC.sendQueue.add(concatenateArrays(start, chunk));
              // Clear the buffer for the next iteration
              byteBuffer.clear();
            }
            //reseting the readCounter for comparing blocks
            clientC.writeCounter = 1;
            // Close the FileInputStream
            fis.close();
            clientC.out.write(clientC.encdec.encode(clientC.sendQueue.poll()));
            clientC.out.flush();
          } catch (IOException e) {
            sendError((short) 0, "error reading the file");
            clientC.waitingForResponse = false;
            clientC.workingFileName = "";
            clientC.recentRequestOpCode = 0;
          }
        } else {
          if (!clientC.sendQueue.isEmpty()) {
            try {
              clientC.out.write(
                clientC.encdec.encode(clientC.sendQueue.poll())
              );
              clientC.out.flush();
              clientC.writeCounter++;
            } catch (IOException e) {
              System.out.println("Error writing the file");
              sendError((short) 0, "Error writing the file");
              clientC.sendQueue.clear();
              clientC.recentRequestOpCode = 0;
              clientC.waitingForResponse = false;

              e.printStackTrace();
            }
          }
          if (clientC.sendQueue.isEmpty()) {
            clientC.waitingForResponse = false;
            clientC.recentRequestOpCode = 0;
            System.out.println("file Sent");
          }
        }
        
      }
      if (clientC.recentRequestOpCode == 10) {
        clientC.shouldTerminate = true;
        clientC.waitingForResponse = false;
        System.out.println("< ACK 0");
      }
    }
    if (opCode == 5) {
      String errorMsg = new String(ans, 4, ans.length - 4);
      short errorCode = (short) (
        ((short) ans[2] & 0xff) << 8 | (short) (ans[3] & 0xff)
      );
      System.err.println("Error " + errorCode + ": " + errorMsg);
      clientC.ansQueue.clear();
      clientC.sendQueue.clear();
      clientC.waitingForResponse = false;
      clientC.recentRequestOpCode = 0;
    }
    if (opCode == 9) {
      String deleteOrAdded = (ans[2] == (byte) 1) ? "add" : "del";
      String fileName = new String(ans, 3, ans.length - 3);
      System.out.println("BCAST: " + deleteOrAdded + " " + fileName);
    }
  }

  public static byte[] sendError(short opCode, String message) {
    byte[] opCodeByteArray = new byte[] {
      (byte) (opCode >> 8),
      (byte) (opCode & 0xff),
    };
    byte[] errorCode = { 0, 5 };
    byte[] errorStart = concatenateArrays(errorCode, opCodeByteArray);
    byte[] errorMsg = new String(message + new String(new byte[] { 0 }))
      .getBytes();
    return concatenateArrays(errorStart, errorMsg);
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

  public static List<String> getAllFileNames(
    ConcurrentLinkedQueue<byte[]> bytesQueue
  ) {
    List<String> fileNames = new ArrayList<>();

    // Concatenate all byte arrays into one array
    int totalLength = 0;
    for (byte[] byteArray : bytesQueue) {
      if (byteArray != null) {
        totalLength += byteArray.length;
      }
    }

    byte[] combinedArray = new byte[totalLength];
    int currentIndex = 0;
    for (byte[] byteArray : bytesQueue) {
      if (byteArray != null) {
        System.arraycopy(
          byteArray,
          0,
          combinedArray,
          currentIndex,
          byteArray.length
        );
        currentIndex += byteArray.length;
      }
    }

    // Create strings from the combined array, each separated by null byte "\0"
    StringBuilder currentFileName = new StringBuilder();
    for (byte b : combinedArray) {
      if (b == 0) {
        // Found null byte, add current file name to the list and reset
        if (currentFileName.length() > 0) {
          fileNames.add(currentFileName.toString());
          currentFileName = new StringBuilder();
        }
      } else {
        // Append byte to current file name
        currentFileName.append((char) b);
      }
    }

    // Add the last file name if not added already
    if (currentFileName.length() > 0) {
      fileNames.add(currentFileName.toString());
    }

    return fileNames;
  }

  public static boolean isCommandValid(String cmd) {
    int indexOfSpace = cmd.indexOf(' ', 0);
    boolean isSplit = false;
    String firstPart = "";
    String secondPart = "";
    if (indexOfSpace != -1) {
      firstPart = cmd.substring(0, indexOfSpace);
      secondPart = cmd.substring(indexOfSpace + 1, cmd.length());
      isSplit = true;
    }
    if (!isSplit) {
      if (cmd.equals("DIRQ") || cmd.equals("DISC")) return true;
    } else {
      if (
        (
          firstPart.equals("LOGRQ") |
          firstPart.equals("RRQ") |
          firstPart.equals("WRQ") |
          firstPart.equals("DELRQ")
        ) &
        !secondPart.equals("")
      ) return true;
    }
    return false;
  }

  public static void handleCommand(
    String[] cmd,
    ClientConnectionHandler clientC
  ) {
    if (cmd[0].equals("LOGRQ")) {
      byte[] start = { 0, 7 };
      if (checkIfContainsNullByte(cmd[1].getBytes())) {
        System.out.println("name contains null byte");
        return;
      }
      byte[] userName = (cmd[1] + "\0").getBytes();
      try {
        clientC.recentRequestOpCode = 7;
        clientC.waitingForResponse = true;
        clientC.out.write(
          clientC.encdec.encode(concatenateArrays(start, userName))
        );
        clientC.out.flush();
      } catch (IOException e) {
        clientC.recentRequestOpCode = 0;
        clientC.waitingForResponse = false;
        e.printStackTrace();
      }
    }
    if (cmd[0].equals("RRQ")) {
      byte[] start = { 0, 1 };
      if (checkIfContainsNullByte(cmd[1].getBytes())) {
        System.out.println("name contains null byte");
        return;
      }

      byte[] fileName = (cmd[1] + "\0").getBytes();
      try {
        clientC.recentRequestOpCode = 1;
        clientC.workingFileName = cmd[1];
        clientC.waitingForResponse = true;
        clientC.out.write(
          clientC.encdec.encode(concatenateArrays(start, fileName))
        );
        clientC.out.flush();
      } catch (IOException e) {
        clientC.recentRequestOpCode = 0;
        clientC.workingFileName = "";
        clientC.waitingForResponse = false;
        clientC.writeCounter = 0;
        e.printStackTrace();
      }
    }
    if (cmd[0].equals("WRQ")) {
      byte[] start = { 0, 2 };
      if (checkIfContainsNullByte(cmd[1].getBytes())) {
        System.out.println("name contains null byte");
        return;
      }
      List<String> files = getFileInDir();
      if (!files.contains(cmd[1])) {
        System.out.println("File doesnt exsists in folder");
      }
      byte[] fileName = (cmd[1] + "\0").getBytes();
      try {
        clientC.recentRequestOpCode = 2;
        clientC.waitingForResponse = true;
        clientC.workingFileName = cmd[1];
        clientC.out.write(
          clientC.encdec.encode(concatenateArrays(start, fileName))
        );
        clientC.out.flush();
      } catch (IOException e) {
        clientC.recentRequestOpCode = 0;
        clientC.workingFileName = "";
        clientC.waitingForResponse = false;
        e.printStackTrace();
      }
    }
    if (cmd[0].equals("DELRQ")) {
      byte[] start = { 0, 8 };
      if (checkIfContainsNullByte(cmd[1].getBytes())) {
        System.out.println("name contains null byte");
        return;
      }
      byte[] fileName = (cmd[1] + "\0").getBytes();
      try {
        clientC.recentRequestOpCode = 8;
        clientC.waitingForResponse = true;
        clientC.out.write(
          clientC.encdec.encode(concatenateArrays(start, fileName))
        );
        clientC.out.flush();
      } catch (IOException e) {
        clientC.recentRequestOpCode = 0;
        clientC.waitingForResponse = false;
        e.printStackTrace();
      }
    }
    if (cmd[0].equals("DIRQ")) {
      byte[] code = { 0, 6 };
      try {
        clientC.out.write(clientC.encdec.encode(code));
        clientC.out.flush();
        clientC.recentRequestOpCode = 6;
        clientC.waitingForResponse = true;
      } catch (IOException e) {}
    }
    if (cmd[0].equals("DISC")) {
      byte[] code = { 0, 10 };
      try {
        clientC.out.write(clientC.encdec.encode(code));
        clientC.out.flush();
      } catch (IOException e) {}
    }
  }

  public static boolean checkIfContainsNullByte(byte[] bytes) {
    for (byte b : bytes) {
      if (b == 0) return true;
    }
    return false;
  }

  public static List<String> getFileInDir() {
    List<String> fileNamesList = new ArrayList<>();
    File folder = new File(System.getProperty("user.dir"));
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

    return fileNamesList;
  }
}
