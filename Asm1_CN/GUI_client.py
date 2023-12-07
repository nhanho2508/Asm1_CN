import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from server.server import *
from peer.peer import *
import psutil
import socket

# Tạo cửa sổ chính
listen_thread = None
send_thread = None
peer = None
root = tk.Tk()
root.title("Simple file-sharing application")
lbl =Label(root, text = "CLIENT INTERFACE", font = 'arial 15 bold', fg='black')
lbl.pack(side="top", pady=5)
root.geometry("400x170")
root.resizable(False,True)

frame = tk.Frame(root, bg="white", bd=2, relief="solid", width=200, height=50)
frame.pack(side="bottom", fill="both", expand=True, padx=3, pady=3)

# Tạo label bên trong khung
inform_label = tk.Label(frame, text="WELCOME TO OUR APPLICATION", fg="blue", bg="white")
inform_label.pack(fill="both", expand=True)
error_label = tk.Label(frame, text="", fg="red")
error_label.pack( fill="both", expand=True)
# Tạo các thành phần giao diện
def get_wifi_ip_address():
    target_interface = "Wi-Fi 2"  # Thay thế bằng tên của giao diện WiFi bạn quan tâm
    interfaces = psutil.net_if_addrs()
    for interface, addresses in interfaces.items():
        if interface == target_interface:
            for address in addresses:
                if address.family == socket.AF_INET:
                    return address.address
    return None
def register():
    username = username_entry.get()
    password = password_entry.get()
    if(username=="" or password==""):
        error_label.config(text="Nhập vào đầy đủ các trường thông tin")
    else:
        error_label.config(text="")
        command_line = f"register {username} {password}"
        peer.set_command(command_line)
        while peer.wait:
            continue
        info = peer.get_info()
        peer.reset_info()
        if info != "":
            login_frame.pack_forget()
            inform_label.config(text=info)
            error_label.config(text="")
            root.geometry("400x500")
            main_frame.pack()
        else:
            info = peer.get_error()
            peer.reset_error()
            error_label.config(text=info)
def login():
    username = username_entry.get()
    password = password_entry.get()
    if(username=="" or password==""):
        error_label.config(text="Nhập vào đầy đủ các trường thông tin")
    else:
        error_label.config(text="")
        command_line = f"login {username} {password}"
        peer.set_command(command_line)
        while peer.wait:
            continue
        info = peer.get_info()
        peer.reset_info()
        # Kiểm tra thông tin đăng nhập, ở đây là một ví dụ đơn giản
        if info != "":
            # Đăng nhập thành công, ẩn phần login
            login_frame.pack_forget()
            inform_label.config(text=info)
            error_label.config(text="")
            root.geometry("400x500")
            main_frame.pack()
        else:
            info = peer.get_error()
            peer.reset_error()
            # Hiển thị thông báo đăng nhập không thành công
            error_label.config(text=info)
def connect():
    server_ip = server_ip_entry.get()
    server_port = server_port_entry.get()
    command_line = f"connect {server_ip} {server_port}"
    peer.set_command(command_line)
    while peer.wait:
        continue
    info = peer.get_info()
    peer.reset_info()
    inform_label.config(text=info)
    ###########
    connect_frame.pack_forget()
    login_frame.pack(padx=5,pady=5) 
def choosePort():
    host = get_wifi_ip_address()
    if host is None: 
        host =socket.gethostbyname(socket.gethostname())
    port = "8081"
    PORT = "8080"
    HOST = host
    port = port_entry.get()
    if port == '':
        error_label.config(text="Please fill in the valid port number")
    else:
        global peer
        peer = Peer(host, int(port), HOST, int(PORT))
        response = peer.get_info()
        peer.reset_info()
        peer.set_GUI()
        inform_label.config(text=response)
        global listen_thread
        global send_thread
        listen_thread = threading.Thread(target=peer.listen, args=())
        send_thread = threading.Thread(target=peer.send_command, args=())
        # Start both threads
        listen_thread.start()
        send_thread.start()
        # listen_thread.join()
        # send_thread.join()
        port_frame.pack_forget()
        root.geometry("400x240")
        connect_frame.pack(padx=20, pady=10)
        error_label.config(text="")
