package bgu.spl.net.impl.tftp;

import bgu.spl.net.api.BidiMessagingProtocol;
import bgu.spl.net.srv.Connections;

public class TftpProtocol implements BidiMessagingProtocol<byte[]> {

  private int connectionId;
  private Connections<byte[]> connections;

  @Override
  public void start(int connectionIdVal, Connections<byte[]> connectionsVal) {
    this.connectionId = connectionIdVal;
    this.connections = connectionsVal;
  }

  @Override
  public void process(byte[] message) {
    // TODO implement this
    throw new UnsupportedOperationException("Unimplemented method 'process'");
  }

  @Override
  public boolean shouldTerminate() {
    // TODO implement this
    throw new UnsupportedOperationException(
      "Unimplemented method 'shouldTerminate'"
    );
  }
}
