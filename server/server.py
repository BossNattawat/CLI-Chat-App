import socket
import threading
import sqlite3
import bcrypt

HOST = '127.0.0.1'
PORT = 12345

clients = {}
rooms = {}

# Database setup
conn = sqlite3.connect('chat.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY,
        room_id TEXT UNIQUE,
        password TEXT
    )
""")
conn.commit()

def handle_client(client_socket, addr):
    try:
        client_socket.send(b"Welcome! Type 'register' or 'login': ")
        mode = client_socket.recv(1024).decode().strip().lower()

        if mode == 'register':
            while True:
                client_socket.send(b"Username: ")
                username = client_socket.recv(1024).decode().strip()
                if not username:
                    client_socket.send(b"Please provide username!\n")
                    continue

                client_socket.send(b"Password: ")
                password = client_socket.recv(1024).decode().strip()
                if not password:
                    client_socket.send(b"Please provide password!\n")
                    continue
                if len(password) <= 6:
                    client_socket.send(b"Your password must be at least 6 characters long!\n")
                    continue

                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

                try:
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
                    conn.commit()
                    client_socket.send(b"Registered successfully. Please login.\n")
                    break
                except sqlite3.IntegrityError:
                    client_socket.send(b"Username already exists.\n")
                    return

        if mode == 'login':
            while True:
                client_socket.send(b"Username: ")
                username = client_socket.recv(1024).decode().strip()
                if not username:
                    client_socket.send(b"Please provide username!\n")
                    continue

                client_socket.send(b"Password: ")
                password = client_socket.recv(1024).decode().strip()
                if not password:
                    client_socket.send(b"Please provide password!\n")
                    continue
                if len(password) <= 6:
                    client_socket.send(b"Your password must be at least 6 characters long!\n")
                    continue

                cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()

                if not result or not bcrypt.checkpw(password.encode(), result[0]):
                    client_socket.send(b"Invalid login.\n")
                    continue

                client_socket.send(b"Login successful.\n")
                clients[client_socket] = username
                break

        client_socket.send(b"[1] Create Room\n[2] Join Room\nChoose option: ")
        option = client_socket.recv(1024).decode().strip()

        room_id = None

        if option == '1':
            while True:
                client_socket.send(b"Room ID: ")
                room_id = client_socket.recv(1024).decode().strip()

                cursor.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,))
                if cursor.fetchone():
                    client_socket.send(b"Room ID already exists. Please try again.\n")
                    continue

                client_socket.send(b"Room Password: ")
                room_pass = client_socket.recv(1024).decode().strip()
                if not room_pass:
                    client_socket.send(b"Please provide password!\n")
                    continue

                hashed_pass = bcrypt.hashpw(room_pass.encode(), bcrypt.gensalt())
                cursor.execute("INSERT INTO rooms (room_id, password) VALUES (?, ?)", (room_id, hashed_pass))
                conn.commit()
                rooms[room_id] = [client_socket]
                client_socket.send(b"Room created. Start chatting:\n")
                break

        elif option == '2':
            while True:
                client_socket.send(b"Room ID: ")
                room_id = client_socket.recv(1024).decode().strip()

                cursor.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,))
                if not cursor.fetchone():
                    client_socket.send(b"Room ID does not exist. Please try again.\n")
                    continue

                client_socket.send(b"Room Password: ")
                room_pass = client_socket.recv(1024).decode().strip()
                if not room_pass:
                    client_socket.send(b"Please provide password!\n")
                    continue

                cursor.execute("SELECT password FROM rooms WHERE room_id = ?", (room_id,))
                result = cursor.fetchone()
                if not result or not bcrypt.checkpw(room_pass.encode(), result[0]):
                    client_socket.send(b"Invalid room credentials.\n")
                    continue

                rooms.setdefault(room_id, []).append(client_socket)
                client_socket.send(b"Joined room. Start chatting:\n")
                break
        else:
            client_socket.send(b"Invalid option.\n")
            return

        # Chat loop
        while True:
            try:
                msg = client_socket.recv(1024)
                if not msg:
                    break

                decoded_msg = msg.decode().strip()
                username = clients.get(client_socket, "Unknown")

                if decoded_msg == "/clients":
                    current_clients = [clients.get(c, "Unknown") for c in rooms.get(room_id, [])]
                    client_socket.send(f"Users in room:\n".encode() + "\n".join(current_clients).encode())
                    continue

                full_msg = f"{username} >> {decoded_msg}".encode()
                for client in rooms.get(room_id, []):
                    if client != client_socket:
                        try:
                            client.send(full_msg)
                        except:
                            continue
            except:
                break

    finally:
        if room_id and client_socket in rooms.get(room_id, []):
            rooms[room_id].remove(client_socket)
        if client_socket in clients:
            del clients[client_socket]
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[+] Server started on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"[+] New connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

if __name__ == "__main__":
    main()
