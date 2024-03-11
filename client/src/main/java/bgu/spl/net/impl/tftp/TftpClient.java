package bgu.spl.net.impl.tftp;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;

public class TftpClient {

  //TODO: implement the main logic of the client, when using a thread per client the main logic goes here
  public static void main(String[] args) throws IOException {
    if (args.length == 0) {
      args = new String[] { "localhost", "hello" };
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
        BufferedReader keyBoardInput = new BufferedReader(
          new InputStreamReader(System.in)
        );
        String message;
        try {
          while (
            (message = keyBoardInput.readLine()) != null &
            !clientConnection.shouldTerminate
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
              if (indexOfSpace == -1) {
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
      if (blockNum != clientC.ansQueue.size() - 1) {
        byte[] error = sendError((short) 0, "got the wrong block");
        try {
          clientC.out.write(error);
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
            fos.close();
          } catch (IOException e) {
            e.printStackTrace();
            clientC.ansQueue.clear();
            clientC.recentRequestOpCode = 0;
            clientC.waitingForResponse = false;
          }
        } else if (clientC.recentRequestOpCode == 6) {
          List<String> fileNames = getAllFileNames(clientC.ansQueue);
          for (String fileName : fileNames) {
            System.out.println(fileName);
          }
        }
      }
      byte[] ack = { 0, 4, ans[4], ans[5] };
      try {
        clientC.out.write((clientC.encdec.encode(ack)));
      } catch (IOException e) {
        e.printStackTrace();
      }
    }
    if (opCode == 4) {
      if (
        clientC.recentRequestOpCode != 2 | clientC.recentRequestOpCode != 10
      ) {
        System.out.println("< ACK  0");
        clientC.recentRequestOpCode = 0;
        clientC.waitingForResponse = false;
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
        if (!clientC.sendQueue.isEmpty()) {
          try {
            clientC.out.write(clientC.encdec.encode(clientC.sendQueue.poll()));
          } catch (IOException e) {
            e.printStackTrace();
          }
          if (clientC.sendQueue.isEmpty()) {
            clientC.waitingForResponse = false;
            clientC.recentRequestOpCode = 0;
          }
        }
      }
      if (clientC.recentRequestOpCode == 10) {
        clientC.shouldTerminate = true;
        clientC.waitingForResponse = false;
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

    // Iterate over each byte array in the queue
    while (!bytesQueue.isEmpty()) {
      byte[] byteArray = bytesQueue.poll();
      if (byteArray == null || byteArray.length < 6) {
        // Invalid byte array, continue to the next one
        continue;
      }

      // Extract data length number from the byte array

      int dataLength = (byteArray[2] << 8) | (byteArray[3] & 0xFF);

      // Check if data length is valid
      if (dataLength == 0) {
        // If data length is 0, skip processing this byte array
        continue;
      }

      // Check if data length is valid
      if (byteArray.length < 6 + dataLength) {
        // Invalid data length, continue to the next byte array
        continue;
      }

      // Extract data from the byte array
      String data = new String(byteArray, 6, dataLength);

      // Split data into file names using nullByte ("\0")
      String[] fileNamesInData = data.split("\0");

      // Add each file name to the list
      for (String fileName : fileNamesInData) {
        if (!fileName.isEmpty()) {
          fileNames.add(fileName);
        }
      }
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
      byte[] fileName = (cmd[1] + "\0").getBytes();
      try {
        clientC.recentRequestOpCode = 7;
        clientC.waitingForResponse = true;
        clientC.out.write(concatenateArrays(start, fileName));
      } catch (IOException e) {
        clientC.recentRequestOpCode = 0;
        clientC.waitingForResponse = false;
        e.printStackTrace();
      }
    }
    if (cmd[0].equals("RRQ")) {}
    if (cmd[0].equals("WRQ")) {}
    if (cmd[0].equals("DELRQ")) {}
    if (cmd[0].equals("DIRQ")) {}
    if (cmd[0].equals("DISC")) {}
  }

  public static boolean checkIfContainsNullByte(byte[] bytes) {
    for (byte b : bytes) {
      if (b == 0) return true;
    }
    return false;
  }
}
