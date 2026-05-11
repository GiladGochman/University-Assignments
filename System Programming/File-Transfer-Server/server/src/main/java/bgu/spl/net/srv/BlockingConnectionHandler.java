package bgu.spl.net.srv;

import bgu.spl.net.api.BidiMessagingProtocol;
import bgu.spl.net.api.MessageEncoderDecoder;
import bgu.spl.net.api.MessagingProtocol;
import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.IOException;
import java.net.Socket;

public class BlockingConnectionHandler<T>
  implements Runnable, ConnectionHandler<T> {

  private final BidiMessagingProtocol<T> protocol;
  private final MessageEncoderDecoder<T> encdec;
  private final Socket sock;
  private BufferedInputStream in;
  public int connectionId;
  private BufferedOutputStream out;
  private volatile boolean connected = true;

  public BlockingConnectionHandler(
    Socket sock,
    MessageEncoderDecoder<T> reader,
    BidiMessagingProtocol<T> protocol,
    int connectionId
  ) {
    this.sock = sock;
    this.encdec = reader;
    this.protocol = protocol;
    this.connectionId = connectionId;
  }

  @Override
  public void run() {
    try (Socket sock = this.sock) { //just for automatic closing
      int read;

      in = new BufferedInputStream(sock.getInputStream());
      out = new BufferedOutputStream(sock.getOutputStream());

      while (
        !protocol.shouldTerminate() && connected && (read = in.read()) >= 0
      ) {
        T nextMessage = encdec.decodeNextByte((byte) read);
        if (nextMessage != null) {
          protocol.process(nextMessage);
        }
      }
      close();
    } catch (IOException ex) {
      ex.printStackTrace();
    }
  }

  @Override
  public void close() throws IOException {
    connected = false;
    sock.close();
  }

  @Override
  public synchronized void send(T msg) {
    try {
      out.write(encdec.encode(msg));
      out.flush();
    } catch (IOException e) {}
  }

  public void start(int connectionIdVal, ConnectionsImpl<T> connectionsVal) {
    protocol.start(connectionIdVal, connectionsVal);
  }
}
