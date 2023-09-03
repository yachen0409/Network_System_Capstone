import socket


def client_program():

    host = "10.0.2.8"  # as both code is running on same pc
    port = 8888  # socket server port number
    SOURCE_PORT = 7777
    client_socket = socket.socket()  # instantiate
    client_socket.bind(('10.0.2.15', SOURCE_PORT))
    client_socket.connect((host, port))  # connect to the server
    data = client_socket.recv(1024).decode()  # receive response
    print('Received from server: ' + data)  # show in terminal

    message = input(" -> ")  # again take input


    while True:
        
        client_socket.send(message.encode())  # send message
        data = client_socket.recv(1024).decode()  # receive response
        print('Received from server: ' + data)  # show in terminal

        message = input(" -> ")  # again take input

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()
