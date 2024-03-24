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

## Building Docker

```sh
// build docker image
docker build -t vits .

// run container, specify your port you wish to run with
docker run -dit --gpus all -v $PWD/api:/api -p 9999:9999 --name vits vits python3 ./server.py --port 9999
docker run -dit --gpus all -v $PWD/api:/api -p 9998:9998 --name vits_kaiwater vits python3 ./server.py --port 9998
docker run -dit --gpus all -v $PWD/api:/api -p 9997:9997 --name vits_politics vits python3 ./server.py --port 9997
```

## Restart Docker
因為有多隻 API run on 同一個 image, 重啟可以下下面的指令
```sh
docker restart $(docker ps -aqf "name=vits*")
```

## API 使用情況
`9999` for web, 憂鬱症
`9998` for app
`9997` for politics