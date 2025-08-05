from rich.console import Console
from rich.panel import Panel
import socket
import threading

console = Console()
HOST = '127.0.0.1'
PORT = 12345

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024)
            if not msg:
                break
            console.print(f"[bold cyan]{msg.decode()}[/]")
        except:
            break

def main():
    console.print(Panel("💬 [bold yellow]Welcome to CLI Chat App[/bold yellow]", expand=False))

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    thread = threading.Thread(target=receive_messages, args=(client,), daemon=True)
    thread.start()

    while True:
        try:
            msg = console.input("[bold green]>> [/bold green]")
            if msg.lower() in ['exit', 'quit']:
                console.print("[bold red]👋 Goodbye![/bold red]")
                break
            client.send(msg.encode())
        except KeyboardInterrupt:
            break

    client.close()

if __name__ == "__main__":
    main()
