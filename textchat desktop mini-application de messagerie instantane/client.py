import tkinter as tk
import threading
import socket
import time
import PIL
from PIL import Image, ImageTk
from tkinter import ttk,messagebox
from tkinter import *
from tkinter import simpledialog, scrolledtext
from tkcalendar import DateEntry
import customtkinter
import json

host = '127.0.0.1'
port = 8080
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))
def receive_messages(message_display,cleintonline):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode("utf-8")
            if message.startswith("@"):
                online=message.split('@')
                cleintonline.config(state=tk.NORMAL)
                cleintonline.insert(tk.END, f"{online[1]}est en ligne\n", "received")
                cleintonline.insert(tk.END,"\n", "received")
                cleintonline.config(state=tk.DISABLED)
            else:
                message_display.config(state=tk.NORMAL)
                message_display.insert(tk.END, f"{message}\n", "received")
                message_display.insert(tk.END,"\n", "received")
                message_display.config(state=tk.DISABLED)
        except ConnectionAbortedError:
            break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def send_message(client_socket, entry_message, name,message_display):
   try: 
    message = entry_message.get()
    if message:
        full_message = f"{name}:{message}"
        message_display.configure(state='normal')
        message_display.insert(END, "\n" + "Vous: "+ message+ "\n")
        message_display.configure(state='disabled')
        msg=f'{name}:{message}'
        client_socket.send(msg.encode())
        entry_message.delete(0, "end")
   except ConnectionAbortedError as e:
        print(f"ConnectionAbortedError: {e}") 
   except Exception as e:
        print(f"Error: {e}")         
def send_group_info(name, entryk,message_display,chattgroup):
    group_members = entryk.get().split(',')
    data_to_send = f"{','.join(group_members)}"
    print(data_to_send)
    send_message(client_socket, entryk, name,message_display)
    messagebox.showinfo("Success", "Le groupe a été créé avec succès!")
    chattgroup.destroy()

def singroup(name,message_display):
    chattgroup = tk.Tk()
    chattgroup.title("Créer un Groupe")
    chattgroup.iconbitmap("messager.ico")
    chattgroup.geometry('400x300')
    chattgroup.resizable(False,False)
    chattgroup.config(bg="linen")
    entryk = customtkinter.CTkEntry(master=chattgroup,placeholder_text="groupname,user1,user2,....",width=280,height=30,border_width=2,corner_radius=10)
    entryk.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
    
    send_button = tk.Button(chattgroup,text="VALIDER",width=8,pady=7,font="lucida 7 bold",bg='#57a1f8',border=0,command=lambda: threading.Thread(target=send_group_info, args=(name, entryk, message_display,chattgroup)).start())
    send_button.pack(pady=10)
    send_button.place(x=180,y=200)
    chattgroup.mainloop()        
def change_name_entry():
    fenetre = tk.Tk()
    fenetre.title("Modifier le nom")
    fenetre.iconbitmap("messager.ico")
    fenetre.geometry('400x300')
    entrynew_name = customtkinter.CTkEntry(master=fenetre,placeholder_text="Entrez le nouveau nom",width=280,height=30,border_width=2,corner_radius=10)
    entrynew_name.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
    entryname = customtkinter.CTkEntry(master=fenetre,placeholder_text="Veuillez entrer l'ancien nom  ",width=280,height=30,border_width=2,corner_radius=10)
    entryname.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    send_button = tk.Button(fenetre,text="VALIDER",width=8,pady=7,font="lucida 7 bold",bg='#57a1f8',border=0,command=lambda:changer())
    send_button.pack(pady=10)
    send_button.place(x=180,y=200)
    def changer():
     new_name=entrynew_name.get()
     name=entryname.get()
     try:
        client_socket.send("CHANGENAME".encode("utf-8"))
        time.sleep(0.1)
        client_socket.send(new_name.encode("utf-8"))
        time.sleep(0.1)
        client_socket.send(name.encode("utf-8"))
        response = client_socket.recv(1024).decode("utf-8")
        if response == "4":
            messagebox.showinfo("Success", "Changement de nom réussi")
        elif response == "5":
            messagebox.showerror("Error", "Changement de nom échoué")
     except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
     fenetre.destroy()    
    fenetre.mainloop()
