# VITS-TCP_server

## TCP server:

A simple process that runs on a machine and 'listens' to a specific port. Any client wanting to communicate with the server must connect to the server's port and establish a connection.

1.  Create a socket object.
2.  Bind the socket to the current machine on a specific port.
3.  Listen for connections made to the socket.
4.  Accept a connection.
5.  Send/Receive data.
6.  Close the connection.

*Note:* The server can handle multiple clients simultaneously by creating a new thread for each client.

## Threaded TCP server:

Essentially, a TCP server capable of handling multiple clients concurrently.

The server creates a new thread for each client connecting to it. 

A pool of threads is utilized to limit the number of threads that can be created and to reuse threads that are no longer in use. Using a pool of threads is more efficient than creating a new thread for each client, as creating a new thread is a heavy operation.