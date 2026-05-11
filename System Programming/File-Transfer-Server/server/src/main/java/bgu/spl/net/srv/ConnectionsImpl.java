package bgu.spl.net.srv;

import java.util.Iterator;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class ConnectionsImpl<T> implements Connections<T> {

  ConcurrentHashMap<Integer, BlockingConnectionHandler<T>> map;
  ConcurrentHashMap<String, Integer> loggedInList;

  public ReentrantReadWriteLock lock;

  public ConnectionsImpl() {
    map = new ConcurrentHashMap<>();
    loggedInList = new ConcurrentHashMap<>();

    lock = new ReentrantReadWriteLock();
  }

  @Override
  public void connect(int connectionId, BlockingConnectionHandler<T> handler) {
    if (map.get(connectionId) != null) return;
    map.put(connectionId, handler);
  }

  @Override
  public boolean send(int connectionId, T msg) {
    if (map.get(connectionId) == null) return false;
    map.get(connectionId).send(msg);
    return true;
  }

  @Override
  public void disconnect(int connectionId) {
    if (map.get(connectionId) != null) map.remove(connectionId);
  }

  public Integer checkIfLoggedin(String userName) {
    synchronized (loggedInList) {
      return loggedInList.get(userName);
    }
  }

  public void logIn(String userName, int connectionId) {
    synchronized (loggedInList) {
      loggedInList.put(userName, connectionId);
    }
  }

  public void logOut(String userName) {
    synchronized (loggedInList) {
      loggedInList.remove(userName);
    }
  }

  public BlockingConnectionHandler<T> getConnectionHandler(int connectionId) {
    return map.get(connectionId);
  }

  public void bCast(int connectionId, T msg) {
    synchronized (loggedInList) {
      Iterator<Integer> connectionsIt = loggedInList.values().iterator();
      while (connectionsIt.hasNext()) {
        int conId = connectionsIt.next();
        if (conId != connectionId) {
          map.get(conId).send(msg);
        }
      }
    }
  }
}
