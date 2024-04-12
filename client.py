import socket

def send_msg(ip, port, msg):
    HOST = ip
    PORT = port
    data = msg
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))
            sock.sendall(bytes(data+"\n", 'utf-8'))
        return "OK bytes were written"
    except Exception as ex:
        return str(ex)
        
    