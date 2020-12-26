import sys
import pickle
import socket
import colorama
import threading

from tkinter import *

from datetime import datetime

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
          self.logged_in = False # Permite saber si el usuario se encuentra dentro del chat.

          # Se genera la interfaz de usuario según sus configuraciones predefinidas.
          self.gui_generation()

        except Exception as error:
            log_print(
                'Se ha producido el siguiente error al establecer conexión con el servidor:', 0)
            log_print(str(error), 0)
            return
    
    # Método para cerrar conexión al cerrar la interfaz de usuario
    def close_gui_window(self):
      self.sock.close()
      self.recv_message_thread.join()

      exit()

    # Método para generar la interfaz de usuario utilizando Tkinter.
    def gui_generation(self):
      self.root_window = Tk()
      self.root_window.iconbitmap('../gui-files/root-icon.ico')
      self.root_window.withdraw()
      self.root_window.protocol('WM_DELETE_WINDOW', self.close_gui_window)

      # Ventana de inicio de sesión
      self.login = Toplevel()
      self.login.title('PySocketChat - Inicio de sesión')
      self.login.iconbitmap('../gui-files/root-icon.ico')
      self.login.protocol('WM_DELETE_WINDOW', self.close_gui_window)
      self.login.resizable(width=False,
                           height=False)
      self.login.configure(width=500,
                           height=400,
                           bg="#00695c")
        
      
      self.pls = Label(self.login,
                       text="Ingresa tu nombre de usuario",
                       justify=CENTER,
                       font="Helvetica 14 bold",
                       bg="#00695c",
                       fg="#ffffff")

      self.pls.place(relheight=0.15,
                     relx=0.2,
                     rely=0.07)
      
      self.entryName = Entry(self.login,
                             justify=CENTER,
                             font="Helvetica 12")

      self.entryName.place(relwidth=0.4,
                           relheight=0.08,
                           relx=0.3,
                           rely=0.2)
      
      # Botón para continuar con la siguiente ventana.
      self.go = Button(self.login,
                       text="Continuar",
                       font="Helvetica 14 bold",
                       command=lambda: self.go_ahead(self.entryName.get()))

      self.go.place(relx=0.38,
                    rely=0.3)

      self.root_window.mainloop()
    
    # Método para cambiar de ventana en la interfaz de usuario.
    def go_ahead(self, name):
      self.login.destroy()

      if len(name.strip()) == 0:
        self.gui_generation()

      self.layout(name)

    # Layout principal del chat.
    def layout(self, name):

      # Se crea un nuevo thread para obtener los mensajes desde el servidor.
      self.recv_message_thread = threading.Thread(target=self.handle_communication)
      self.recv_message_thread.daemon = True
      self.recv_message_thread.start()

      self.username = name
      self.username_register() # Registro del nombre de usuario en el servidor.

      # Se muestra la ventana del chat.
      self.root_window.deiconify()
      self.root_window.title('PySocketChat - Chatroom')
      self.root_window.resizable(width=False,
                                 height=False)
      self.root_window.configure(width=470,
                            height=550,
                                 bg="#004d40")
      
      self.labelHead = Label(self.root_window,
                             bg="#00695c",
                             fg="#EAECEE",
                             text=self.username,
                             font="Helvetica 13 bold",
                             pady=5)
      
      self.labelHead.place(relwidth=1)
      self.line = Label(self.root_window,
                        width=450,
                        bg="#004d40")
      
      self.line.place(relwidth=1,
                      rely=0.07,
                      relheight=0.012)

      self.textCons = Text(self.root_window,
                           width=20,
                           height=2,
                           bg="#e0f2f1",
                           fg="#212121",
                           font="Helvetica 10 bold",
                           padx=5,
                           pady=5)
      
      self.textCons.config(state=DISABLED)

      self.textCons.place(relheight=0.745,
                          relwidth=1,
                          rely=0.08)
      
      self.labelBottom = Label(self.root_window,
                               bg="#00695c",
                               height=80)
      
      self.labelBottom.place(relwidth=1,
                             rely=0.825)
      
      self.entryMsg = Text(self.labelBottom,
                           bg="#e0f2f1",
                           fg="#212121",
                            font="Helvetica 10")
      
      # Posiciona el widget dentro de la ventana.
      self.entryMsg.place(relwidth=0.74,
                          relheight=0.06,
                          rely=0.008,
                          relx=0.011)

      self.entryMsg.focus()

      # Se crea el botón para enviar mensajes.
      self.buttonMsg = Button(self.labelBottom,
                              text="Enviar",
                              font="Helvetica 10 bold",
                              width=20,
                              bg="#e0f2f1",
                              fg="#000000",
                              command=lambda: self.send_message(self.entryMsg.get('1.0', END)))

      self.buttonMsg.place(relx=0.77,
                           rely=0.008,
                           relheight=0.06,
                           relwidth=0.22)

      self.textCons.config(cursor="arrow")

      # Se crea el scroll bar.
      scrollbar = Scrollbar(self.textCons)

      # Se posiciona el scroll bar dentro de la ventana.
      scrollbar.place(relheight=1,
                      relx=0.974)

      scrollbar.config(command=self.textCons.yview)

      self.textCons.config(state=DISABLED)

      self.logged_in = True

    # Método para obtener datos desde el servidor.    
    def handle_communication(self):
      while True:

        try:
          data = self.sock.recv(4096)

          if not data:
            log_print('Se ha perdido conexión con el servidor.', 0)
            self.sock.close()
            break

          if self.logged_in:
            # Se decodifica el mensaje entrante y se actualiza la lista de mensajes de la interfaz.
            recv_data = pickle.loads(data)
            tx_code = recv_data[0]

            if tx_code == 'CLIENT_MSG':
              # Actualización de mensaje recibido desde otro cliente.
              msg_object = recv_data[1]

              # Se genera el mensaje según los atributos del objeto recibido.
              incoming_msg = '\n[' + msg_object['sent_at'] + '] ' + msg_object['sender_username'] + ': \n' + msg_object['incoming_msg'] + '\n'
              self.write_into_chatbox(incoming_msg)
            
            elif tx_code == 'CLIENT_JOIN': # Mensaje de alerta al conectarse un nuevo cliente al chat.

              alert_msg = '\n* ' + recv_data[1] + ' se ha unido al chat.\n'
              self.write_into_chatbox(alert_msg)
            
            elif tx_code == 'CLIENT_EXIT': # Mensaje de alerta al desconectarse un cliente del chat.
              
              alert_msg = '\n* ' + recv_data[1] + ' ha abandonado el chat.\n'
              self.write_into_chatbox(alert_msg)

        except Exception as error:
          log_print(
              'Se ha producido el siguiente error al establecer conexión con el servidor:', 0)
          log_print(str(error), 0)
          return
    
    # Método para escribir dentro del chatbox.
    def write_into_chatbox(self, message):
      self.textCons.config(state=NORMAL)
      self.textCons.insert(END, message)

      self.textCons.config(state=DISABLED)
      self.textCons.see(END)
    
    # Método para registrar nombre de usuario en el servidor
    def username_register(self):
      data = pickle.dumps(('USERNAME_REG', self.username))
      self.sock.send(data)
    
    # Método para enviar datos al servidor.
    def send_message(self, new_message):
      if len(new_message.strip()) == 0:
        return
      
      self.entryMsg.delete('1.0', END)

      # Se genera la tupla para el envío del mensaje y el código de transacción
      data = pickle.dumps(('CLIENT_MSG', new_message))
      self.sock.send(data)

      sent_at = str(datetime.now().replace(microsecond=0))
      new_message = '\n[' + sent_at + '] Tú: \n' + new_message + '\n'
      self.write_into_chatbox(new_message)



if __name__ == '__main__':
  client = Client('127.0.0.1', 3000)