def messagegroup(client_socket, entry_message, name,message_display,entrygr):
    try: 
     message = entry_message.get()
     groupname=entrygr.get()
     if message:
        full_message = f"{name}:.{groupname}@{message}"
        message_display.configure(state='normal')
        message_display.insert(END, "\n" + "Vous: "+ message+ "\n")
        message_display.configure(state='disabled')
        msg=f"{name}:.{groupname}@{message}"
        client_socket.send(msg.encode())
        entry_message.delete(0, "end")
        entrygr.delete(0, "end")
    except ConnectionAbortedError as e:
        print(f"ConnectionAbortedError: {e}") 
    except Exception as e:
        print(f"Error: {e}")
def messageprive(client_socket, entry_message, name,message_display,entrypr):
    try: 
     message = entry_message.get()
     prname=entrypr.get()
     if message:
        message_display.configure(state='normal')
        message_display.insert(END, "\n" + "Vous: "+ message+ "\n")
        message_display.configure(state='disabled')
        msg=f"{name}:?@{prname}.{message}"
        client_socket.send(msg.encode())
        entry_message.delete(0, "end")
        entrypr.delete(0, "end")
    except ConnectionAbortedError as e:
        print(f"ConnectionAbortedError: {e}") 
    except Exception as e:
        print(f"Error: {e}")        

def chat(name):

    chatt = tk.Tk()
    chatt.title("Salon de Discussion")
    chatt.geometry('520x500')
    chatt.iconbitmap("messager.ico")
    chatt.resizable(False, False)
    chatt.config(bg="linen")

    message_display = scrolledtext.ScrolledText(chatt, wrap=tk.WORD, width=40, height=20, state=tk.DISABLED)
    message_display.tag_config("received", foreground="green")
    message_display.pack(padx=10, pady=10)
    message_display.place(x=10, y=90)

    cleintonline = scrolledtext.ScrolledText(chatt, wrap=tk.WORD, width=60, height=5, state=tk.DISABLED)
    cleintonline.tag_config("received", foreground="green")
    cleintonline.place(x=10, y=5)

    entry = customtkinter.CTkEntry(master=chatt, placeholder_text="send message", width=280, height=30,
                                    border_width=2, corner_radius=10)
    entry.place(relx=0.3, rely=0.9, anchor=tk.CENTER)
    entrygr = customtkinter.CTkEntry(master=chatt, placeholder_text="group name", width=90, height=30,
                                    border_width=2, corner_radius=10)
    entrygr.place(relx=0.9, rely=0.8, anchor=tk.CENTER)
    entrypr = customtkinter.CTkEntry(master=chatt, placeholder_text="name", width=90, height=30,
                                    border_width=2, corner_radius=10)
    entrypr.place(relx=0.9, rely=0.9, anchor=tk.CENTER)

    send_button = tk.Button(chatt, text="Send", width=5, pady=7, font="lucida 7 bold", bg='#57a1f8', border=0,
                            command=lambda: threading.Thread(target=send_message, args=(client_socket, entry, name, message_display)).start())
    send_button.pack(pady=10)
    send_button.place(x=305, y=436)
    send_button = tk.Button(chatt, text="Send group", width=10, pady=7, font="lucida 7 bold", bg='#57a1f8', border=0,
                            command=lambda: threading.Thread(target=messagegroup, args=(client_socket, entry, name, message_display, entrygr)).start())
    send_button.pack(pady=10)
    send_button.place(x=355, y=385)
    send_button = tk.Button(chatt, text="Send prive", width=10, pady=7, font="lucida 7 bold", bg='#57a1f8', border=0,
                            command=lambda: threading.Thread(target=messageprive, args=(client_socket, entry, name, message_display, entrypr)).start())
    send_button.pack(pady=10)
    send_button.place(x=355, y=436)

    def onlinecleint():
        operation = "actu"
        client_socket.send(operation.encode("utf-8"))
    def historique():
        operation = "messages"
        client_socket.send(operation.encode("utf-8"))
    tk.Label(chatt, text="cleint online:", font="lucida 7 bold", bg='linen').place(x=350, y=100)
    actuilise = tk.Button(chatt, text="Historique", width=8, pady=7, font="lucida 7 bold", bg='#57a1f8', border=0,
                          fg='white', command=lambda: threading.Thread(target=historique).start())
    actuilise.pack(pady=10)
    actuilise.place(x=370, y=190)
    online = tk.Button(chatt, text="statut", width=8, pady=7, font="lucida 7 bold", bg='#57a1f8', border=0,
                          fg='white', command= lambda:threading.Thread(target=onlinecleint).start())
    online.pack(pady=10)
    online.place(x=370, y=120)

    def Deconnecter():
     client_socket.close()
     chatt.destroy()

    quitte = tk.Button(chatt, text="Déconnecter", width=9, pady=7, font="lucida 7 bold", bg='#57a1f8', border=0, fg='white',
                       command=lambda:Deconnecter())
    quitte.pack(pady=10)
    quitte.place(x=370, y=250)

    creergroup = tk.Button(chatt, text="créer un groupe", width=12, pady=7, font="lucida 7 bold", bg='#57a1f8', border=0,
                           fg='white', command=lambda: threading.Thread(target=singroup, args=(name, message_display)).start())
    creergroup.pack(pady=10)
    creergroup.place(x=370, y=300)

    receive_thread = threading.Thread(target=lambda: receive_messages(message_display,cleintonline))
    receive_thread.start()
    chatt.mainloop()
   
