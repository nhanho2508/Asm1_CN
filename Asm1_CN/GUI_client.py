import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from server.server import *
from peer.peer import *
import psutil
import subprocess
import socket
from tkinter import scrolledtext
import os

# Tạo cửa sổ chính

peer = None
root = tk.Tk()
root.title("Simple file-sharing application")
lbl =Label(root, text = "CLIENT INTERFACE", font = 'arial 15 bold', fg='black')
lbl.pack(side="top", pady=3)
lbl2 =Label(root, text = "", font = 'arial 10 bold', fg='blue')
lbl2.pack(side="top", pady=1)
root.geometry("500x500")
root.resizable(False,False)

frame = tk.Frame(root, bg="white", bd=2, relief="solid", width=200, height=50)
frame.pack(side="bottom", fill="both", expand=True, padx=3, pady=3)

# Tạo label bên trong khung
inform_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD,height=7)
inform_text.insert(tk.END, "WELCOME TO OUR APPLICATION\n")
inform_text.pack(fill="both", expand=True)
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
        peer.command_line = f"register {username} {password}"
        time.sleep(1)
        if peer.is_online ==  1:
            # Đăng nhập thành công, ẩn phần login
            lbl2.config(text=f"Welcome to our app, {username}!", fg="blue")
            login_frame.pack_forget()
            error_label.config(text="")
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            root.geometry("800x620")
            main_frame.pack()
def login():
    username = username_entry.get()
    password = password_entry.get()
    if(username=="" or password==""):
        error_label.config(text="Nhập vào đầy đủ các trường thông tin!")
    else:
        error_label.config(text="")
        peer.command_line = f"login {username} {password}"
        # Kiểm tra thông tin đăng nhập, ở đây là một ví dụ đơn giản
        time.sleep(1)
        if peer.is_online ==  1:
            # Đăng nhập thành công, ẩn phần login
            lbl2.config(text=f"Welcome back, {username}!", fg="blue")
            login_frame.pack_forget()
            error_label.config(text="")
            username_entry.delete(0, tk.END)
            password_entry.delete(0,tk.END)
            root.geometry("800x620")
            main_frame.pack()
def connect():
    server_ip = server_ip_entry.get()
    server_port = server_port_entry.get()
    if(server_ip=="" or server_port ==""):
        error_label.config(text="Vui lòng không bỏ sót trường thông tin!")
    else:
        error_label.config(text="")
        peer.command_line = f"connect {server_ip} {server_port}"
        time.sleep(1)
        if peer.is_connect:
            connect_frame.pack_forget()
            server_ip_entry.delete(0,tk.END)
            server_port_entry.delete(0,tk.END)
            login_frame.pack(padx=5,pady=5) 

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
        peer.command_line=f'publish "{lname}" "{fname}"'
        time.sleep(1)
        if peer.is_replace:
            peer.is_replace = False
            sub_frame2.grid(column=0, columnspan=3)
            error_label.config(text= "")
        else:
            entry_path.delete(0, tk.END)
            entry_name.delete(0, tk.END)
def replaceYes():
    peer.action = "R"
    sub_frame2.grid_forget()
def replaceNo():
    peer.action = "C"
    sub_frame2.grid_forget()
def replaceYes3():
    peer.action = "R"
    sub_frame3.grid_forget()
    time.sleep(1)
    if peer.is_multi_peer:
        peer.is_multi_peer = False
        sub_frame.grid(column=0, columnspan=3)
    else:
        entry_fetch.delete(0, tk.END)
        entry_name_store.delete(0, tk.END)
def replaceNo3():
    peer.action = "C"
    sub_frame3.grid_forget()
def fetch():
    fname = entry_fetch.get()
    sname = entry_name_store.get()
    if (fname ==""):
        error_label.config(text="Vui lòng nhập vào tên file!")
    else:
        error_label.config(text="")
        if(sname == ""):
            peer.command_line = f"fetch '{fname}'"
        else: 
            peer.command_line = f"fetch '{fname}' {sname}"
        time.sleep(1)
        if peer.is_replace:
            peer.is_replace = False
            sub_frame3.grid(column=0, columnspan=3)
        elif peer.is_multi_peer:
            peer.is_multi_peer = False
            sub_frame.grid(column=0, columnspan=3)    
        else:
            entry_fetch.delete(0, tk.END)
            entry_name_store.delete(0, tk.END)

