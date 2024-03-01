# File-Transfer-Server
SPL Assignment 3 by Gilad Gochman and Clil Argas

Testing: /n
○ Server: from server folder/n
    ```
mvn compile
mvn exec:java -Dexec.mainClass="bgu.spl.net.impl.tftp.TftpServer" -Dexec.args="<port>"
    ```
○ Client: from client folder/n
    ```
 mvn compile
 mvn exec:java -Dexec.mainClass="bgu.spl.net.impl.stomp.tftp.TftpClient" -Dexec.args="<ip> <port>"
    ```