def login():
    operation="LOGIN"
    if pathname.get() == "" or pathpass.get() == "":
        messagebox.showerror("Error", "Veuillez saisir le nom d'utilisateur et le mot de passe")
    else:
        name = pathname.get()
        lecode = pathpass.get()
        try:
            client_socket.send(operation.encode("utf-8"))
            time.sleep(0.1)
            client_socket.send(name.encode("utf-8"))
            time.sleep(0.1)
            client_socket.send(lecode.encode("utf-8"))
            response = client_socket.recv(1024).decode("utf-8")
            if response == "0":
                messagebox.showinfo("Success", "Authentification réussie. Bienvenue !")
                root.destroy()
                chat(name)
            elif response=="1":
                messagebox.showerror("Error", "Échec de l'authentification. Veuillez vérifier vos informations.")           
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


root= Tk()
root.geometry("900x600")
root.title("authentification")
root.iconbitmap("messager.ico")
#root.resizable(FALSE,FALSE)
img =PhotoImage(file='fste.png')
Label(root,image=img,bg='WHITE').place(x=50,y=50)
pathname =tk.Entry(root,font="lucida 12 bold",width=25,fg='black',border=0,bg='white')
pathname.place(x=560,y=200)

Frame(root,width=280,height=2,bg='black').place(x=560,y=225)

tk.Label(root,text="password:",font="lucida 15 bold",bg='white').place(x=420,y=270)
tk.Label(root,text="username:",font="lucida 15 bold",bg='white').place(x=420,y=205)

pathpass =tk.Entry(root,font="lucida 10 bold",border=0)
pathpass.place(x=560,y=270)
Frame(root,width=280,height=2,bg='black').place(x=560,y=295)
sumbit=tk.Button(root,text="Login",width=25,pady=7,font="lucida 7 bold",bg='#57a1f8',border=0,fg='white',command=lambda:login())
sumbit.place(x=620,y=330)
tk.Label(root,text="Modify username:",fg='black',font="lucida 10 bold",bg='white').place(x=520,y=430)
tk.Label(root,text="Don't have an account?",fg='black',font="lucida 10 bold",bg='white').place(x=500,y=400)

