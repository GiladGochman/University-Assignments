package bgu.spl.net.srv;

import bgu.spl.net.api.BidiMessagingProtocol;
import bgu.spl.net.api.MessageEncoderDecoder;
import bgu.spl.net.api.MessagingProtocol;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.function.Supplier;

public abstract class BaseServer<T> implements Server<T> {

  private final int port;
  private final Supplier<BidiMessagingProtocol<T>> protocolFactory;
  private final Supplier<MessageEncoderDecoder<T>> encdecFactory;
  private ConnectionsImpl<T> connections;
  int counter = 0;
  private ServerSocket sock;

  public BaseServer(
    int port,
    Supplier<BidiMessagingProtocol<T>> protocolFactory,
    Supplier<MessageEncoderDecoder<T>> encdecFactory,
    ConnectionsImpl<T> connections
  ) {
    this.port = port;
    this.protocolFactory = protocolFactory;
    this.encdecFactory = encdecFactory;
    this.connections = connections;
    this.sock = null;
  }

  @Override
  public void serve() {
    try (ServerSocket serverSock = new ServerSocket(port)) {
      System.out.println("Server started");

      this.sock = serverSock; //just to be able to close

      while (!Thread.currentThread().isInterrupted()) {
        Socket clientSock = serverSock.accept();

        BlockingConnectionHandler<T> handler = new BlockingConnectionHandler<>(
          clientSock,
          encdecFactory.get(),
          protocolFactory.get(),
          counter
        );
        connections.connect(counter, handler);
        handler.start(counter, connections);
        counter++;
        execute(handler);
      }
    } catch (IOException ex) {}

    System.out.println("server closed!!!");
    try {
      close();
    } catch (IOException e) {}
  }

  @Override
  public void close() throws IOException {
    if (sock != null) sock.close();
  }

  protected abstract void execute(BlockingConnectionHandler<T> handler);
}
