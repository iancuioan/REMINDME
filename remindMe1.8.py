#!/usr/bin/python3
# -*- coding: utf-8 -*-
from tkinter import *
#import tkinter.ttk as ttk
from tkinter import messagebox
from tkcalendar import Calendar, DateEntry
from datetime import datetime,date
from tkinter import scrolledtext
import os, csv, sys
import pickle
import webbrowser
import time
import threading
#from plyer import notification
from notifypy import Notify
import pywhatkit as pwk
import pyautogui
from pynput.keyboard import Key, Controller
# moon icon = https://icons8.com/icon/33207/moon-and-stars

'''====== Tkinter default icon replaced ======='''
import tempfile
ICON = (b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00'
    b'\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00'
    b'\x08\x00\x00\x00\x00\x00@\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x01\x00\x00\x00\x01') + b'\x00'*1282 + b'\xff'*64
_, ICON_PATH = tempfile.mkstemp()
with open(ICON_PATH, 'wb') as icon_file:
    icon_file.write(ICON)
'''============================================'''

'''===== Display setings ======================'''
basedir = os.path.dirname(__file__)
try:
    from ctypes import windll  # Only exists on Windows.
    windll.shcore.SetProcessDpiAwareness(1)
    myappid = "remindMe.1.8"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    print('Error importing...')
    pass
'''============================================'''

root = Tk()

'''========Globals et path====================='''
azi = datetime.now()
notes = []
copyright = u"\u00A9"
note_counter = 0
######### os setup ############
mydir = 'RemindMe'# Store dir
mypath = os.getcwd()+'\\'+ mydir
isExist = os.path.exists(mypath)

if not isExist:
    try:
        os.mkdir(mypath)
    except FileExistsError:
        pass

def nzdif(b): 
    azi=datetime.now()
    return (azi - b).days

if not os.path.exists(mypath+'\\'+"reminder.csv"):# store file
    with open(mypath+'\\'+'reminder.csv', 'w') as f:
        f.write('')
if not os.path.exists(mypath+'\\'+"Archived.txt"):# arhived notes
        with open(mypath+'\\'+'Archived.txt', 'w') as f:
            f.write('')