def ouvrir_fichier():
   def creer():
    operation="SIN UP"
    if e_nome.get() == "" or e_email.get() == "" or e_motdepasse.get() == "" or e_tel.get() == "":
        messagebox.showerror("Erreur", "Veuillez remplir tous les champs d'informations", parent=formule)
    else:
        name=e_nome.get()
        emaill=e_email.get()
        lecode=e_motdepasse.get()
        tell=e_tel.get()
        sexee=e_sexe.get()
        datee=e_date.get()
        try:
            client_socket.send(operation.encode("utf-8"))
            time.sleep(0.1)
            client_socket.send(name.encode("utf-8"))
            time.sleep(0.1)
            client_socket.send(emaill.encode("utf-8"))
            time.sleep(0.1)
            client_socket.send(lecode.encode("utf-8"))
            time.sleep(0.1)
            client_socket.send(tell.encode("utf-8"))
            time.sleep(0.1)
            client_socket.send(sexee.encode("utf-8"))
            time.sleep(0.1)
            client_socket.send(datee.encode("utf-8"))
            time.sleep(0.1)
            response = client_socket.recv(1024).decode("utf-8")
            if response == "2":
                messagebox.showinfo("Success", "Inscription réussie. Vos informations ont été enregistrées.")
            elif response=="3":
                messagebox.showerror("Error", "L'inscription a échoué. Le nom d'utilisateur existe déjà. Veuillez réessayer avec un autre nom.")  
            formule.destroy()             
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
   formule = Tk()
   formule.title('Création de Compte')
   formule.geometry('500x400')
   formule.iconbitmap("messager.ico")
   formule.config(bg="linen")

   motdepass = Label(formule, text="mot de passe:", bg='linen')
   nome = Label(formule, text="NOM:", bg='linen')
   email = Label(formule, text="Email :", bg='linen')
   tel = Label(formule, text="Téléphone :", bg='linen')
   sexe = Label(formule, text="sexe:", bg='linen')
   date = Label(formule, text="Date de naissance :", bg='linen')

   e_motdepasse = customtkinter.CTkEntry(master=formule,placeholder_text="Mot de passe",width=280,height=30,border_width=2,corner_radius=10)
   e_nome = customtkinter.CTkEntry(master=formule,placeholder_text="Nom d'utilisateur",width=280,height=30,border_width=2,corner_radius=10)
   e_email = customtkinter.CTkEntry(master=formule,placeholder_text="Adresse e-mail",width=280,height=30,border_width=2,corner_radius=10)
   e_tel = customtkinter.CTkEntry(master=formule,placeholder_text="Numéro de téléphone",width=280,height=30,border_width=2,corner_radius=10)
   e_sexe = ttk.Combobox(formule, width=29, state="readonly",font=('Arial', 12))
   e_sexe['values'] = ['Homme', 'Femme']
   e_sexe.set('Homme')
   e_date = DateEntry(formule, width=29, date_pattern="dd/mm/yyyy",font=('Arial', 12))

   motdepass.grid(row=8, column=0, padx=15, pady=20)
   e_motdepasse.grid(row=8, column=1)

   nome.grid(row=3, column=0, padx=15, pady=20)
   e_nome.grid(row=3, column=1, padx=15)

   email.grid(row=4, column=0, padx=15, pady=20)
   e_email.grid(row=4, column=1, padx=15)

   tel.grid(row=5, column=0, padx=15, pady=20)
   e_tel.grid(row=5, column=1, padx=15)

   sexe.grid(row=6, column=0, padx=15, pady=20)
   e_sexe.grid(row=6, column=1, padx=15)

   date.grid(row=7, column=0, padx=10, pady=20)
   e_date.grid(row=7, column=1, padx=15)

   save = Button(formule, text="SAVE",bg='#57a1f8',border=0,fg='white', width=30,command=creer)  # Corrected the button text
   save.grid(row=9, column=1, columnspan=2)
   formule.mainloop()

sumbit=tk.Button(root,text="Sign Up",width=25,pady=7,font="lucida 7 bold",bg='#57a1f8',cursor='hand2',border=0,fg='white',command=ouvrir_fichier)
sumbit.place(x=700,y=390)
sumbit=tk.Button(root,text="Update Name",width=25,pady=7,font="lucida 7 bold",bg='#57a1f8',cursor='hand2',border=0,fg='white',command=lambda:change_name_entry())
sumbit.place(x=700,y=430)

root.mainloop()