import socket
from networking import *

SERVER = extract_ip()
change_global_var("ADDR", (SERVER, return_global_var("PORT")))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(return_global_var("ADDR"))
print("CREATED SOCKET!")

print(f"LISTENING FOR CONNECTIONS AT {SERVER}...")
server.listen()
conn, addr = server.accept()
print(f"NEW CONNECTION AT {addr}")

initialize_receiver_connection(conn)
receive_file(server)
print("DONE!")
conn.close()
