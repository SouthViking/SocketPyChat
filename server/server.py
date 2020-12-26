import sys
import os
import pickle
import socket
import colorama
import threading

sys.path.append('..')

from utils.screen_cleaner import screen_cleaner
from utils.log_print import log_print

colorama.init()  # Inicialización de colores para CLI.

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
                    conn.close()
                    break

                msg = 'Recibido desde cliente (' + str(client_address[0]) + ' , ' + str(client_address[1]) + '): ' + str(data)
                log_print(msg, 3)

                # Se envía a los demás clientes conectados
                self.send_all(conn, data)
        
        except Exception as error:
            msg = 'Se ha producido el siguiente error en la conexión con el cliente (' + str(client_address[0]) + ' , ' + str(client_address[1]) +'):'
            log_print(msg, 0)
            log_print(str(error), 0)

            # Se cierra la conexión y se elimina de la lista de conexiones del servidor.
            self.connections.remove(conn)
            conn.close()
            print(colorama.Fore.YELLOW + '* Conexiones actuales: ' + str(self.connections) + colorama.Style.RESET_ALL)
            
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
                print(colorama.Fore.YELLOW + '* Conexiones actuales: ' + str(self.connections) + colorama.Style.RESET_ALL)

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