def select():
    username = entry_username.get()
    if (username==""):
        error_label.config(text="Vui lòng nhập vào username!")
    else:
        error_label.config(text="")
        peer.sender_username = username
        time.sleep(1)
        if peer.select_peer:
            peer.select_peer = False
            error_label.config(text="")
            entry_username.delete(0, tk.END)
            entry_fetch.delete(0,tk.END)
            entry_name_store.delete(0, tk.END)
            sub_frame.grid_forget()
def search():
    fname = entry_search.get()
    if (fname == ""):
        error_label.config(text="Vui lòng nhập vào tên file!")
    else:
        error_label.config(text="")
        peer.command_line=f"search '{fname}'"
def View():
    peer.command_line = f"view"
def Delete():
    fname = entry_delete.get()
    if fname == "":
        error_label.config(text="Vui lòng nhập vào tên file!")
    else:
        error_label.config(text="")
        peer.command_line=f"delete '{fname}'"
def LogOut():
    inform_text.delete(3.0, tk.END)
    inform_text.insert(tk.END, "\n")
    entry_delete.delete(0, tk.END)
    entry_search.delete(0,tk.END)
    peer.command_line = f"logout"
    main_frame.pack_forget()
    lbl2.config(text="")
    login_frame.pack(padx=5,pady=5) 
    root.geometry("500x500")
def Disconnect():
    inform_text.delete(2.0, tk.END)
    inform_text.insert(tk.END, "\n")
    entry_delete.delete(0, tk.END)
    entry_search.delete(0,tk.END)
    peer.command_line = f"disconnect"
    main_frame.pack_forget()
    lbl2.config(text="")
    root.geometry("500x500")
    connect_frame.pack()
def disconnect2():
    inform_text.delete(2.0, tk.END)
    inform_text.insert(tk.END, "\n")
    entry_delete.delete(0, tk.END)
    entry_search.delete(0,tk.END)
    peer.command_line = f"disconnect"
    login_frame.pack_forget()
    lbl2.config(text="")
    root.geometry("500x500")
    connect_frame.pack()
def changepass():
    sub_frame4.grid(column=0, columnspan=3)

def submitchangePassword():
    old = entry_old.get()
    new = entry_new.get()
    if (old == "" or new == ""):
        if (old =="") and new =="": sub_frame4.grid_forget()
        error_label.config(text="Vui lòng nhập đầy đủ các trường")
    else:
        error_label.config(text="")
        peer.command_line =f"change_password '{old}' '{new}'"
        time.sleep(1)
        if peer.ischange_password:
            peer.ischange_password = False
            entry_old.delete(0, tk.END)
            entry_new.delete(0, tk.END)
            sub_frame4.grid_forget()

def catch_event():
    while True:
        if(peer.info_renew):
            inform_text.insert(tk.END, peer.info+"\n")
            peer.info_renew = False
        if(peer.error_renew):
            error_label.config(text=peer.error)
            peer.error_renew = False
        time.sleep(0.05)
def start_client():
    host = get_wifi_ip_address()
    if host is None: 
        host =socket.gethostbyname(socket.gethostname())
    port = "8081"
    PORT = "8080"
    HOST = host
    global peer
    peer = Peer(host, int(port), HOST, int(PORT))
    peer.is_GUI = True
    send_thread = threading.Thread(target=peer.send_command, args=())
    # Start both threads
    send_thread.start()
    connect_frame.pack()
    info = peer.info
    inform_text.insert(tk.END, info+"\n")

    catch_event_thread = threading.Thread(target=catch_event, args=())
    catch_event_thread.start()
    # listen_thread.join()
    # send_thread.join()
# Tạo cửa sổ để nhập vào port.

def on_closing():
    if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát?"):
        root.destroy()
        pid = os.getpid()
        subprocess.run(["taskkill", "/F", "/PID", str(pid)])

# Tạo frame để connect tới server.
connect_frame = tk.Frame(root, padx=5, pady=2)
tk.Label(connect_frame, text="Set up Server's IP address and Port to connect to server",font = 'arial 10 bold', fg='black').grid(row=0, columnspan=2,pady=2)
tk.Label(connect_frame, text="Server's IP:").grid(row=1, column=0, sticky="e",pady=2)
server_ip_entry = tk.Entry(connect_frame)
server_ip_entry.grid(row=1, column=1, pady=2)

tk.Label(connect_frame, text="Server's Port:").grid(row=2, column=0, sticky="e",pady=2)
server_port_entry = tk.Entry(connect_frame)
server_port_entry.grid(row=2, column=1, pady=2)

