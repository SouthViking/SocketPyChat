import sys
import socket
import colorama
import threading

from tkinter import *

sys.path.append('..')
from utils.log_print import log_print
from utils.screen_cleaner import screen_cleaner

colorama.init() # Inicialización de colores para CLI.

class Client:
    def __init__(self, host, port):
        # Se intenta la conexión con el servidor según el host y puerto que se especifican.
        try:
          self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          self.sock.connect((host, int(port)))
          log_print('Conexión establecida con el servidor.', 2)

          self.host = host
          self.port = port

          # Se crea un nuevo thread para obtener los mensajes desde el servidor.
          recv_message_thread = threading.Thread(target=self.handle_communication)
          recv_message_thread.daemon = True
          recv_message_thread.start()

          # Se genera la interfaz de usuario según sus configuraciones predefinidas.
          self.gui_generation()

        except Exception as error:
            log_print(
                'Se ha producido el siguiente error al establecer conexión con el servidor:', 0)
            log_print(str(error), 0)
            return
    
    # Método para generar la interfaz de usuario utilizando Tkinter.
    def gui_generation(self):
      self.root_window = Tk()
      self.root_window.title('PySocketChat')

      # Textarea para imprimir mensajes recibidos.
      self.message_list_textarea = Text(self.root_window)
      self.message_list_textarea.config(state=DISABLED) # Readonly
      self.message_list_textarea.grid(row= 0, column=0, columnspan=2)

      # Textarea para escribir nuevo mensaje.
      self.message_entry = Text(self.root_window, width=100)
      self.message_entry.grid(row=1, column=0)

      # Botón de envío de mensaje.
      self.send_button = Button(self.root_window, text='Enviar', command=self.send_message)
      self.send_button.grid(row=1, column=1)

      self.root_window.mainloop()

    # Método para obtener datos desde el servidor.    
    def handle_communication(self):
      while True:
        data = self.sock.recv(4096)

        if not data:
          log_print('Se ha perdido conexión con el servidor.', 0)
          self.sock.close()
          break

        # Se decodifica el mensaje entrante y se actualiza la lista de mensajes de la interfaz.
        incoming_msg = data.decode('UTF-8')

        self.message_list_textarea.configure(state='normal')
        self.message_list_textarea.insert(END, incoming_msg)
        self.message_list_textarea.config(state=DISABLED)

    
    # Método para enviar datos al servidor.
    def send_message(self):
      # Se activa el textarea (originalmente en 'readonly') para actualizarlo.
      self.message_list_textarea.configure(state='normal')
      new_message = self.message_entry.get('1.0', END)

      if len(new_message.strip()) == 0:
        return
      
      msg = '* Tú mensaje: \n' + new_message + '\n'

      self.message_list_textarea.insert(END, msg)
      self.message_list_textarea.config(state=DISABLED)

      self.sock.send(msg.encode(encoding='UTF-8'))

      self.message_entry.delete('1.0', END)



if __name__ == '__main__':
  client = Client('127.0.0.1', 3000)
