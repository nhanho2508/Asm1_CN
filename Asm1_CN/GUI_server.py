import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from server.server import *
from peer.peer import *
import psutil
import socket

# Tạo cửa sổ chính
accept_thread = None
send_thread = None
server = None
root = tk.Tk()
root.title("Simple file-sharing application")
lbl =Label(root, text = "SERVER INTERFACE", font = 'arial 15 bold', fg='black')
lbl.pack(side="top", pady=5)
root.geometry("500x280")
root.resizable(False,True)

frame = tk.Frame(root, bg="white", bd=2, relief="solid", width=200, height=50)
frame.pack(side="bottom", fill="both", expand=True, padx=3, pady=3)

# Tạo label bên trong khung
inform_text = tk.Text(frame, wrap=tk.WORD, height = 7)
inform_text.insert(tk.END, "WELCOME TO OUR APPLICATION\n")
inform_text.pack(fill="both", expand=True)
error_label = tk.Label(frame, text="", fg="red")
error_label.pack( fill="both", expand=True)
######Check host###########
def get_wifi_ip_address():
    target_interface = "Wi-Fi 2"  # Thay thế bằng tên của giao diện WiFi bạn quan tâm
    interfaces = psutil.net_if_addrs()
    for interface, addresses in interfaces.items():
        if interface == target_interface:
            for address in addresses:
                if address.family == socket.AF_INET:
                    return address.address
    return None

def choosePort():
    host = get_wifi_ip_address()
    if host == None:
        host = socket.gethostbyname(socket.gethostname())
    port = "8080"
    port = port_entry.get()
    if port == '':
        error_label.config(text="Please fill in the valid port number")
    else:
        error_label.config(text="")
        global server
        server = Server(host, int(port),True)
        response = server.info
        server.info = ""
        inform_text.insert(tk.END,response+"\n")
        global accept_thread
        global send_thread
        accept_thread = threading.Thread(target=server.accept_connect, args=())
        send_thread = threading.Thread(target=server.send_command, args=())
        # Start both threads
        accept_thread.start()
        send_thread.start()
        catch_event_thread = threading.Thread(target=catch_event, args=())
        
        # listen_thread.join()
        # send_thread.join()
        port_frame.pack_forget()
        root.geometry("500x500")
        main_frame.pack(padx=20, pady=10)
        catch_event_thread.start()
def discover():
    user_discover = user_entry.get()
    if (user_discover==""):
        error_label.config(text="Vui lòng nhập username cần discover")
    else: 
        error_label.config(text="")
        server.command_line = f"discover {user_discover}"
def ping():
    user_ping = ping_entry.get()
    if (user_ping==""):
        error_label.config(text="Vui lòng nhập username cần ping")
    else: 
        error_label.config(text="")
        server.command_line = f"ping {user_ping}"
def show():
    server.command_line = f"host_info"

def catch_event():
    while True:
        if(server.info_renew):
            inform_text.insert(tk.END, server.info+"\n")
            server.info_renew = False
        if(server.error_renew):
            error_label.config(text=server.error)
            server.error_renew = False
        time.sleep(0.2)
##########PORT ENTER FRAME#################
port_frame =tk.Frame(root, padx =5, pady =3)
port_frame.pack(padx=20,pady=5)
tk.Label(port_frame, text="Choose a port for your server set up",font = 'arial 10 bold', fg='black').grid(row=0, columnspan=2)
tk.Label(port_frame, text="Enter server port:").grid(row=1, column=0, sticky="e",pady=5,padx=2)
port_entry = tk.Entry(port_frame)
port_entry.grid(row=1, column=1, pady=5)
port_button = tk.Button(port_frame, text="Enter", command=choosePort)
port_button.grid(row=1, column=2, padx=2, pady=5)
########## MAIN FRAME ################
main_frame =tk.Frame(root, padx =5, pady =3)
main_frame.pack(padx=20,pady=5)
tk.Label(main_frame, text="Manage your client here",font = 'arial 10 bold', fg='black').grid(row=0, columnspan=2)
tk.Label(main_frame, text="Enter client you want to discover:").grid(row=1, column=0, sticky="e",pady=5,padx=2)
user_entry = tk.Entry(main_frame)
user_entry.grid(row=1, column=1, pady=5)
discover_button = tk.Button(main_frame, text="Discover", command=discover, width=10)
discover_button.grid(row=1, column=2, padx=5, pady=5)
###Ping
tk.Label(main_frame, text="Enter client you want to ping").grid(row=2, column=0, sticky="e",pady=5,padx=2)
ping_entry = tk.Entry(main_frame)
ping_entry.grid(row=2, column=1, pady=5)
ping_button = tk.Button(main_frame, text="Ping", command=ping, width=10)
ping_button.grid(row=2, column=2, padx=5, pady=5)
###HostInfo
tk.Label(main_frame, text="Show information of all clients").grid(row=3, column=0, sticky="e",pady=5,padx=2)
show_button = tk.Button(main_frame, text="Show", command=show)
show_button.grid(row=3, column=1, padx=5, pady=5)

# Khởi chạy vòng lặp chính của GUI
root.pack_propagate(True)
root.mainloop()