connect_button = tk.Button(connect_frame, text="Connect", command=connect, bg="forestgreen", fg="white")
connect_button.grid(row=3, column=1,pady=2)
connect_frame.pack(padx=20, pady=2)
# Tạo frame cho phần login
login_frame = tk.Frame(root, padx=10, pady=2)
# login_frame.pack(padx=20, pady=20)
tk.Label(login_frame, text="Login or register an account to server",font = 'arial 10 bold', fg='black').grid(row=0, columnspan=3,pady=2)
tk.Label(login_frame, text="Username:").grid(row=1, column=0, sticky="e", padx=3,pady=2)
username_entry = tk.Entry(login_frame)
username_entry.grid(row=1, column=1,padx=3,pady=2)

tk.Label(login_frame, text="Password:").grid(row=2, column=0, sticky="e", padx=3,pady=2)
password_entry = tk.Entry(login_frame, show="*")
password_entry.grid(row=2, column=1,padx=3,pady=2)

login_button = tk.Button(login_frame, text="Login", command=login, width=10, bg="gainsboro", fg="black")
login_button.grid(row=1, column=2, padx=3,pady=2)
register_button = tk.Button(login_frame, text="Register", command=register, width=10, bg="darkslateblue", fg="white")
register_button.grid(row=2, column=2,padx=3,pady=2)
tk.Label(login_frame, text="Disconnect to connect another server?").grid(row=3, column=0, sticky="e", padx=3,pady=2,columnspan=2)
disconnect_button = tk.Button(login_frame, text="Disconnect", command=disconnect2, width=10, bg="brown3")
disconnect_button.grid(row=3, column=2,padx=3,pady=2)


# Tạo frame có 2 lệnh và nút cơ bản là publish và fetch
main_frame = tk.Frame(root, padx=10, pady=5)
# -----------------------------------Publish ----------------------
#--------------------------------------------------------------------
tk.Label(main_frame, text="Publish your file here",font = 'arial 10 bold', fg='black').grid(row=0, columnspan=3,pady=2)
tk.Label(main_frame, text="Path: ",anchor='w').grid(row=1, column=0, sticky="w")
entry_path = tk.Entry(main_frame, width=50)
entry_path.grid(row=1, column=1, padx=10, pady=2)
button_browse = tk.Button(main_frame, text="Browse", command=browse_file, bg="goldenrod3", fg="black")
button_browse.grid(row=1, column=2, padx=10, pady=2)

tk.Label(main_frame, text="Save in your client's repository as: ",anchor='w').grid(row=2, column=0, sticky="w")
entry_name = tk.Entry(main_frame, width=50)
entry_name.grid(row=2, column=1, padx=10, pady=2)

# Tạo nút "Publish File"
button_publish = tk.Button(main_frame, text="Publish", command=publish, bg="darkslateblue", fg="white")
button_publish.grid(row=2, column=2, padx=10, pady=2)

sub_frame2 = tk.Frame(main_frame, padx=0, pady=2)
tk.Label(sub_frame2, text="Replace the original file?",anchor='w',font='arial 8 bold').grid(row=3, column=0, sticky="w")
button_yes = tk.Button(sub_frame2, text="Yes", command=replaceYes, fg="green3")
button_yes.grid(row=3, column=1, padx=10, pady=2)
button_no = tk.Button(sub_frame2, text="No", command=replaceNo, fg="brown3")
button_no.grid(row=3, column=2, padx=10, pady=2)
#-----------------------------SEARCH --------------------------------
# -----------------------------------------------------------
tk.Label(main_frame, text="Search a file here",font = 'arial 10 bold', fg='black').grid(row=4, columnspan=3,pady=2)
# search file
tk.Label(main_frame, text="Input file name you want to search",anchor='w').grid(row=5, column=0, sticky="w")
entry_search = tk.Entry(main_frame, width=50)
entry_search.grid(row=5, column=1, padx=10, pady=2)
button_search = tk.Button(main_frame, text="Search", command=search, bg="darkslateblue", fg="white")
button_search.grid(row=5, column=2, padx=10, pady=2)
# -----------------------------FETCH----------------------------
tk.Label(main_frame, text="Fetch a file here",font = 'arial 10 bold', fg='black').grid(row=6, columnspan=3,pady=2)
# Tạo fetch file
tk.Label(main_frame, text="Input file name you want to fetch",anchor='w').grid(row=7, column=0, sticky="w")
entry_fetch = tk.Entry(main_frame, width=50)
entry_fetch.grid(row=7, column=1, padx=10, pady=2)
tk.Label(main_frame, text="Store in your repository as name: ",anchor='w').grid(row=8, column=0, sticky="w")
entry_name_store = tk.Entry(main_frame, width=50)
entry_name_store.grid(row=8, column=1, padx=10, pady=2)
button_fetch = tk.Button(main_frame, text="Fetch", command=fetch, bg="darkslateblue", fg="white")
button_fetch.grid(row=7, column=2, padx=10, pady=2, rowspan= 2 )
###########
# - Handle trùng tên file
sub_frame3 = tk.Frame(main_frame, padx=0, pady=2)
tk.Label(sub_frame3, text="Replace the original file?",anchor='w',font='arial 8 bold').grid(row=8, column=0, sticky="w")
button_yes3 = tk.Button(sub_frame3, text="Yes", command=replaceYes3, fg="green3")
button_yes3.grid(row=8, column=1, padx=10, pady=2)
button_no3 = tk.Button(sub_frame3, text="No", command=replaceNo3, fg="brown3")
button_no3.grid(row=8, column=2, padx=10, pady=2)
# -- Multi peer to fetch
sub_frame = tk.Frame(main_frame, padx=0, pady=2)
tk.Label(sub_frame, text="Select an username you want to fetch:",anchor='w', font='arial 8 bold').grid(row=9, column=0, sticky="w")
entry_username = tk.Entry(sub_frame, width=50)
entry_username.grid(row=9, column=1, padx=10, pady=2)

