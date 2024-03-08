package bgu.spl.net.srv;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class ConnectionsImpl<T> implements Connections<T> {

  ConcurrentHashMap<Integer, BlockingConnectionHandler<T>> map;
  ConcurrentHashMap<String, Integer> loggedInList;
  ReentrantReadWriteLock lock;

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
    return loggedInList.get(userName);
  }

  public void logIn(String userName, int connectionId) {
    loggedInList.put(userName, connectionId);
  }
}
