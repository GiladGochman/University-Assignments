package bgu.spl.net.impl.tftp;

import bgu.spl.net.srv.BlockingConnectionHandler;
import bgu.spl.net.srv.ConnectionHandler;
import bgu.spl.net.srv.Connections;
import java.util.concurrent.ConcurrentHashMap;

public class ConnectionsTftp implements Connections<byte[]> {

  private ConcurrentHashMap<Integer, BlockingConnectionHandler<byte[]>> map;

  public ConnectionsTftp() {
    map = new ConcurrentHashMap<Integer, BlockingConnectionHandler<byte[]>>();
  }

  public void connect(
    int connectionId,
    BlockingConnectionHandler<byte[]> handler
  ) {
    map.put(connectionId, handler);
  }

  public boolean send(int connectionId, byte[] msg) {
    BlockingConnectionHandler<byte[]> b = map.get(connectionId);
    if (b == null) return false;
    b.send(msg);
    return true;
  }

  public void disconnect(int connectionId) {
    map.remove(connectionId);
  }
}
