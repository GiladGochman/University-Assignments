# File-Transfer-Server
SPL Assignment 3 by Gilad Gochman and Clil Argas

Testing:  
○ Server: from server folder  
    ```
mvn compile  
mvn exec:java -Dexec.mainClass="bgu.spl.net.impl.tftp.TftpServer" -Dexec.args="<port>"  
    ```
○ Client: from client folder  
    ```
 mvn compile  
 mvn exec:java -Dexec.mainClass="bgu.spl.net.impl.stomp.tftp.TftpClient" -Dexec.args="<ip> <port>"
    ```