def read_from_file():
    global notes
    with open(mypath+'\\'+'reminder.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            if row != '':
                notes.append(row)
        notes.sort()   
        
def write_to_file():
    global notes
    with open(mypath+'\\''reminder.csv', 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerows(sorted(notes))
    return f
'''============================================'''


'''==== Alerts functions ======================'''
def wake_up_pc():
    pyautogui.FAILSAFE = False
    for i in range(0, 5):
        pyautogui.press('shift')
    

def send_email(subject, to_email,password, message):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    password = password # 
    my_email = to_email #
    smtp_obj = smtplib.SMTP('smtp.mail.yahoo.com', 587)
    smtp_obj.starttls()
    smtp_obj.ehlo()
    smtp_obj.login(my_email, password)
    msg = MIMEMultipart()
    msg['From'] = my_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    smtp_obj.sendmail(msg['From'], msg['To'], msg.as_string())
    smtp_obj.quit()
    return True

def send_notification(stop_event):
    
    def job():
        global azi
        wake_up_pc()
        this_day = datetime.now().day
        if this_day != azi.day:
            azi = datetime.now()
            refresh()
            day_label.configure(text='')
            day_label.configure(text = str(azi)[ :11])
            if os.path.exists(mypath+'\\'+"email_password.dat") and \
                      len(message_area.get('1.0', 'end')) > 1:
                user_email_and_pwd = pickle.load(open(mypath+'\\'+
                                        "email_password.dat", "rb"))
                try:
                    send_email('remindMe - Alerts', user_email_and_pwd[0],
                       user_email_and_pwd[1],message_area.get('1.0', 'end') )
                except:
                    messagebox_showinfo('','Email failed')
            if os.path.exists(mypath+'\\'+"phone.dat") and \
                      len(message_area.get('1.0', 'end')) > 1:
                user_phone = pickle.load(open(mypath+'\\'+
                                        "phone.dat", "rb"))
                try:
                    send_whatsapp_message('+40'+user_phone,
                                message_area.get('1.0', 'end'))
                except:
                    messagebox_showinfo('','Whatsapp message failed')
            if len(message_area.get(1.0,END)) > 1:
                notification = Notify()
                notification.title = "Alerts"
                notification.message = "Notifications from remindMe."
                notification.icon = ICON_PATH
                notification.send()
                
    while not stop_event.is_set():
        job()
        time.sleep(60*20)


def send_whatsapp_message(phoneNumber,msg):    
    try:
        pwk.sendwhatmsg_instantly(phoneNumber, msg)
        time.sleep(30)
        pyautogui.press('enter')
        pyautogui.press('enter')
        time.sleep(80)
        pyautogui.press('enter')
    except Exception as e:
        pass
'''============================================'''        


#================================================================ 
#============= Set Password Frame ===============================
def set_password():
    def save_password():
        user_pwd = password_entry.get()
        if user_pwd != '':
            pickle.dump(user_pwd, open(mypath+'\\'+"password.dat", "wb"))# store in pickle
            password_frame.forget()
            set_password_button.place_forget()
            frame1.pack(side = "top", expand = True, fill = "both")
            user_pwd = pickle.load(open(mypath+'\\'+"password.dat", "rb"))
            messagebox.showinfo('', 'Your password was set.')
            hide_screen_btn.place(x = 400, y = 560)
        else:
            messagebox.showinfo('', 'Empty field.')

    def back():
        password_frame.forget()
        frame1.pack(side = "top", expand = True, fill = "both")

    password_frame = Frame(root, bg= 'light yellow')#'#B5E5CF')
    go_back_button = Button(password_frame, width=24, cursor="hand2",
                text = "Cancel", bg='#45b592',
                font = ("arial", "12"),fg='white', command = back)
    go_back_button.pack(side= TOP, pady=15)
    
    password_label = Label(password_frame, bg= 'light yellow', fg='brown',
        text = 'Set your password', font = ("arial", "18"))
    password_label.pack(side= TOP, pady=35)
    
    password_entry = Entry(password_frame,
        font = ("arial", "18"),width=30)
    password_entry.pack(side= TOP, pady=35, padx=10)
    password_entry.focus_set()
    
    password_button = Button(password_frame, width=10, text = 'Save',
        font = ("arial", "12"), cursor="hand2", command = save_password)
    password_button.pack()
    frame1.forget()    
    password_frame.pack(side = "top", expand = True, fill = "both")

#=============================================================== 
#============= Set Whatsup Frame ===============================
def set_whatsapp_alerts():
    code = str(datetime.now())[-6: ]
    
    def get_phone_number():
        if phone_entry.get() != '' and len(phone_entry.get())==10 \
           and phone_entry.get().isdigit():            
            send_whatsapp_message('+40'+phone_entry.get(),code)
            Controller().press(Key.enter)
            Controller().release(Key.enter)
            time.sleep(3)
            Controller().press(Key.enter)
            Controller().release(Key.enter)
            time.sleep(3)
            phone_label.pack_forget()
            phone_entry.pack_forget()
            phone_button.pack_forget()
            check_code_label.pack()
            check_code_entry.pack()
            save_phone_button.pack()
        else:
            messagebox.showinfo('', '10 digits please.')
            
    def save_phone_number():
        if check_code_entry.get() == code:
            pickle.dump(phone_entry.get(), open(mypath+'\\'+"phone.dat", "wb"))# store in pickle
            whatsapp_frame.forget()
            frame1.pack(side = "top", expand = True, fill = "both")
            set_whatsapp_button.config(text='Stop whatsapp alerts',
                                       command=stop_whatsapp_alerts)
            send_whatsapp_btn.place(x = 620, y = 10)
            user_phone = pickle.load(open(mypath+'\\'+"phone.dat", "rb"))
            messagebox.showinfo('', 'Your whatsapp alerts was set.\
             Whatsapp alerts will be sent daily after midnight\
             while app is running')
        else:
            messagebox.showinfo('', 'Incorrect code. Check your\
                   internet connection.')
        
    
    def back():
        whatsapp_frame.forget()
        frame1.pack(side = "top", expand = True, fill = "both")

    whatsapp_frame = Frame(root, bg= 'light yellow')
    
    go_back_button = Button(whatsapp_frame, width=24, cursor="hand2",
                text = "Cancel.", bg='#45b592',
                font = ("arial", "12"),fg='white', command = back)
    go_back_button.pack(side= TOP, pady=15)
    
    phone_label = Label(whatsapp_frame, bg= 'light yellow', fg='brown',
        text = 'Your phone number 10 digits', font = ("arial", "18"))
    phone_label.pack(side= TOP, pady=35)
    
    phone_entry = Entry(whatsapp_frame,
        font = ("arial", "18"),width=30)
    phone_entry.pack(side= TOP, pady=35, padx=10)
    phone_entry.focus_set()

    phone_button = Button(whatsapp_frame,width=10, text = 'Verify',
        font = ("arial", "12"), cursor="hand2", command = get_phone_number)
    phone_button.pack()
    check_code_label = Label(whatsapp_frame, bg= 'light yellow', fg='brown',
        text = 'Enter code recieved on your whatsup', font = ("arial", "18"))
    
    check_code_entry = Entry(whatsapp_frame,
        font = ("arial", "18"),width=30)
    
    save_phone_button = Button(whatsapp_frame, width=10, text = 'Save',
        font = ("arial", "12"), cursor="hand2", command = save_phone_number)

    frame1.forget()    
    whatsapp_frame.pack(side = "top", expand = True, fill = "both")
    
#================================================================ 
#============ Set email Frame ===================================
def set_email_and_password():
    code = str(datetime.now())[-6: ]
    def send_mail():
        send_email('Test', email_entry.get().strip(),
                   app_password_entry.get().strip(), code)# Test email
        email_label.pack_forget()
        email_entry.pack_forget()
        app_password_label.pack_forget()
        app_password_entry.pack_forget()
        check_email_button.pack_forget()
        check_email_label.pack(pady=20)
        check_code_entry.pack(pady=20)
        email_button.pack(pady=20)
        messagebox.showinfo('',
            'We sent a code to your email.')
    def get_email_and_password():   
        if check_code_entry.get() == code:
            pickle.dump([email_entry.get().strip(),
                        app_password_entry.get().strip()],
                        open(mypath+'\\'+"email_password.dat", "wb"))
            email_frame.forget()
            set_mail_button.configure(text='Stop mail alerts',
                                      command=stop_mail_alerts)
            frame1.pack(side = "top", expand = True, fill = "both")
            send_mail_btn.place(x = 730, y = 10)
            messagebox.showinfo('',
            'It works. Your email and password was set. Mail alerts \
            will be sent daily after midnight while app is running')
        else:
            messagebox.showinfo('', 'It does not works or bad internet connection. Follow instructions again.')
    
    
    def back():
        email_frame.forget()
        frame1.pack(side = "top", expand = True, fill = "both")

    email_frame = Frame(root, bg= 'light yellow')
    go_back_button = Button(email_frame, width=42, cursor="hand2",
            text = "Cancel",
            bg='#45b592', font = ("arial", "12"),fg='white',
            command = back).pack(side= TOP, pady=10)

    info_label = Label(email_frame,bg= 'light yellow', fg='brown',width=50, height=8,
                text="""Follow these instructions:
                           - Go to your Yahoo  account                         
                        - Go to the account info page                     
                        - Click account security                            
                        - Click create app passwords                     
                        Paste your App Password in 'Your app password'""",
                     font = ("arial", "10")).pack(side= TOP, pady=20)
    
    email_label = Label(email_frame, bg= 'light yellow', fg='brown',
        text = 'Your email', font = ("arial", "18"))
    email_label.pack(side= TOP, pady=20)
    email_entry = Entry(email_frame,font = ("arial", "18"),width=30)
    email_entry.pack(side= TOP, pady=10, padx=10)
    email_entry.focus_set()

    app_password_label = Label(email_frame, bg= 'light yellow', fg='brown',
        text = 'Your App Password', font = ("arial", "18"))
    app_password_label.pack(side= TOP, pady=20)
    app_password_entry = Entry(email_frame,font = ("arial", "18"),width=30)
    app_password_entry.pack(side= TOP, pady=10, padx=10)

    check_email_label = Label(email_frame, bg= 'light yellow', fg='brown',
        text = 'Paste code sent to your email', font = ("arial", "18"))
    
    check_code_entry = Entry(email_frame,font = ("arial", "18"),width=30)
    check_code_entry.focus_set()
    
    check_email_button = Button(email_frame, width=10, text = 'Verify',font = ("arial", "12"),
        cursor="hand2",command = send_mail)
    check_email_button.pack(pady=20)
    
    email_button = Button(email_frame, width=10, text = 'Save',font = ("arial", "12"),
        cursor="hand2",command = get_email_and_password)
    
    frame1.forget()    
    email_frame.pack(side = "top", expand = True, fill = "both")

#================================================================
#=== Check Password Frame =======================================
def check_password():
    
    check_password_frame = Frame(root, bg = 'light yellow')
    if os.path.exists(mypath+'\\'+"password.dat"):
        frame1.forget()
        check_password_frame.pack(side = "top", expand = True, fill = "both")

    def verify_password():
        try:
            stored_pwd = pickle.load(open(mypath+'\\'+"password.dat", "rb"))
            if e.get() == stored_pwd:
                check_password_frame.forget()
                frame1.pack(side = "top", expand = True, fill = "both")
                
            else:
                err_lbl.config(text='Incorect password. Try again')
                e.delete(0, END)
        except Exception as ex:
            pass
        
    l=Label(check_password_frame, bg= 'light yellow',text = 'Your password',
      font = ("arial", "18"), fg='brown')
    l.pack(side= TOP, pady=25)
    
    e=Entry(check_password_frame, font = ("arial", "18"), width=30)
    e.pack(side= TOP, pady=25)
    e.focus_set()
    e.bind("<Return>",
                (lambda event: verify_password()))#bind enter to verify password 
    
    err_lbl = Label(check_password_frame, bg= 'light yellow', font = ("arial", "20"))
    err_lbl.pack(side= TOP, pady=25)
    
#================================================================
#===== Notebook Frame ===========================================
def go_to_notebook():
    clear_entries()
    entrydate.config(state='disabled')
    entrytext.config(state='disabled')
    search_lbl.place_forget()
    search_entry.place_forget()
    if not os.path.exists(mypath+'\\'+"Notes.txt"):
        with open(mypath+'\\'+'Notes.txt', 'w') as f:
            f.write('')

    def callback_fisa(): # open fisa
        webbrowser.open_new(mypath+'\\'+'Notes.txt')
        
    def save_notebook():
        with open(mypath+'\\'+'Notes.txt', 'w') as f:
            f.write(notebook_text.get(1.0, 'end'))
            messagebox.showinfo('',"Saved.")
        return f

    def load_notebook():
        notebook_text.delete(1.0,'end')
        with open(mypath+'\\'+'Notes.txt', 'r') as f:   
            lines = f.readlines()           
            for lin in lines:
                notebook_text.insert(END,lin)

    def back_to_main():
        entrydate.config(state='normal')
        entrytext.config(state='normal')
        search_lbl.place(x = 330,y = 55)
        search_entry.place(x = 355, y = 51)
        canvas.destroy()   

    canvas=Canvas(frame1, bg='light yellow',width=836, height=398, borderwidth=0)

    label=Label(canvas,text='Notebook', bg='light yellow',borderwidth=0,
                        font=('Arial','12','italic','bold'))
    label.place(x=10,y=15)

    back_from_notes_btn=Button(canvas, text='Back',
       width = 6,cursor="hand2", bg='light yellow',borderwidth=0,
       font=("arial", "10", "bold"),command=back_to_main)
    back_from_notes_btn.bind("<Enter>",
            lambda e: back_from_notes_btn.config(fg='#caf0f8', bg='#3d6466'))
    back_from_notes_btn.bind("<Leave>",
            lambda e: back_from_notes_btn.config(fg='Black', bg='light yellow'))
    back_from_notes_btn.place(x=650,y=15)

    print_notes_btn=Button(canvas, text='Print',
        width = 6,cursor="hand2", bg='light yellow',borderwidth=0,
        font=("arial", "10", "bold"),command=callback_fisa)
    print_notes_btn.bind("<Enter>",
                lambda e: print_notes_btn.config(fg='#caf0f8', bg='#3d6466'))
    print_notes_btn.bind("<Leave>",
                lambda e: print_notes_btn.config(fg='Black', bg='light yellow'))
    print_notes_btn.place(x=480,y=15)

    

    save_notes_btn=Button(canvas, text='Save',
        width = 6,cursor="hand2", bg='light yellow',borderwidth=0,
        font=("arial", "10", "bold"),command=save_notebook)
    save_notes_btn.bind("<Enter>",
                lambda e: save_notes_btn.config(fg='#caf0f8', bg='#3d6466'))
    save_notes_btn.bind("<Leave>",
                lambda e: save_notes_btn.config(fg='Black', bg='light yellow'))
    save_notes_btn.place(x=330,y=15)

    notebook_text = Text(canvas, font='Bahnschrift', wrap=WORD,
        width = 90,height = 18)
    notebook_text.place(x=15,y=45)

    sb2 = Scrollbar(canvas)
    sb2.place(x=810, y=46, height=345)
    
    notebook_text.config(yscrollcommand=sb2.set)
    sb2.config(command=notebook_text.yview)
   
    load_notebook()
    canvas.place(x=10,y=185)
    
#================================================================    
#===== Archived Frame ===========================================    
def go_to_archived():
    clear_entries()
    entrydate.config(state='disabled')
    entrytext.config(state='disabled')
    search_lbl.place_forget()
    search_entry.place_forget()
    if not os.path.exists(mypath+'\\'+"Archived.txt"):
        with open(mypath+'\\'+'Archived.txt', 'w') as f:
            f.write('')
            
    def save_archived():
        with open(mypath+'\\'+'Archived.txt', 'w') as f:
            f.write(archived_text.get(1.0, 'end'))
            messagebox.showinfo('',"Saved.")
            return f

    def load_archived():
        archived_text.delete(1.0,'end')
        with open(mypath+'\\'+'Archived.txt', 'r') as f:   
            lines = f.readlines()           
            for lin in lines:
                archived_text.insert(END,lin)

    def back_to_main():
        entrydate.config(state='normal')
        entrytext.config(state='normal')
        search_lbl.place(x = 330,y = 55)
        search_entry.place(x = 355, y = 51)
        canvas_archived.destroy()   

    canvas_archived=Canvas(frame1, bg='light yellow',width=836, height=398,
                  borderwidth=0)

    label=Label(canvas_archived,text='Archived', bg='light yellow',borderwidth=0,
                        font=('Arial','12','italic','bold'))
    label.place(x=10,y=15)
    
    back_from_archived_btn=Button(canvas_archived, text='Back',
        width = 6,cursor="hand2", bg='light yellow',borderwidth=0,
        font=("arial", "10", "bold"),command=back_to_main)
    back_from_archived_btn.bind("<Enter>",
                lambda e: back_from_archived_btn.config(fg='#caf0f8', bg='#3d6466'))
    back_from_archived_btn.bind("<Leave>",
                lambda e: back_from_archived_btn.config(fg='Black', bg='light yellow'))
    back_from_archived_btn.place(x=650,y=15)

    save_archived_btn=Button(canvas_archived, text='Save',
        width = 6,cursor="hand2", bg='light yellow',borderwidth=0,
        font=("arial", "10", "bold"),command=save_archived)
    save_archived_btn.bind("<Enter>",
                lambda e: save_archived_btn.config(fg='#caf0f8', bg='#3d6466'))
    save_archived_btn.bind("<Leave>",
                lambda e: save_archived_btn.config(fg='Black', bg='light yellow'))
    save_archived_btn.place(x=330,y=15)

    archived_text = Text(canvas_archived, font='Bahnschrift', wrap=WORD,
        width = 90,
        height = 18)
    archived_text.place(x=15,y=45)

    sb2_archived = Scrollbar(canvas_archived)
    sb2_archived.place(x=810, y=46, height=345)
    
    archived_text.config(yscrollcommand=sb2_archived.set)
    sb2_archived.config(command=archived_text.yview)
    load_archived()
    canvas_archived.place(x=10,y=185)
    
#================================================================ 
#============ Hide screen =======================================
def hide_screen():
    hide_screen_frame=Frame(root, bg='light yellow')
    
    def back_to_screen():
        stored_pwd = pickle.load(open(mypath+'\\'+"password.dat", "rb"))
        if password_entry.get() == stored_pwd:
            hide_screen_frame.forget()
            frame1.pack(side = "top", expand = True, fill = "both")
        else:
            messagebox.showinfo('', 'Incorect password.')

    password_label = Label(hide_screen_frame, bg= 'light yellow', fg='brown',
        text = 'Password:', font = ("arial", "18"))
    password_label.pack(side= TOP, pady=35)
    
    password_entry = Entry(hide_screen_frame,
        font = ("arial", "18"),width=30)
    password_entry.pack(side= TOP, pady=35, padx=10)
    password_entry.focus_set()
    password_entry.bind("<Return>",
                (lambda event: back_to_screen()))#bind enter to verify password 
    
    frame1.forget()
    hide_screen_frame.pack(side = "top", expand = True, fill = "both")


'''================================================================''' 
'''============ Main App ==========================================''' 

def check_dates(li):
    global note_counter
    message_area.config(state='normal')
    message_area.delete('1.0', 'end')
    for el in li:
        if el != '' and not el[1].startswith('Done'):
            if nzdif(datetime.strptime(el[0],"%Y-%m-%d")) in range(0, -7, -1):
                note_counter+=1
                message_area.insert('insert', ' >>> ' + 
                    str(abs(nzdif(datetime.strptime(el[0],"%Y-%m-%d")))) +
                            ' day(s) ' + '\n ' + el[1]+'\n'+
                    '__________________________________________________' + '\n')

    counter_label.configure(text = str(note_counter) + ' notification(s) today.')    
    message_area.config(state='disabled')
    note_counter = 0

def refresh():
    clear_entries()
    listbox_update()   
    check_dates(notes)
    write_to_file()
            
def add_note():
    global notes
    date_note = entrydate.get()
    user_note = entrytext.get('1.0', 'end').strip()
    if len(user_note) == 0 or len(date_note) == 0:
        messagebox.showinfo('', 'Empty field.')        
    else:
        notes.append([date_note, user_note])
        notes.sort()
        refresh()
            
def delete_note():
    global notes
    note_to_delete = [entrydate.get(),
                        entrytext.get('1.0', 'end').strip()]
    if note_to_delete in notes:
        resp = messagebox.askquestion('Are you sure ?')
        if resp.upper() == "YES":
            notes.remove(list(note_to_delete))
            notes.sort()
            refresh()
    else:
        messagebox.showinfo('', "Can't delete an edited record.")
        clear_entries()

def archive_note():
    global notes
    note_to_archive = [entrydate.get(),
                            entrytext.get('1.0', 'end').strip()]
    if note_to_archive in notes:
        resp = messagebox.askquestion('Are you sure ?')
        if resp.upper() == "YES":
            notes.remove(list(note_to_archive))
            notes.sort()
            ################
            f = open(mypath+'\\'+'Archived.txt', 'r+')
            lines=f.readlines() # read old content
            f.seek(0) # go to begining
            f.write(', '.join(note_to_archive)+
                ' arhived on '+ str(azi)[ :10]+'.'+'\n') # write new content at begining
            for line in lines: # write old content after new
                f.write(line)
            f.close()
            ################
            refresh()                
    else:    
        messagebox.showinfo('', "Can't archive an edited record.")
        clear_entries()
    
def edit_note():
    global notes
    _index = main_listbox.curselection()
    if _index != ():
        if entrydate.get() != '' and entrytext.get('1.0', 'end').strip() != '':
            notes[_index[0]] = [entrydate.get(),
                        entrytext.get('1.0', 'end').strip()]
            notes.sort()
            refresh()
        else:
            messagebox.showinfo('',
            "Empty field.")
    else:# if main listbox loose selection
        messagebox.showinfo('',
            "Select the record then press 'Edit'.")

def mark_as_done():
    global notes
    _index = main_listbox.curselection()
    done_note = [entrydate.get(),
                        entrytext.get('1.0', 'end').strip()]
    if _index != () and done_note in notes and not notes[_index[0]][1].startswith('Done'):
        notes[_index[0]][1]=f'Done on {str(azi)[ :10]} - ' + notes[_index[0]][1]
        notes.sort()
        refresh()
    

def item_selected(event):
    if len(main_listbox.get(ANCHOR)) > 0:
        
        _index = main_listbox.curselection()
        entrytext.delete('1.0', 'end')
        entrydate.delete(0, 'end')
        note_to_edit=notes[_index[0]]
        entrytext.insert('1.0', ''.join(note_to_edit[1: ]))
        entrydate.insert(0, ''.join(note_to_edit[0]))
        edit_button.place(x = 180, y = 185)
        del_button.place(x = 297, y = 185)
        archive_button.place(x = 407, y = 185)
        done_button.place(x = 524, y = 185)
        add_button.place_forget()

def dark_mode():
    frame1.config(bg='black', fg='red')
    day_label.config(bg='black', fg='white')
    counter_label.config(bg='black', fg='lightgreen')
    label1.config(bg='black', fg='white')
    label2.config(bg='black', fg='white')
    search_entry.config(bg='black', fg='white')
    note_counter_label.config(bg='black', fg='lightgreen')
    labelcopyright.config(bg='black', fg='white')
    search_lbl.config(bg='black', fg='white')
    clear_button.config(bg='black', fg='white')

    lis=(add_button,edit_button,del_button,archive_button,done_button,
         archived_btn, notes_btn)
    for el in lis:
        el.config(bg='black', fg='white')
    
    add_button.bind("<Enter>",
                lambda e: add_button.config(fg='white', bg="#3d6466"))
    add_button.bind("<Leave>",
                lambda e: add_button.config(fg='white', bg='black'))
    edit_button.bind("<Enter>",
                lambda e: edit_button.config(fg='white', bg="#3d6466"))
    edit_button.bind("<Leave>",
                lambda e: edit_button.config(fg='white', bg='black'))
    del_button.bind("<Enter>",
                lambda e: del_button.config(fg='white', bg="#3d6466"))
    del_button.bind("<Leave>",
                lambda e: del_button.config(fg='white', bg='black'))
    archive_button.bind("<Enter>",
                lambda e: archive_button.config(fg='white', bg="#3d6466"))
    archive_button.bind("<Leave>",
                lambda e: archive_button.config(fg='white', bg='black'))
    done_button.bind("<Enter>",
                lambda e: done_button.config(fg='white', bg="#3d6466"))
    done_button.bind("<Leave>",
                lambda e: done_button.config(fg='white', bg='black'))
    archived_btn.bind("<Enter>",
                lambda e: archived_btn.config(fg='white', bg="#3d6466"))
    archived_btn.bind("<Leave>",
                lambda e: archived_btn.config(fg='white', bg='black'))
    notes_btn.bind("<Enter>",
                lambda e: notes_btn.config(fg='white', bg="#3d6466"))
    notes_btn.bind("<Leave>",
                lambda e: notes_btn.config(fg='white', bg='black'))
    
    if not os.path.exists(mypath+'\\'+"password.dat"):
        set_password_button.configure(bg='black',fg='white')
    set_mail_button.configure(bg='black',fg='white')
    set_whatsapp_button.configure(bg='black',fg='white')
    
    hide_screen_btn.configure(bg='black',fg='white')
    dark_button.config(bg='black')
    dark_button.config(command=light_mode, image=image2)

def light_mode():
    frame1.config(bg='#f2e9e4', fg='brown')
    day_label.config(bg='#f2e9e4', fg='black')
    counter_label.config(bg='#f2e9e4', fg='firebrick')
    label1.config(bg='#f2e9e4', fg='black')
    label2.config(bg='#f2e9e4', fg='black')
    search_entry.config(bg='#f2e9e4', fg='black')
    note_counter_label.config(bg='#f2e9e4', fg='firebrick')
    labelcopyright.config(bg='#f2e9e4', fg='black')
    search_lbl.config(bg='#f2e9e4', fg='black')
    clear_button.config(bg='#f2e9e4', fg='black')
    
    lis=[add_button,edit_button,del_button,archive_button,done_button,
         archived_btn, notes_btn]
    for el in lis:
        el.config(bg='#f2e9e4', fg='black')
    
    add_button.bind("<Enter>",
                lambda e: add_button.config(fg='white', bg="#3d6466"))
    add_button.bind("<Leave>",
                lambda e: add_button.config(fg='black', bg='#f2e9e4'))
    edit_button.bind("<Enter>",
                lambda e: edit_button.config(fg='white', bg="#3d6466"))
    edit_button.bind("<Leave>",
                lambda e: edit_button.config(fg='black', bg='#f2e9e4'))
    del_button.bind("<Enter>",
                lambda e: del_button.config(fg='white', bg="#3d6466"))
    del_button.bind("<Leave>",
                lambda e: del_button.config(fg='black', bg='#f2e9e4'))
    archive_button.bind("<Enter>",
                lambda e: archive_button.config(fg='white', bg="#3d6466"))
    archive_button.bind("<Leave>",
                lambda e: archive_button.config(fg='black', bg='#f2e9e4'))
    done_button.bind("<Enter>",
                lambda e: done_button.config(fg='white', bg="#3d6466"))
    done_button.bind("<Leave>",
                lambda e: done_button.config(fg='black', bg='#f2e9e4'))
    archived_btn.bind("<Enter>",
                lambda e: archived_btn.config(fg='white', bg="#3d6466"))
    archived_btn.bind("<Leave>",
                lambda e: archived_btn.config(fg='black', bg='#f2e9e4'))    
    notes_btn.bind("<Enter>",
                lambda e: notes_btn.config(fg='white', bg="#3d6466"))
    notes_btn.bind("<Leave>",
                lambda e: notes_btn.config(fg='black', bg='#f2e9e4'))
    
    if not os.path.exists(mypath+'\\'+"password.dat"):
        set_password_button.configure(bg='#f2e9e4',fg='black')
    set_mail_button.configure(bg='#f2e9e4',fg='black')
    set_whatsapp_button.configure(bg='#f2e9e4',fg='black')
    
    hide_screen_btn.configure(fg='black',bg='#f2e9e4')
    dark_button.config(bg='#03fceb')
    dark_button.config(bg='#f2e9e4',command=dark_mode,image=image)
    

def clear_entries():
    main_listbox.bind('<<ListboxSelect>>', item_selected)
    entrytext.delete('1.0', 'end')
    entrydate.delete(0, 'end')
    search_entry.delete(0, 'end')
    main_listbox.selection_clear(0, END)
    edit_button.place_forget()
    del_button.place_forget()
    archive_button.place_forget()
    done_button.place_forget()
    add_button.place(x = 73, y = 185)

def listbox_update():
    global notes
    main_listbox.delete(0, 'end')
    note_counter_label.config(text=f'{str(len(notes))} record(s)')
    for note in notes:
        if note:
            main_listbox.insert('end', ', '.join(note))    
            if nzdif(datetime.strptime(note[0],"%Y-%m-%d")) > 0 or\
               note[1].startswith('Done'):
                main_listbox.itemconfig('end',fg='gray55')
            elif nzdif(datetime.strptime(note[0],"%Y-%m-%d")) in range(0, -7, -1):
                main_listbox.itemconfig('end',fg='black',
                                background = "bisque")
            else:
                main_listbox.itemconfig('end',fg='black')
        
def search():
    main_listbox.bind('<<ListboxSelect>>', do_nothing2)
    entrytext.delete('1.0', 'end')
    entrydate.delete(0, 'end')
    search_list = []
    for el in notes:
        if search_entry.get().strip() != '' and \
           search_entry.get().strip().lower() in str(el).lower():
            search_list.append(el)
            
    
    if len(search_list) > 0 :
        main_listbox.delete(0, 'end')
        for e in search_list:                    
            main_listbox.insert('end', ', '.join(e))
            if nzdif(datetime.strptime(e[0],"%Y-%m-%d")) > 0:
                main_listbox.itemconfig('end',fg='gray55')
            elif nzdif(datetime.strptime(e[0],"%Y-%m-%d")) in range(0, -7, -1)\
                 and not el[1].startswith('Done'):
                main_listbox.itemconfig('end',fg='black',
                                background = "bisque")
            else:
                main_listbox.itemconfig('end',fg='black')
    search_entry.delete(0, 'end')

def close():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        stop_event.set()
        root.destroy()  
        sys.exit()

def do_nothing():
    pass
def do_nothing2(event):
    pass

def whatsapp_me_now():
    try:
        user_phone = pickle.load(open(mypath+'\\'+
                                        "phone.dat", "rb"))
        if len(message_area.get('1.0', 'end')) == 1:
            messagebox.showinfo('',"There are no notifications to sent now.")
        else:
            send_whatsapp_message('+40'+user_phone,
                                message_area.get('1.0', 'end'))
            messagebox.showinfo('',"Whatsapp message was sent.")
    except:
        messagebox.showinfo('',
            "You have poor internet connection.Whatsapp message failed")

def stop_whatsapp_alerts():
    if os.path.exists(mypath+'\\'+"phone.dat"):
        os.remove(mypath+'\\'+"phone.dat")
        set_whatsapp_button.config(text="Set whatsapp alerts",
                                   command = set_whatsapp_alerts)
        send_whatsapp_btn.place_forget()
        
def mail_me_now():    
    try:
        user_email_and_pwd = pickle.load(open(mypath+'\\'+
                                        "email_password.dat", "rb"))
        if len(message_area.get('1.0', 'end')) == 1:
            messagebox.showinfo('',"There are no notifications to sent now.")
        else:
            send_email('remindMe - Alerts', user_email_and_pwd[0],
                       user_email_and_pwd[1],message_area.get('1.0', 'end') )
            messagebox.showinfo('',"Email was sent.")               
    except:
        messagebox.showinfo('',
            "You have poor internet connection.Email failed")

def stop_mail_alerts():
    if os.path.exists(mypath+'\\'+"email_password.dat"):
        os.remove(mypath+'\\'+"email_password.dat")
        set_mail_button.config(text="Set mail alerts",
                                   command = set_email_and_password)
        send_mail_btn.place_forget()

'''============================================================'''
'''==========  INTERFACE  ====================================='''
root.title(string='')   
root.geometry("865x620+350+50")
root.iconbitmap(ICON_PATH) 
root.protocol("WM_DELETE_WINDOW", close)
    
image = PhotoImage(file=os.path.join(basedir, 'icons8-moon-and-stars-16.png'))
image2 = PhotoImage(file=os.path.join(basedir, 'icons8-summer-16.png'))

    
frame1 = LabelFrame(root, bg='#f2e9e4',
            fg='brown',text='      - RemindMe -',
            font=('Arial','12','italic','bold'),borderwidth=0)  
frame1.pack(side = "top", expand = True, fill = "both")
    

day_label = Label(frame1, text = str(azi)[ :11], fg = 'black',font = ("arial", "8"), bg='#f2e9e4' )
day_label.place(x = 10, y = 10)

counter_label = Label(frame1, text = "", fg = 'firebrick4', font = ("arial", "10"), bg='#f2e9e4' )
counter_label.place(x = 470, y = 10)
    
label1 = Label(frame1, text = "When :", font = ("arial", "14"), bg='#f2e9e4')   
label1.place(x = 40, y = 45)
  
label2 = Label(frame1, text = "What  :",font = ("arial", "14"), bg='#f2e9e4')   
label2.place(x = 40, y = 80)

entrydate = DateEntry(frame1, date_pattern='YYYY-mm-dd',font = ("Arial", "12"),borderwidth=3,width = 10)
entrydate.place(x = 120, y = 48)

search_lbl= Label(frame1,text='Find',fg = 'firebrick4',font = ("arial", "7"), bg='#f2e9e4')
search_lbl.place(x = 330,y = 55)

search_entry = Entry(frame1, width=14, font = ("arial", "10"),bg='#f2e9e4', borderwidth=0.5)
search_entry.place(x = 355, y = 51)
search_entry.focus_set()
search_entry.bind("<Return>",
                (lambda event: search()))# bind enter key to search
        
    
entrytext = Text(frame1, font = ("Times", "12", "bold"),
                     height = 5, wrap = WORD,
                    width = 42, foreground="black", background = "white")          
entrytext.place(x = 120, y = 82)
entrytext.focus_set()

note_counter_label = Label(frame1, text = "", fg = 'firebrick4',font = ("arial", "8"), bg='#f2e9e4' )
note_counter_label.place(x = 14, y = 190)
#send mail now
send_mail_btn=Button(frame1,  text = "Mail now", width = 14,borderwidth=0,
                    cursor="hand2", bg="grey", fg = 'white',
                    font=("arial","8",'bold'),command = mail_me_now)
#send whatsapp now
send_whatsapp_btn=Button(frame1,  text = "Whatsapp now", width = 14,borderwidth=0,
                    cursor="hand2", bg="grey", fg = 'white',
                    font=("arial","8",'bold'),command = whatsapp_me_now)
#add    
add_button =Button(frame1,  text = "Add", width = 9,borderwidth=0,
                    cursor="hand2", bg='#f2e9e4', fg = 'black',
                    font=("arial","11",'italic'),command = add_note)
add_button.place(x = 73, y = 185)
add_button.bind("<Enter>",
                lambda e: add_button.config(fg='white', bg="#3d6466"))
add_button.bind("<Leave>",
                lambda e: add_button.config(fg='Black', bg='#f2e9e4'))
#Add_button.bind('<Return>',lambda event:add_note())
#edit    
edit_button =Button(frame1,  text = "Edit", width = 10,borderwidth=0,
                    cursor="hand2", bg='#f2e9e4', fg = 'black',
                    font=("arial", "11",'italic'),command = edit_note)
edit_button.bind("<Enter>",
                lambda e: edit_button.config(fg='white', bg='#3d6466'))
edit_button.bind("<Leave>",
                lambda e: edit_button.config(fg='Black', bg='#f2e9e4'))
#delete      
del_button = Button(frame1,  text = "Delete",  width = 10,borderwidth=0,
                    cursor="hand2", bg='#f2e9e4', fg = 'black',
                    font=("arial", "11",'italic'),command = delete_note)
del_button.bind("<Enter>",
                    lambda e: del_button.config(fg='white', bg='#3d6466'))
del_button.bind("<Leave>",
                    lambda e: del_button.config(fg='Black', bg='#f2e9e4'))
#archive
archive_button = Button(frame1,  text = "Archive",  width = 10,borderwidth=0,
                    cursor="hand2", bg='#f2e9e4', fg = 'black',
                    font=("arial", "11",'italic'),command = archive_note)
archive_button.bind("<Enter>",
                    lambda e: archive_button.config(fg='white', bg='#3d6466'))
archive_button.bind("<Leave>",
                    lambda e: archive_button.config(fg='Black', bg='#f2e9e4'))
#done
done_button = Button(frame1,  text = "Done",  width = 10,borderwidth=0,
                    cursor="hand2", bg='#f2e9e4', fg = 'black',
                    font=("arial", "11",'italic'),command = mark_as_done)
done_button.bind("<Enter>",
                    lambda e: done_button.config(fg='white', bg='#3d6466'))
done_button.bind("<Leave>",
                    lambda e: done_button.config(fg='Black', bg='#f2e9e4'))
#dark_mode
dark_button = Button(frame1,  image = image,  width = 12,bg='#f2e9e4',
                         borderwidth=0,
                    cursor="hand2",command = dark_mode)
dark_button.place(x = 140, y = 0)#x = 670, y = 185)

#clear
clear_button = Button(frame1,text = "Clear", width = 7,
                    cursor="hand2",bg='#f2e9e4',borderwidth=1,
                    font=("arial", "7", "bold"), command = refresh)
clear_button.place(x = 260, y = 55)
     
main_listbox = Listbox(frame1, width = 104,
        height = 18, borderwidth=0, font=("Arial bold", "11",'italic'),
        selectmode = 'SINGLE',
        background = "white", foreground="darkgreen",                   
        selectbackground = 'dark green',
        selectforeground="white",
        activestyle='none',        
    )   
main_listbox.place( x = 17, y = 215)

sb = Scrollbar(frame1)
sb.place(x=833, y=215, height=344)
    
main_listbox.config(yscrollcommand=sb.set)
sb.config(command=main_listbox.yview)
    

labelcopyright = Label( frame1,
        text = copyright + str(azi)[ :4] + " iancuioan897@yahoo.ro",  
        font = ("arial", "7"), bg='#f2e9e4')   
labelcopyright.place(x = 20, y = 585)

set_mail_button = Button(frame1, text = "Set mail alerts",borderwidth=0,
        width = 12, bg='#f2e9e4', fg='black', font=("italic", "8", 'bold'),
        cursor="hand2", command = set_email_and_password)
set_mail_button.place(x = 250, y = 560)


set_password_button = Button(frame1, text = "Set a password",borderwidth=0,
        width = 12, bg='#f2e9e4', fg='black', font=("italic", "8", 'bold'),
        cursor="hand2", command = set_password)
set_password_button.place(x = 400, y = 560)

set_whatsapp_button = Button(frame1, text = "Set whatsapp alerts",borderwidth=0,
        width = 16, bg='#f2e9e4', fg='black', font=("italic", "8", 'bold'),
        cursor="hand2", command = set_whatsapp_alerts)
set_whatsapp_button.place(x = 80, y = 560)

hide_screen_btn = Button(frame1, text = "Logout",borderwidth=0,
        width = 12, bg='#f2e9e4', fg='black', font=("italic", "8", 'bold'),
        cursor="hand2", command = hide_screen)
    
# archived
archived_btn=Button(frame1, text='Archived ', width = 12,
        bg='#f2e9e4', fg='black', font=("italic", "8", 'bold'),borderwidth=0,
        cursor="hand2", command = go_to_archived)
archived_btn.place(x = 560, y = 560)
archived_btn.bind("<Enter>",
                    lambda e: archived_btn.config(fg='white', bg='#3d6466'))
archived_btn.bind("<Leave>",
                    lambda e: archived_btn.config(fg='Black', bg='#f2e9e4'))
    
# notes
notes_btn=Button(frame1, text='Notebook ', width = 12,
        bg='#f2e9e4', fg='black', font=("italic", "8", 'bold'),borderwidth=0,
        cursor="hand2", command = go_to_notebook)
notes_btn.place(x = 715, y = 560)
notes_btn.bind("<Enter>",
                    lambda e: notes_btn.config(fg='white', bg='#3d6466'))
notes_btn.bind("<Leave>",
                    lambda e: notes_btn.config(fg='Black', bg='#f2e9e4'))
    
message_area = scrolledtext.ScrolledText(frame1, wrap=WORD,
                                fg='black', height = 9,
                                borderwidth=0,width = 51,
                                font = "none 10 bold")
message_area.place(x = 475, y = 35 )

if os.path.exists(mypath+'\\'+"email_password.dat"):
    set_mail_button.config(text="Stop mail alerts",
                                   command = stop_mail_alerts)
    send_mail_btn.place(x = 740, y = 10)
if os.path.exists(mypath+'\\'+"password.dat"):
    set_password_button.destroy()
    hide_screen_btn.place(x = 400, y = 560)
if os.path.exists(mypath+'\\'+"phone.dat"):
    set_whatsapp_button.config(text="Stop whatsapp alerts",
                                   command = stop_whatsapp_alerts)
    send_whatsapp_btn.place(x = 620, y = 10)


stop_event=threading.Event()        
t1 = threading.Thread(target=send_notification, args=(stop_event,))
t1.start()    
check_password()
read_from_file()
check_dates(notes)
listbox_update()        
main_listbox.bind('<<ListboxSelect>>', item_selected)
  
root.mainloop()
    
    






