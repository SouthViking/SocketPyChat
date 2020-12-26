import colorama
from datetime import datetime
from colorama import Fore, Back, Style

# Prints con formato '[Fecha - Hora] mensaje' y color según su tipo.
def log_print(message, msg_type):
    current_datetime = datetime.now().replace(microsecond=0)
    fore_color = None

    if msg_type == 0:  # Error msg
        fore_color = Fore.RED
        pass

    elif msg_type == 1:  # Warning msg
        fore_color = Fore.YELLOW
        pass

    elif msg_type == 2:  # Success msg
        fore_color = Fore.GREEN
        pass

    elif msg_type == 3:  # Info msg
        fore_color = Fore.CYAN
        pass

    if fore_color:
        print(fore_color + '[' + str(current_datetime) +
              '] ' + message + Style.RESET_ALL)
    else:
        print('[' + str(current_datetime) + '] ' + message + Style.RESET_ALL)
