import socket
from compress import *
from encrypt import *


def extract_ip() -> str:
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('255.255.255.255', 1))
        ip = st.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        st.close()
    return ip


GLOBALS = {
    "PORT": 1114,
    "FORMAT": "utf-8",
    "MTU": 4096,
    "ACK": "!ACK",
    "FAIL": "!FAIL",
    "NEWKEY": "",
    "ADDR": (),
    "CLIENT_IP": ""
}

GLOBALS["ODD_MSG_LEN"] = len(str(GLOBALS["MTU"]).encode(GLOBALS["FORMAT"]))
GLOBALS["ENCRYPTEDFILEDIRPATH"] = os.path.abspath("EncryptedFiles")


# Global Changing Functions
def return_global_var(var_name: str) -> tuple[str, int]:
    global GLOBALS
    if var_name in GLOBALS:
        return GLOBALS[var_name]
    else:
        raise Exception(f"GLOBAL with name {var_name} does not exist!")


def change_global_var(var_name: str, changed_val):
    global GLOBALS
    if var_name in GLOBALS:
        GLOBALS[var_name] = changed_val
    else:
        raise Exception(f"GLOBAL with name {var_name} does not exist!")


# when given data to format, returns the msg_1 and msg_2
# msg_1 - msg_len bits in size, contains the size in bytes of msg_2, encoded w/ format
# msg_2 - contains data encoded w/format
def format_outgoing_transmission(data: str, msg_len: int = GLOBALS["ODD_MSG_LEN"], format: str = GLOBALS["FORMAT"]) -> tuple[bytes, bytes]:
    global GLOBALS

    encoded_data = data.encode(format)
    data_len = len(encoded_data)
    encoded_data_len = str(data_len).encode(format)
    padding_len = (msg_len - len(encoded_data_len))
    if padding_len < 0:
        print("Padding is less than zero!")
        print("DATA LOSS MAY OCCUR DURING RECEIVING")

    msg_1 = encoded_data_len + (b' ' * padding_len)
    msg_2 = encoded_data

    return msg_1, msg_2


# takes msg_1 as encoded bytes w/ padding, returns decoded int
def format_msg_1(msg1: bytes, decode_format: str = GLOBALS["FORMAT"]) -> int:
    global GLOBALS
    return int(msg1.decode(decode_format))


# takes msg_2 as encoded bytes, returns decoded str
def format_msg_2(msg2: bytes, decode_format: str = GLOBALS["FORMAT"]) -> str:
    global GLOBALS
    return msg2.decode(decode_format)


def check_if_valid_ip(ip: str) -> bool:
    if '.' not in ip:
        return False

    split_ip = ip.split('.')
    if len(split_ip) != 4:
        return False

    for i in split_ip:
        if int(i) < 0 or int(i) > 255:
            return False

    return True


def send_msg(cur_socket, data: str):
    data_tuple = format_outgoing_transmission(data)
    cur_socket.send(data_tuple[0])
    cur_socket.send(data_tuple[1])


def receive_msg(cur_socket) -> str:
    global GLOBALS

    msg_1 = cur_socket.recv(GLOBALS["ODD_MSG_LEN"])
    msg_2_len = format_msg_1(msg_1)
    msg_2 = cur_socket.recv(msg_2_len)

    return format_msg_2(msg_2)


# Sender Specific

# takes connected client_socket
def initialize_sender_connection(client_socket):
    global GLOBALS
    # 1. Ip exchange

    # 1.1 Server sends IP
    # -> recieve IP
    received_ip = receive_msg(client_socket)
    # 1.1 END

    # 1.2 Client sends IP / FAIL
    # -> check IP validity & if it matches socket ip, send IP / FAIL
    if check_if_valid_ip(received_ip) == False or received_ip != GLOBALS["CLIENT_IP"]:
        send_msg(client_socket, GLOBALS["FAIL"])

        client_socket.close()
        print(f"INCORRECT IP RECIEVED, CORRECT IP: {GLOBALS['CLIENT_IP']}, RECEIVED IP {received_ip}")
        raise Exception("INCORRECT IP RECEIVED!,TERMINATING CONNECTION!")

    send_msg(client_socket, GLOBALS["ADDR"][0])
    # 1.2 END

    # 1.3 Server sends ACK / FAIL
    # -> recieve ACK / FAIL, continue if ACK, raise exception if FAIL or else
    received_status = receive_msg(client_socket)

    if received_status != GLOBALS["ACK"]:
        if received_status == GLOBALS["FAIL"]:
            client_socket.close()
            raise Exception("FAIL RECIEVED DURING IP EXCHANGE!,TERMINATED CONNECTION!")
        else:
            client_socket.close()
            raise Exception(f"UNIDENTIFIED STATUS: {received_status} DURING IP EXCHANGE!, TERMINATED CONNECTION!")
        # 1.3 END
    print("SUCCESSFUL IP EXCHANGE!")
    # 1. END

    # 2. Key Exchange

    # 2.1 Client sends newly generated key, encrypted with private key
    # -> generate NEWKEY, read private key from file, encrypt NEWKEY
    # -> send NEWKEY
    GLOBALS["NEWKEY"] = Fernet.generate_key()
    print(f'NEWKEY: {GLOBALS["NEWKEY"]}')
    private_key = return_key_from_file("key.txt")
    key_msg = return_encrypted(GLOBALS["NEWKEY"], private_key).decode()

    send_msg(client_socket, key_msg)
    # 2.1 END

    # 2.2 Server sends hash of new key or FAIL
    # -> receive msg, check if FAIL
    hash_msg = receive_msg(client_socket)
    if hash_msg == GLOBALS["FAIL"]:
        client_socket.close()
        raise Exception("FAIL RECEIVED DURING HASH EXCHANGE!, TERMINATING CONNECTION!")
    # 2.2 END

    # 2.3 Client sends FAIL or newkey hash encrypted with newkey
    # -> get hash of newkey, compare to received key, send FAIL or encrypted newkey hash
    newkey_hash = return_hash_of_bytes(GLOBALS["NEWKEY"])

    if hash_msg != newkey_hash:
        send_msg(client_socket, GLOBALS["FAIL"])
        client_socket.close()
        raise Exception(f"HASH EXCHANGE FAILED, CORRECT:{newkey_hash}, RECEIVED: {hash_msg}")

    encrypted_newkey_hash = return_encrypted(newkey_hash.encode(), GLOBALS["NEWKEY"])
    send_msg(client_socket, encrypted_newkey_hash.decode())
    # 2.3 END

    # 2.4 Server sends FAIL or ACK
    hash_exchange_status = receive_msg(client_socket)
    if hash_exchange_status == GLOBALS["FAIL"]:
        client_socket.close()
        raise Exception("FAIL RECEIVED DURING HASH EXCHANGE!, TERMINATING CONNECTION!")
    # 2.4 END
    print("SUCCESSFUL KEY EXCHANGE!")
    # 2. END


