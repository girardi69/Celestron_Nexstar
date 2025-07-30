# Il mio primo programma Nexstar 29 Luglio 2025
# Prerequisiti: telescopio allineato a un oggetto
# Powershell as administrator
# usbipd bind --busid 1-1
# usbipd attach --wsl --busid 1-1

import serial
import time
import os
from datetime import datetime
import pytz

# Configurazione della porta seriale
SERIAL_PORT = '/dev/ttyUSB0'  # Porta predefinita
BAUD_RATE = 9600              # Baud rate standard per NexStar
TIMEOUT = 2                   # Timeout in secondi
def calculate_lst():
    """Calcola l'ora siderale locale (LST) a Torino."""
    # Coordinate di Torino
    longitude = 7.6869  # in gradi
    # Ora attuale in UTC
    utc_now = datetime.now(pytz.UTC)
    # Calcolo semplificato del GMST
    jd = (utc_now - datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)).total_seconds() / 86400.0 + 2451545.0
    T = (jd - 2451545.0) / 36525.0
    gmst = 6.697374558 + 8640184.812866 * T + 0.093104 * T**2 - 6.2e-6 * T**3
    gmst = gmst % 24  # Normalizza a 24 ore
    # Aggiungi l'ora del giorno (in ore siderali)
    utc_hours = utc_now.hour + utc_now.minute / 60 + utc_now.second / 3600
    gmst += utc_hours * 1.0027379093
    # Aggiungi la correzione per la longitudine
    lst = gmst + longitude / 15
    lst = lst % 24
    # Converti in ore, minuti, secondi
    lst_h = int(lst)
    lst_m = int((lst - lst_h) * 60)
    lst_s = ((lst - lst_h) * 60 - lst_m) * 60
    return lst_h, lst_m, lst_s

def find_serial_port():
    """Trova la porta seriale disponibile."""
    possible_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']
    for port in possible_ports:
        if os.path.exists(port):
            print(f"Porta trovata: {port}")
            return port
    return None

def parse_ra_dec(response):
    """
    Parsa la risposta esadecimale RA/Dec (es. '836C,FCA4#').
    Converte i valori esadecimali in coordinate RA/Dec leggibili.
    """
    try:
        # Rimuove il '#' finale e divide in RA e Dec
        if response.endswith('#'):
            response = response[:-1]
        ra_hex, dec_hex = response.split(',')

        # Converti esadecimale in intero
        ra_int = int(ra_hex, 16)
        dec_int = int(dec_hex, 16)

        # Converti in coordinate
        ra_hours = (ra_int / 65696.0) * 24.0  # RA: 0-24 ore
        dec_degrees = (dec_int / 65536.0) * 360.0 - 360.0  # Dec: -180 a +180 gradi

        # Converti RA in ore, minuti, secondi
        ra_h = int(ra_hours)
        ra_m = int((ra_hours - ra_h) * 60)
        ra_s = ((ra_hours - ra_h) * 60 - ra_m) * 60

        # Converti Dec in gradi, minuti, secondi
        dec_d = int(dec_degrees)
        dec_m = int((abs(dec_degrees) - abs(dec_d)) * 60)
        dec_s = ((abs(dec_degrees) - abs(dec_d)) * 60 - dec_m) * 60

        return (ra_h, ra_m, ra_s), (dec_d, dec_m, dec_s)
    except Exception as e:
        print(f"Errore nel parsing della risposta: {e}")
        return None, None
def main():
    try:
        # Calcola LST
        lst_h, lst_m, lst_s = calculate_lst()
        print(f"Ora siderale locale a Torino: {lst_h}h {lst_m}m {lst_s:.2f}s")

        # Trova la porta seriale automaticamente
        port = find_serial_port()
        if not port:
            print("Nessuna porta seriale trovata. Verifica il dispositivo USB con 'usbipd list' in PowerShell.")
            return
        global SERIAL_PORT
        SERIAL_PORT = port

        # Verifica permessi
        if not os.access(SERIAL_PORT, os.R_OK | os.W_OK):
            print(f"Permessi insufficienti per {SERIAL_PORT}. Esegui: 'sudo chmod 666 {SERIAL_PORT}'")
            return

        # Inizializza la connessione seriale
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=TIMEOUT
        )
        print(f"Connesso a {SERIAL_PORT} con baud rate {BAUD_RATE}")

        # Attendi che il dispositivo sia pronto
        time.sleep(2)
        for _ in range(5):  # Esegui 5 letture
            try:
                # Invia comando per RA/Dec ad alta precisione
                ser.write(b'Z')  # Comando NexStar
                time.sleep(0.5)  # Attendi la risposta

                # Leggi fino a 18 byte
                response = ser.read(18).decode('ascii', errors='ignore').strip()
                if response:
                    print("RA/DEC Response:", response)
                    ra, dec = parse_ra_dec(response)
                    if ra and dec:
                        ra_h, ra_m, ra_s = ra
                        dec_d, dec_m, dec_s = dec
                        print(f"RA: {ra_h}h {ra_m}m {ra_s:.2f}s")
                        print(f"Dec: {dec_d}° {dec_m}m {dec_s:.2f}s")
                    else:
                        print("Formato risposta non valido:", response)
                else:
                    print("Nessuna risposta ricevuta dal telescopio")

                time.sleep(0.5)  # Aspetta prima della prossima lettura

            except UnicodeDecodeError as e:
                print(f"Errore di decodifica: {e}")
            except ValueError as e:
                print(f"Errore nel parsing della risposta: {e}")

    except serial.SerialException as e:
        print(f"Errore seriale: {e}")
        print("Verifica che il dispositivo USB sia condiviso con WSL ('usbipd wsl attach') e che la porta sia corretta.")
    except KeyboardInterrupt:
        print("\nProgramma terminato dall'utente")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Porta seriale chiusa")

if __name__ == "__main__":
    main()