def browse_file():
    file_path = filedialog.askopenfilename()
    entry_path.delete(0, tk.END)
    entry_path.insert(0, file_path)
def publish():
    lname = entry_path.get()
    fname = entry_name.get()
    if(lname=="" or fname ==""):
        error_label.config(text="Nhập vào đầy đủ các trường thông tin")
    else:
        error_label.config(text="")
        peer.set_command(f"publish '{lname}' '{fname}'")
        while peer.wait:
            continue
        info = peer.get_info()
        peer.reset_info()
        if info!="":
            inform_label.config(text=info)
            error_label.config(text= "")
        else:
            info = peer.get_error()
            peer.reset_error()
            error_label.config(text=info)
            inform_label.config(text ="")
        entry_path.delete(0, tk.END)
        entry_name.delete(0, tk.END)
def fetch():
    fname =entry_fetch.get()
    if (fname ==""):
        error_label.config(text="Vui lòng nhập vào tên file!")
        inform_label.config(text="")
    else:
        error_label.config(text="")
        peer.set_command(f"fetch '{fname}'")
        while peer.wait:
            continue
        if peer.get_multi_peer() == True:
            info = peer.get_info()
            peer.reset_info()
            if info!="":
                inform_label.config(text=info)
        else:
            while peer.wait:
                continue
            info = peer.get_info()
            peer.reset_info()
            if info!="":
                inform_label.config(text=info+"\n Hãy vào thư mục kiểm tra")
                error_label.config(text="")
            else:
                info = peer.get_error()
                peer.reset_error()
                error_label.config(text=info)
                inform_label.config(text ="")
        if peer.get_multi_peer() == True:
            sub_frame.grid(row = 10, column=0)
            for i, item in enumerate(peer.get_list_peer()):
                label = tk.Label(sub_frame, text=item)
                label.grid(row=i+10, column=0, pady=5)
        else:    
            entry_fetch.delete(0, tk.END)
def select():
    username = entry_username.get()
    if (username==""):
        error_label.config(text="Vui lòng nhập vào username!")
    else:
        error_label.config(text="")
        peer.sender_username = username
        while peer.wait:
            continue
        info = peer.get_info()
        peer.reset_info()
        if info!="":
            inform_label.config(text=info+"\n Hãy vào thư mục kiểm tra")
            error_label.config(text="")
            entry_username.delete(0, tk.END)
            entry_fetch.delete(0, tk.END)
            sub_frame.grid_forget()
        else:
            info = peer.get_error()
            peer.reset_error()
            error_label.config(text=info)
            inform_label.config(text ="")
# Tạo cửa sổ để nhập vào port.
port_frame =tk.Frame(root, padx =5, pady =3)
port_frame.pack(padx=20,pady=5)
tk.Label(port_frame, text="Choose a port for your client to set up",font = 'arial 10 bold', fg='black').grid(row=0, columnspan=2)
tk.Label(port_frame, text="Enter your port:").grid(row=1, column=0, sticky="e",pady=5,padx=2)
port_entry = tk.Entry(port_frame)
port_entry.grid(row=1, column=1, pady=5)
port_button = tk.Button(port_frame, text="Enter", command=choosePort)
port_button.grid(row=1, column=2, padx=2, pady=5)

# Tạo frame để connect tới server.
connect_frame = tk.Frame(root, padx=5, pady=5)
tk.Label(connect_frame, text="Set up IP address and Port to connect to server",font = 'arial 10 bold', fg='black').grid(row=0, columnspan=2,pady=3)
tk.Label(connect_frame, text="Host IP:").grid(row=1, column=0, sticky="e",pady=3)
server_ip_entry = tk.Entry(connect_frame)
server_ip_entry.grid(row=1, column=1, pady=3)

