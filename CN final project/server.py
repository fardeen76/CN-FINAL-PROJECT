import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = '127.0.0.1'
PORT = 1234
LISTENER_LIMIT = 5
active_clients = []  

server = None  
server_running = False  


def send_message_to_client(client, message):
    
    try:
        client.sendall(message.encode())
    except:
        print("Failed to send message to client.")


def send_messages_to_all(message):
    
    for user in active_clients:
        send_message_to_client(user[1], message)


def listen_for_messages(client, username):
    
    while server_running:
        try:
            message = client.recv(2048).decode('utf-8')
            if message:
                final_msg = f"{username}~{message}"
                send_messages_to_all(final_msg)
                log_message(final_msg)
            else:
                print(f"The message sent from client {username} is empty.")
        except:
            remove_client(username, client)
            break


def client_handler(client):
    
    global active_clients
    try:
        while server_running:
            username = client.recv(2048).decode('utf-8')
            if username:
                active_clients.append((username, client))
                prompt_message = f"SERVER~{username} joined the chat."
                send_messages_to_all(prompt_message)
                log_message(prompt_message)
                break
            else:
                print("Client username is empty.")
        threading.Thread(target=listen_for_messages, args=(client, username), daemon=True).start()
    except:
        client.close()


def remove_client(username, client):
    
    global active_clients
    active_clients = [user for user in active_clients if user[1] != client]
    send_messages_to_all(f"SERVER~{username} has left the chat.")
    log_message(f"{username} disconnected.")


def start_server():
    
    global server, server_running
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen(LISTENER_LIMIT)
        server_running = True
        log_message(f"Server started on {HOST}:{PORT}.")
        threading.Thread(target=accept_clients, daemon=True).start()
    except Exception as e:
        log_message(f"Error starting server: {e}")


def stop_server():
    
    global server, server_running
    if server_running:
        server_running = False
        for user in active_clients:
            user[1].close()
        active_clients.clear()
        if server:
            server.close()
            server = None
        log_message("Server stopped.")


def accept_clients():
    
    global server
    while server_running:
        try:
            client, address = server.accept()
            log_message(f"Connected to client {address[0]}:{address[1]}.")
            threading.Thread(target=client_handler, args=(client,), daemon=True).start()
        except:
            break



app = tk.Tk()
app.title("Chat Server")
app.configure(bg="#222831")


TEXT_BG = "#1E293B"  
TEXT_FG = "#E0E7FF"  
BUTTON_BG = "#00ADB5"  
BUTTON_FG = "#222831" 


log_area = scrolledtext.ScrolledText(
    app,
    width=50,
    height=20,
    state=tk.DISABLED,
    bg=TEXT_BG,  
    fg=TEXT_FG,  
    font=("Helvetica", 12),
    wrap=tk.WORD
)
log_area.pack(padx=10, pady=10)


def log_message(message):
    """Logs a message to the GUI."""
    log_area.config(state=tk.NORMAL)
    log_area.insert(tk.END, f"{message}\n")
    log_area.config(state=tk.DISABLED)
    log_area.yview(tk.END)



start_button = tk.Button(
    app,
    text="Start Server",
    command=start_server,
    bg=BUTTON_BG,
    fg=BUTTON_FG,
    font=("Helvetica", 14),
    width=15
)
start_button.pack(side=tk.LEFT, padx=20, pady=10)


stop_button = tk.Button(
    app,
    text="Stop Server",
    command=stop_server,
    bg=BUTTON_BG,
    fg=BUTTON_FG,
    font=("Helvetica", 14),
    width=15
)
stop_button.pack(side=tk.RIGHT, padx=20, pady=10)

app.mainloop()
