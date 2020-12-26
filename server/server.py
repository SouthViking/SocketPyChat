import sys
import os
import pickle
import socket
import colorama
import threading
from datetime import datetime

sys.path.append('..')

from utils.screen_cleaner import screen_cleaner
from utils.log_print import log_print

colorama.init()  # Inicialización de colores para CLI.

class ClientInfo:
    def __init__(self, from_host, from_port, username = None):
        self.from_host = from_host
        self.from_port = from_port
        self.username = username

class Server:
    
    def __init__(self, host, port):
        # Se intenta realizar la conexión según el host y puerto señalado.
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((host, int(port)))
            self.sock.listen(5)

            self.host = host
            self.port = port
            self.connections = [] # Lista de conexiones de clientes.
            self.clients = {} # Diccionario para almacenamiento de información de usuarios.

            # Se inicia el proceso principal del servidor.
            log_print('Servidor inicializado correctamente.', 2)
            self.run()

        except Exception as error:
            log_print(
                'Se ha producido el siguiente error al inicializar el servidor:', 0)
            log_print(str(error), 0)
            return
    
    # Método para control de comunicación con cada uno de los clientes.
    def handler(self, conn, client_address):
        try:
            while True:
                data = conn.recv(4096)

                if not data:
                    self.connections.remove(conn)
                    del self.clients[conn]
                    conn.close()
                    break

                # Se descompone la tupla recibida entre datos y código de transacción
                recv_data = pickle.loads(data)
                tx_code = recv_data[0]

                log_print('[!] Se ha recibido una nueva transacción.', 3)
                log_print('Código de transacción: ' + str(tx_code) + ' || Recibido desde cliente: (' +
                          str(client_address[0]) + ' , ' + str(client_address[1]) + ').', 3)

                # Se verifica la transacción según el código recibido.

                if tx_code == 'CLIENT_MSG': # Envío de mensaje de chat hacia los demás usuarios.

                    log_print('Mensaje recibido: ' + str(recv_data[1]), 3)

                    # Se genera el objeto a enviar, con el mensaje, datetime y nombre del usuario emisor.
                    msg_object = {}
                    msg_object['incoming_msg'] = recv_data[1]
                    msg_object['sent_at'] = str(
                        datetime.now().replace(microsecond=0))
                    
                    if conn in self.clients.keys():
                        msg_object['sender_username'] = self.clients[conn].username if self.clients[conn].username else '???'
                    
                    else:
                        msg_object['sender_username'] = '???'

                    self.send_all(conn, pickle.dumps(
                        (tx_code, msg_object)))
                
                elif tx_code == 'USERNAME_REG': # Registro de nombre de usuario en el servidor.

                    self.clients[conn].username = recv_data[1]
                    log_print('Nombre de usuario registrado: ' + str(recv_data[1]), 3)
                    
                    # Se notifica a los clientes el ingreso del nuevo usuario al chat.
                    self.send_all(conn, pickle.dumps(
                        ('CLIENT_JOIN', recv_data[1])))
        
        except Exception as error:
            msg = 'Se ha producido el siguiente error en la conexión con el cliente (' + str(client_address[0]) + ' , ' + str(client_address[1]) +'):'
            log_print(msg, 0)
            log_print(str(error), 0)

            # Se notifica la salida del cliente del chat.
            if conn in self.clients.keys():
                self.send_all(conn, pickle.dumps(
                    ('CLIENT_EXIT', self.clients[conn].username)))

            # Se cierra la conexión y se elimina de la lista de conexiones del servidor.
            self.connections.remove(conn)
            del self.clients[conn]
            conn.close()
            log_print('* Conexiones actuales: ' + str(self.connections), 1)
            
            return
    
    # Método para enviar mensaje a todos los clientes conectados
    def send_all(self, conn, data):
        for connection in self.connections:
            if connection != conn:
                # En caso de que la conexión no corresponda a la del emisor, se envía al cliente correspondiente.
                connection.send(data)

    # Proceso principal de ejecución del servidor
    def run(self):
        log_print('Servidor en ejecución.', 2)
        while True:
            try:
                # Se obtienen conexiones de clientes.
                connection, client_address = self.sock.accept()
                log_print('Se ha establecido una conexión con un nuevo cliente (' + str(client_address[0]) + ' , ' +str(client_address[1]) +').', 3)

                # Se agrega la conexión a la lista de conexiones del servidor.
                self.connections.append(connection)
                self.clients[connection] = ClientInfo(str(client_address[0]), str(client_address[1]))
                log_print('* Conexiones actuales: ' + str(self.connections), 1)

                # Se crea un nuevo thread para la atención de la conexión del nuevo cliente.
                client_thread = threading.Thread(target = self.handler, args = (connection, client_address))
                client_thread.daemon = True
                client_thread.start()


            except KeyboardInterrupt:
                log_print('Servidor detenido manualmente.', 1)
                break


if __name__ == '__main__':
    screen_cleaner()
    server = Server('127.0.0.1', 3000)