button_select = tk.Button(sub_frame, text="Select", command=select, bg="forestgreen", fg="white")
button_select.grid(row=9, column=2, padx=10, pady=2)


#-------------------------- View ----------------------------
# -----------------------------------------------------------
tk.Label(main_frame, text="View all files in your publish repository",anchor='w').grid(row=10, column=0, sticky="w")
button_view = tk.Button(main_frame, text="View", command=View, bg="goldenrod3", fg="black")
button_view.grid(row=10, column=1, padx=10, pady=2)

# ---------------------------Delete ---------------------------
# -------------------------------------------------------------
tk.Label(main_frame, text="Delete a file here",font = 'arial 10 bold', fg='black').grid(row=11, columnspan=3,pady=2)
tk.Label(main_frame, text="Input file name you want to delete in your publish repository",anchor='w').grid(row=12, column=0, sticky="w")
entry_delete = tk.Entry(main_frame, width=50)
entry_delete.grid(row=12, column=1, padx=10, pady=2)
button_delete = tk.Button(main_frame, text="Delete", command=Delete, bg="darkslateblue", fg="white")
button_delete.grid(row=12, column=2, padx=10, pady=2)
# -------------------------- 3 Button --------------------------
# ----------------------------------------------------------------
button_changepass = tk.Button(main_frame, text="Change Your Password", command=changepass, bg="white", fg="black")
button_changepass.grid(row=13, column=0, padx=10, pady=2)
button_logout = tk.Button(main_frame, text="Log Out", command=LogOut, bg="gray30", fg="white")
button_logout.grid(row=13, column=2, padx=10, pady=2)
button_disconnect = tk.Button(main_frame, text="Disconnect from Server", command=Disconnect, bg="brown", fg="white" )
button_disconnect.grid(row=13, column=1, padx=10, pady=2)
##Subframe for change pass word
sub_frame4 = tk.Frame(main_frame, padx=0, pady=5)
tk.Label(sub_frame4, text="Change your password here",font = 'arial 10 bold', fg='black').grid(row=18, columnspan=3,pady=2)
tk.Label(sub_frame4, text="Old password: ",anchor='w').grid(row=19, column=0, sticky="w")
entry_old = tk.Entry(sub_frame4, width=50,show="*")
entry_old.grid(row=19, column=1, padx=10, pady=2)
tk.Label(sub_frame4, text="New password: ",anchor='w').grid(row=20, column=0, sticky="w")
entry_new = tk.Entry(sub_frame4, width=50, show="*")
entry_new.grid(row=20, column=1, padx=10, pady=2)
# Tạo nút "submit change password"
button_submit_change = tk.Button(sub_frame4, text="Submit Change", command=submitchangePassword, bg="forestgreen", fg="white")
button_submit_change.grid(row=19, column=2, padx=10, pady=2, rowspan=2)



root.protocol("WM_DELETE_WINDOW", on_closing)
root.after(100, start_client)
# Khởi chạy vòng lặp chính của GUI
root.pack_propagate(True)
root.mainloop()
