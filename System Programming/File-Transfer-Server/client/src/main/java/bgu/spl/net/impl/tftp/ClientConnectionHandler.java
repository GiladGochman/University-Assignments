package bgu.spl.net.impl.tftp;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.util.concurrent.ConcurrentLinkedQueue;

public class ClientConnectionHandler {

  public boolean shouldTerminate;
  public boolean waitingForResponse;
  public short recentRequestOpCode;
  public String workingFileName;
  public int writeCounter;
  public ConcurrentLinkedQueue<byte[]> ansQueue = new ConcurrentLinkedQueue<>();
  public ConcurrentLinkedQueue<byte[]> sendQueue = new ConcurrentLinkedQueue<>();
  TftpEncoderDecoder encdec;
  BufferedInputStream in;
  BufferedOutputStream out;

  public ClientConnectionHandler(
    BufferedInputStream inBuff,
    BufferedOutputStream outBuff
  ) {
    shouldTerminate = false;
    waitingForResponse = false;
    recentRequestOpCode = 0;
    workingFileName = "";
    writeCounter = 0;
    in = inBuff;
    out = outBuff;
    encdec = new TftpEncoderDecoder();
  }
}
