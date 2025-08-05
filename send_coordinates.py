import serial
import time
from datetime import datetime
import pytz

# Configurazione della porta seriale
SERIAL_PORT = '/dev/ttyUSB0'  # Modifica con la tua porta (es. 'COM3' su Windows)
BAUD_RATE = 9600
TIMEOUT = 2

# Coordinate di esempio (Azimut: 180°, Altitudine: 45°)
AZIMUTH_DEGREES = 170.0  # Azimut in gradi
ALTITUDE_DEGREES = 43.0  # Altitudine in gradi

def connect_telescope(port, baudrate, timeout):
    """Connessione al telescopio Nexstar."""
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"Connesso alla porta {port}")
        return ser
    except serial.SerialException as e:
        print(f"Errore di connessione: {e}")
        return None

def az_alt_to_hex(azimuth, altitude):
    """Converte Azimut e Altitudine in formato esadecimale per il comando GOTO."""
    # Converti Azimut e Altitudine in formato Nexstar (0-0xFFFF)
    az_hex = int((azimuth / 360.0) * 0x10000)  # Scala a 16 bit
    alt_hex = int((altitude / 360.0) * 0x10000)  # Scala a 16 bit
    # Formatta in stringa esadecimale (4 cifre)
    az_str = f"{az_hex:04X}"
    alt_str = f"{alt_hex:04X}"
    return az_str, alt_str
  
def send_goto_az_alt(ser, az_hex, alt_hex):
    """Invia il comando GOTO in Azimut/Altitudine al telescopio."""
    try:
        command = f"B{az_hex},{alt_hex}#".encode()  # Comando 'B' per Az/Alt
        ser.write(command)
        print(f"Comando inviato: {command.decode()}")
        # Attendi risposta
        response = ser.read(1)
        if response == b'#':
            print("Comando GOTO ricevuto correttamente.")
        else:
            print("Errore nella risposta del telescopio.")
        # Attendi il completamento del movimento
        time.sleep(1)
        print("Movimento in corso...")
        time.sleep(5)  # Attendi un tempo ragionevole per il movimento
    except Exception as e:
        print(f"Errore durante l'invio del comando: {e}")

def main():
    # Connessione al telescopio
    ser = connect_telescope(SERIAL_PORT, BAUD_RATE, TIMEOUT)
    if ser is None:
        return

    # Converti le coordinate
    az_hex, alt_hex = az_alt_to_hex(AZIMUTH_DEGREES, ALTITUDE_DEGREES)
    print(f"Coordinate convertite: Azimut={az_hex}, Altitudine={alt_hex}")

    # Invia il comando GOTO
    send_goto_az_alt(ser, az_hex, alt_hex)

    # Chiudi la connessione
    ser.close()
    print("Connessione chiusa.")

if __name__ == "__main__":
    main()
