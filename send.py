import socket
from networking import *


change_global_var("CLIENT_IP",extract_ip())
print(f'YOUR IP IS {return_global_var("CLIENT_IP")}')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IPADDR = input("ENTER IP ADDRESS OF SERVER (ex:10.0.0.1)\n")
change_global_var("ADDR", (IPADDR, return_global_var("PORT")))

print(f"1/2 - CONNECTING TO SERVER AT {return_global_var('ADDR')}")

try:
    client.connect(return_global_var("ADDR"))
except Exception as e:
    print(e)
    print("INCORRECT SERVER ADDRESS / SERVER IS UNREACHABLE")
    raise Exception(e)

print(f"2/2 - CONNECTED TO {client.getpeername()}!")

# 1-2 (Key & IP Exchange)
initialize_sender_connection(client)

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

    compressed_file_path = master_compress(filepath)
    encrypted_file_path = master_encrypt(compressed_file_path, return_global_var("NEWKEY"))
    break

send_file(encrypted_file_path, client)

client.close()
print("DONE!")

# with open(filepath,'rb') as f:
#     data = f.read()
#     times_to_send = len(data) / MTUnit
#     last_send_unit = len(data) % MTUnit
#     client_socket.send(data)
