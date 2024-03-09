package bgu.spl.net.impl.tftp;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class main {

  public static void main(String[] args) {
    // connections.lock.readLock().lock();
    List<String> fileNamesList = getFileNames();
    StringBuilder sb = new StringBuilder();
    for (String fileName : fileNamesList) {
      sb.append(fileName).append("\0"); // Use null byte as separator
    }
    // Convert the concatenated string to a byte array
    byte[] byteArray = sb.toString().getBytes();
    // for (int i = 0; i < byteArray.length; i++) {
    //   System.out.println(byteArray[i]);
    // }
    List<byte[]> splitIntoChunks = splitByteArray(byteArray);
    for (byte[] x : splitIntoChunks) {
      for (int i = 0; i < x.length; i++) {
        System.out.println(x[i]);
      }
    }
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

  // // functions that sends Errors to users
  // public void sendError(short opCode, String message) {
  //   byte[] opCodeByteArray = new byte[] {
  //     (byte) (opCode >> 8),
  //     (byte) (opCode & 0xff),
  //   };
  //   byte[] errorStart = concatenateArrays(errorCode, opCodeByteArray);
  //   byte[] errorMsg = new String(message + new String(new byte[] { 0 }))
  //     .getBytes();
  //   connections.send(connectionId, concatenateArrays(errorStart, errorMsg));
  // }

  public static List<String> getFileNames() {
    List<String> fileNamesList = new ArrayList<>();
    String rootDirectory = System.getProperty("user.dir");
    // System.out.println(rootDirectory);
    String pathname =
      rootDirectory + File.separator + "server" + File.separator + "Files";
    System.out.println(pathname);
    File folder = new File(pathname);

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

  public static List<byte[]> splitByteArray(byte[] byteArray) {
    int chunkSize = 12;
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
