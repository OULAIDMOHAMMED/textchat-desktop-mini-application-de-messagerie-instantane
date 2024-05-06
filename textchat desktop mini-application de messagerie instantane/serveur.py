import socket
import sqlite3
import threading
import json

usernames = []
clients = []
user_clients=[]
groupchat=[]
def create_table():
    try:
        con = sqlite3.connect(database="database.db")
        cur = con.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS database (
                username TEXT PRIMARY KEY,
                email TEXT,
                password TEXT,
                gender TEXT,
                phone_number TEXT,
                birth_date TEXT
            )
        ''')
        con.commit()
    except Exception as ex:
        print(f"Error creating table: {str(ex)}")    
def create_tablemessage():
    try:
        con = sqlite3.connect(database="database.db")
        cur = con.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Historique (
                username TEXT  ,
                message TEXT
            )
        ''')
        con.commit()
    except Exception as ex:
        print(f"Error creating table: {str(ex)}")    
def create_tablegroup():
    try:
        con = sqlite3.connect(database="database.db")
        cur = con.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS group_table (
                admin TEXT  ,
                lesmembres TEXT,
                group_name TEXT
            )
        ''')
        con.commit()
    except Exception as ex:
        print(f"Error creating table: {str(ex)}")                
create_table()
create_tablegroup()
create_tablemessage()
def handle_client(client_socket, clients):
    group_members = []
    username = None
    while True:
        try:
         operation = client_socket.recv(1024).decode("utf-8")
         AAA=operation.split(':')
         kk=operation.split(',')
         ooo=len(kk)
         if operation == "LOGIN":
            con = sqlite3.connect(database="database.db")
            cur = con.cursor()
            name = client_socket.recv(1024).decode("utf-8")
            lecode = client_socket.recv(1024).decode("utf-8")
            cur.execute("SELECT * FROM database WHERE username=? AND password=?", (name, lecode))
            row = cur.fetchone()
            if row is not None:
                response = "0"  
                usernames.append(name)
                user=name
                user_clients.append((user,client_socket))
                broadcast_message(f'{name} has joined the chat.', clients, client_socket)

            else:
                response = "1"    
            con.close() 
            client_socket.send(response.encode("utf-8"))   
         elif operation == "SIN UP":
            con = sqlite3.connect(database="database.db")
            cur = con.cursor()
            nome = client_socket.recv(1024).decode("utf-8")
            email = client_socket.recv(1024).decode("utf-8")
            code = client_socket.recv(1024).decode("utf-8")
            tol = client_socket.recv(1024).decode("utf-8")
            genre = client_socket.recv(1024).decode("utf-8")
            dtt= client_socket.recv(1024).decode("utf-8")
            cur.execute("SELECT * FROM database WHERE username=?", (nome,))
            row = cur.fetchone()
            if row is not None:
                response = "3"  
            else:
                cur.execute("INSERT INTO database (username,email, password,phone_number,gender,birth_date) VALUES (?,?,?,?,?,?)", (nome,email,code,tol,genre,dtt ))
                con.commit()
                user_reg=nome
                user_clients.append((user_reg,client_socket))
                response = "2"  # Signup successful    
            con.close()
            client_socket.send(response.encode("utf-8")) 
         elif operation=="messages": 
            con = sqlite3.connect(database="database.db")
            cur = con.cursor() 
            cur.execute('select message from Historique')
            results=cur.fetchall()
            if results:
                result = json.dumps(results)
                client_socket.send(result.encode())
            else:
                client_socket.send("Aucun message trouvé !".encode())
         elif operation == "CHANGENAME": 
            con = sqlite3.connect(database="database.db")
            cur = con.cursor()
            newname = client_socket.recv(1024).decode("utf-8")
            namee = client_socket.recv(1024).decode("utf-8")
            cur.execute("SELECT * FROM database WHERE username=?", (newname,))
            row = cur.fetchone()
            if row is not None:
                response = "5"  
            else:
                cur.execute("UPDATE database SET username = ? WHERE username = ?", (newname, namee))
                con.commit()
                response = "4"     
            con.close()
            client_socket.send(response.encode("utf-8"))

         elif operation =="actu": 
                result = json.dumps(usernames)
                listee="@" + result
                client_socket.send(listee.encode())      
         elif ooo > 1:
           kkk=kk[0]
           group_name=kkk.split(':')
           group_members = kk[1:]
           print(f"Le groupe {group_name[1]} a été créé avec les membres {group_members}")
           for membre in group_members:
            groupchat.append(membre)
           admin_username=group_name[0]
           group_namee=group_name[1] 
           members_json = json.dumps(group_members)
           con = sqlite3.connect(database="database.db")
           cur = con.cursor()
           cur.execute("INSERT INTO group_table (admin,lesmembres, group_name) VALUES (?,?,?)", (admin_username,members_json,group_namee))
           con.commit() 
         elif AAA[1].startswith("."):
          print(AAA[1])
          kkkk=AAA[1].split('.')
          msgroup=kkkk[1].split('@')
          groupchatt=msgroup[0]
          print(groupchatt)
          con = sqlite3.connect(database="database.db")
          cur = con.cursor()
          cur.execute("SELECT lesmembres FROM group_table WHERE group_name = ?", (groupchatt,))
          result = cur.fetchone()
          print(result)
          con.commit()
          members_json = result[0]
          group_member = json.loads(members_json)
          print(group_member)
          for username in group_member:
           for user, client_socket in user_clients:
            if user == username and client_socket in clients:
                message = f"{AAA[0]} (groupe: {groupchatt}): {msgroup[1]}"
                client_socket.send(message.encode("utf-8"))

         elif AAA[1].startswith("?"):        
                prv=AAA[1].split('@')
                to=prv[1].split(".")[0]
                msg_prv=prv[1].split(".")[1]
                for user in user_clients:
                    if user[0] == to: 
                        user[1].send(f"{AAA[0]}(personnel):{msg_prv}\n".encode("utf-8")) 
                    
         else:  
            con = sqlite3.connect(database="database.db")
            cur = con.cursor()
            cur.execute('insert into Historique values (?,?)',(AAA[0],operation))
            con.commit()
            con.close()        
            broadcast_message(f"{operation}",clients,client_socket)
        except Exception as e:
            client_socket.close()
            if clients:
             index=clients.index(client_socket)
             if index < len(usernames):
              username=usernames[index]
              usernames.remove(username)
              cli=user_clients[index]
              user_clients.remove(cli)
            clients.remove(client_socket)  # Retirer le client de la liste
            client_socket.close()
            break
def broadcast_message(message, clients,client_socket):
    for cmp in clients:
        if cmp is not client_socket:
            cmp.send(message.encode("utf-8"))

def start_server():
    host = '127.0.0.1'
    port = 8080

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    print(f"Server listening on {host}:{port}")

    create_table()
    create_tablegroup()

    while True:
        client_socket, client_address = server.accept()

        # Gérer le client en parallèle avec des threads
        client_handler = threading.Thread(target=handle_client, args=(client_socket, clients,))
        client_handler.start()
        clients.append(client_socket)

start_server()