def send_file(filepath: str, client_socket, key: bytes = GLOBALS["NEWKEY"]):
    global GLOBALS
    send_msg(client_socket, filepath)


# Receiver Specific
def initialize_receiver_connection(server_socket):
    global GLOBALS
    # 1. IP Exchange

    # 1.1 Server sends IP
    # -> send IP
    send_msg(server_socket, GLOBALS["ADDR"][0])
    # 1.1 END

    # 1.2 Client sends IP / FAIL
    # -> receive transmission, raise exception if fail, else check ip validity
    received_ip = receive_msg(server_socket)

    if not check_if_valid_ip(received_ip):
        if received_ip == GLOBALS["FAIL"]:
            server_socket.close()
            raise Exception("FAIL RECEIVED DURING IP EXCHANGE!,TERMINATED CONNECTION!")
        else:
            server_socket.close()
            raise Exception(f"UNRECOGNIZED STATUS RECEIVED DURING IP EXCHANGE: {received_ip}")
        # 1.2 END

    # 1.3 Server sends ACK / FAIL
    # -> evaluate IP correctness, send ACK / FAIL
    if received_ip != GLOBALS["ADDR"][0]:
        send_msg(server_socket, GLOBALS["FAIL"])

        server_socket.close()
        raise Exception(f"INCORRECT IP RECEIVED, CORRECT: {GLOBALS['ADDR'][0]}, RECEIVED: {received_ip}")

    send_msg(server_socket, GLOBALS["ACK"])
    # 1.3 END
    print("SUCCESSFUL IP EXCHANGE!")
    # 1. END

    # 2. Key Exchange

    # 2.1 Client sends newly generated key, encrypted with private key
    # -> receive msg, read private key from file
    # !TODO - if breaks remove .encode()
    received_msg = receive_msg(server_socket).encode()
    private_key = return_key_from_file("key.txt")
    # 2.1 END

    # 2.2 Server sends hash of new key or FAIL
    # -> decrypt msg with private key, get hash of new key
    # -> send hash or FAIL
    try:
        GLOBALS["NEWKEY"] = return_decrypted(received_msg, private_key)
        print(f'NEWKEY: {GLOBALS["NEWKEY"]}')
    except Exception as e:
        print("INVALID MSG, COULD NOT BE DECRYPTED, TERMINATING CONNECTION!")
        send_msg(server_socket, FAIL)
        server_socket.close()
        raise Exception(e)

    newkey_hash = return_hash_of_bytes(GLOBALS["NEWKEY"])
    send_msg(server_socket, newkey_hash)
    # 2.2 END

    # 2.3 Client sends FAIL or newkey hash encrypted with newkey
    # -> check if FAIL
    encrypted_hash_msg = receive_msg(server_socket)
    if encrypted_hash_msg == GLOBALS["FAIL"]:
        server_socket.close()
        raise Exception("FAIL RECEIVED DURING KEY EXCHANGE!, TERMINATING CONNECTION!")
    # 2.3 END

    # 2.4 Server sends FAIL or ACK
    # -> decrypt encrypted_hash_msg with NEWKEY, compare with newkey_hash, send FAIL or ACK
    try:
        hash_msg = return_decrypted(encrypted_hash_msg.encode(), GLOBALS["NEWKEY"])
    except Exception as e:
        print("INVALID MSG, COULD NOT BE DECRYPTED, TERMINATING CONNECTION!")
        send_msg(server_socket, GLOBALS["FAIL"])
        server_socket.close()
        raise Exception(e)

    if hash_msg.decode() == newkey_hash:
        send_msg(server_socket, GLOBALS["ACK"])
    else:
        send_msg(server_socket, GLOBALS["FAIL"])
        server_socket.close()
        raise Exception(f"HASH EXCHANGE FAILED, CORRECT: {newkey_hash}, RECEIVED: {hash_msg}")
    # 2.4 END
    print("SUCCESSFUL KEY EXCHANGE!")
    # 2. END


def receive_file(server_socket,recieved_file_dir: str = GLOBALS["ENCRYPTEDFILEDIRPATH"], key: str = GLOBALS["NEWKEY"]):
    while True:
        try:
            msg = receive_msg(server_socket)
            print(f"{msg}!!!")
        except Exception as E:
            continue
        break