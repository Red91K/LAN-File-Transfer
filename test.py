import socket
from compress import *
from networking import *

while True:
    filepath = input("ENTER FULL PATH OF FILE TO SEND:\n")

    # check if valid path
    if not os.path.exists(filepath):
        print("INVALID PATH")
        continue

    print(f"SELECTED {return_file_or_dir(filepath)}: {os.path.basename(filepath)} - {return_formated_file_or_dir_size(filepath)}")
    print("CONFIRM SEND? [y/n]")
    confirm_send = input()

    if confirm_send != "y":
        if confirm_send == "n":
            print("SEND CANCELLED")
            continue
        else:
            print("INVALID STATUS - ENTER [y/n]")
            continue

    compressed_file = master_compress(filepath)
    




#uncompress_dir("/Users/jasonoh/Desktop/Coding/Python/Sockets/FileTransfer/ZipFiles/nmap.zip")
"""
def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('255.255.255.255', 1))
        ip = st.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        st.close()
    return ip


PORT = 1114

SERVER = extract_ip()
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

server.listen()
conn, addr = server.accept()
print("connected!")
print(addr)

while True:
    print(conn.recv(4096))
    conn.send(b"FUCK UP")
"""