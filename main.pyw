import sys
sys.dont_write_bytecode = True
# === wygląd
from myM.colors import color
from time import sleep
from typing import Literal
import customtkinter as ctk

# === pobieranie danych ===
import psutil
import pynvml

import modules

# === inne ===
import json
import threading

NUMBER_OF_PROCESSES = 5

class textbox_manager:
    def __init__(self):
        self.textbox: ctk.CTkTextbox

    def set_textbox(self, textbox: ctk.CTkTextbox):
        self.textbox = textbox

    def text(self, text:str, theme:Literal["default", "err", "warn", "succ"] = "default"):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text, theme)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def clear(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

text = textbox_manager()

# === ŁADOWANIE DANYCH O PROFILU ===

delay,pc_ram,round_cpu_ram = modules.read_profiles()

ctk.set_appearance_mode("Dark")

app = ctk.CTk()
app.title("DASHBOARD NA ŻYWO")
app.geometry("600x500")

# app.resizable(False, False)

app.grid_rowconfigure((0,1), weight=1) #*tytuł, data_frame
app.grid_columnconfigure(0, weight=1) #* wszystko

for i in range(3,5):
    print(i)

title = ctk.CTkLabel(app,text="DASHBOARD NA ŻYWO", font=("Arial", 25, "bold"), text_color="lightgray")
title.grid(row=0, column=0, sticky="ns")

data_frame = ctk.CTkFrame(app, fg_color="transparent")
data_frame.grid(row=1, column=0, sticky="ns")

data_frame.grid_rowconfigure((0,1,2,3), weight=1) #* cpu_lbl, gpu_lbl, ram_lbl, top_5_textbox
# data_frame.grid_rowconfigure(3, weight=1) #* top_5_text
# data_frame.grid_rowconfigure(4, weight=1) #* top_5_lbl 1
# data_frame.grid_rowconfigure(5, weight=1) #* top_5_lbl 2
# data_frame.grid_rowconfigure(6, weight=1) #* top_5_lbl 3
# data_frame.grid_rowconfigure(7, weight=1) #* top_5_lbl 4
# data_frame.grid_rowconfigure(8, weight=1) #* top_5_lbl 5

cpu_lbl = ctk.CTkLabel(data_frame, text="Ładowanie...", font=("Consolas", 20))
cpu_lbl.grid(row=0, column=0)

gpu_lbl = ctk.CTkLabel(data_frame, text="Ładowanie...", font=("Consolas", 20))
gpu_lbl.grid(row=1, column=0)

ram_lbl = ctk.CTkLabel(data_frame, text="Ładowanie...", font=("Consolas", 20))
ram_lbl.grid(row=2, column=0)


# top_5_lbls = [
#     ctk.CTkLabel(data_frame, text="Ładowanie...", font=("Consolas", 20), text_color="lightgray"),
#     ctk.CTkLabel(data_frame, text="Ładowanie...", font=("Consolas", 20), text_color="lightgray"),
#     ctk.CTkLabel(data_frame, text="Ładowanie...", font=("Consolas", 20), text_color="lightgray"),
#     ctk.CTkLabel(data_frame, text="Ładowanie...", font=("Consolas", 20), text_color="lightgray"),
#     ctk.CTkLabel(data_frame, text="Ładowanie...", font=("Consolas", 20), text_color="lightgray")
#     ]
# for id,lbl in enumerate(top_5_lbls):
#     lbl.grid(row=id + 4, column=0)

# top_5_text = ctk.CTkLabel(data_frame, text="Top 5 procesów pod RAM:", font=("Consolas", 20), text_color="lightgray")
# top_5_text.grid(row=3, column=0)

top_5_textbox = ctk.CTkTextbox(data_frame, state="disabled", font=("Consolas", 20))

top_5_textbox.tag_config("default", foreground="lightgray")
top_5_textbox.tag_config("err", foreground="red")
top_5_textbox.tag_config("warn", foreground="orange")
top_5_textbox.tag_config("succ", foreground="green")
text.set_textbox(top_5_textbox)

def start():
    text.clear()
    # === CPU ===
    cpu_usage = psutil.cpu_percent(interval=None)
    # cpu_usage = 1.4
    cpu_usage = round(cpu_usage) if round_cpu_ram else cpu_usage

    # === RAM ===
    ram = psutil.virtual_memory()
    ram_used_gb = round(ram.used / (1024**3), pc_ram)
    ram_total_gb = round(ram.total / (1024**3), pc_ram)
    ram_percent = ram.percent
    ram_percent = round(ram_percent) if round_cpu_ram else ram_percent

    handle = pynvml.nvmlDeviceGetHandleByIndex(0)

    # Zużycie rdzenia GPU w %
    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
    gpu_usage = utilization.gpu
    # gpu_usage = 12.6
        # ? Zużycie VRAM w MB / GB
        # ? memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
        # ? vram_used_gb = round(memory.used / (1024**3), 2)
        # ? vram_total_gb = round(memory.total / (1024**3), 2)
    # === TOP 5 PROCESÓW (po RAM-ie) ===
    # top5 = modules.wez_top_procesy_po_ram(NUMBER_OF_PROCESSES)

    cpu_lbl.configure(text=f"Zużycie CPU: {cpu_usage}%", text_color="green" if cpu_usage <= 50 else "orange" if cpu_usage <= 70 else "red")
    gpu_lbl.configure(text=f"Zużycie GPU: {gpu_usage}%", text_color="green" if gpu_usage <= 50 else "orange" if gpu_usage <= 85 else "red")
    ram_lbl.configure(text=f"Zużycie RAM: {ram_used_gb}/{ram_total_gb}GB - {ram_percent}%", text_color="green" if ram_percent <= 50 else "orange" if ram_percent <= 80 else "red")
    
    # for id, process in enumerate(top5):
        # text.text(f"    #{id + 1}: {process[0]} {process[1]}MB")
    app.update_idletasks()
    app.after(delay, lambda: threading.Thread(target=start, daemon=True).start())

pynvml.nvmlInit()
threading.Thread(target=start, daemon=True).start()
app.mainloop()
pynvml.nvmlShutdown()