tk.Label(connect_frame, text="Port:").grid(row=2, column=0, sticky="e",pady=3)
server_port_entry = tk.Entry(connect_frame)
server_port_entry.grid(row=2, column=1, pady=3)

connect_button = tk.Button(connect_frame, text="Connect", command=connect)
connect_button.grid(row=3, column=1,pady=5)

# Tạo frame cho phần login
login_frame = tk.Frame(root, padx=10, pady=10)
# login_frame.pack(padx=20, pady=20)
tk.Label(login_frame, text="Login or register an account to server",font = 'arial 10 bold', fg='black').grid(row=0, columnspan=3,pady=3)
tk.Label(login_frame, text="Username:").grid(row=1, column=0, sticky="e", padx=3,pady=3)
username_entry = tk.Entry(login_frame)
username_entry.grid(row=1, column=1,padx=3,pady=3)

tk.Label(login_frame, text="Password:").grid(row=2, column=0, sticky="e", padx=3,pady=3)
password_entry = tk.Entry(login_frame, show="*")
password_entry.grid(row=2, column=1,padx=3,pady=3)

login_button = tk.Button(login_frame, text="Login", command=login, width=10)
login_button.grid(row=1, column=3, padx=3,pady=3)
register_button = tk.Button(login_frame, text="Register", command=register, width=10)
register_button.grid(row=2, column=3,padx=3,pady=3)
tk.Label(login_frame, text="").grid(row=3, column=0, sticky="e", padx=3,pady=3)


# Tạo frame có 2 lệnh và nút cơ bản là publish và fetch
main_frame = tk.Frame(root, padx=10, pady=10)
# Publish
tk.Label(main_frame, text="Publish your file here",font = 'arial 10 bold', fg='black').grid(row=0, columnspan=3,pady=3)
tk.Label(main_frame, text="Path: ",anchor='w').grid(row=1, column=0, sticky="w")
entry_path = tk.Entry(main_frame, width=50)
entry_path.grid(row=2, column=0, padx=10, pady=10)
button_browse = tk.Button(main_frame, text="Browse", command=browse_file)
button_browse.grid(row=2, column=1, padx=10, pady=10)

tk.Label(main_frame, text="Save in your client's repository as: ",anchor='w').grid(row=3, column=0, sticky="w")
entry_name = tk.Entry(main_frame, width=50)
entry_name.grid(row=4, column=0, padx=10, pady=10)

# Tạo nút "Duyệt File"
button_publish = tk.Button(main_frame, text="Publish", command=publish)
button_publish.grid(row=4, column=1, padx=10, pady=10)

tk.Label(main_frame, text="Fetch a file here",font = 'arial 10 bold', fg='black').grid(row=5, columnspan=3,pady=5)
# Tạo fetch file
tk.Label(main_frame, text="Input file name you want to fetch",anchor='w').grid(row=6, column=0, sticky="w")
entry_fetch = tk.Entry(main_frame, width=50)
entry_fetch.grid(row=7, column=0, padx=10, pady=10)
button_fetch = tk.Button(main_frame, text="Fetch", command=fetch)
button_fetch.grid(row=7, column=1, padx=10, pady=10)
###########
sub_frame = tk.Frame(main_frame, padx=0, pady=5)

tk.Label(sub_frame, text="Select an username you want to fetch",anchor='w').grid(row=8, column=0, sticky="w")
entry_username = tk.Entry(sub_frame, width=50)
entry_username.grid(row=9, column=0, padx=10, pady=10)

button_select = tk.Button(sub_frame, text="Select", command=select)
button_select.grid(row=9, column=1, padx=10, pady=10)

# Khởi chạy vòng lặp chính của GUI
root.pack_propagate(True)
root.mainloop()
