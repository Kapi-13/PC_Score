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

#app.resizable(False, False)

app.grid_rowconfigure(0, weight=1)
app.grid_rowconfigure(1, weight=1)
app.grid_rowconfigure(2, weight=1)
app.grid_columnconfigure(0, weight=1)

for i in range(3,5):
    print(i)

title = ctk.CTkLabel(app,text="DASHBOARD NA ŻYWO", font=("Arial", 25, "bold"), text_color="lightgray")
# title.place(rely=0, relx=0.5, anchor="n")

cpu_lbl = ctk.CTkLabel(app)

gpu_lbl = ctk.CTkLabel(app)

ram_lbl = ctk.CTkLabel(app)



# frame1 = ctk.CTkFrame(app, fg_color="transparent", border_width=2, border_color="red")
# frame1.grid(row=0, column=0, sticky="nsew")

# frame2 = ctk.CTkFrame(app, fg_color="transparent", border_width=2, border_color="blue")
# frame2.grid(row=1, column=0, sticky="nsew")

textbox = ctk.CTkTextbox(app, state="disabled", font=("Consolas", 20))
textbox.grid(row=2, column=0, sticky="nsew")
textbox.tag_config("default", foreground="lightgray")
textbox.tag_config("err", foreground="red")
textbox.tag_config("warn", foreground="orange")
textbox.tag_config("succ", foreground="green")
text.set_textbox(textbox)

def start():
    text.clear()
    # === CPU ===
    cpu_usage = psutil.cpu_percent(interval=None)
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

        # ? Zużycie VRAM w MB / GB
        # ? memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
        # ? vram_used_gb = round(memory.used / (1024**3), 2)
        # ? vram_total_gb = round(memory.total / (1024**3), 2)
    # === TOP 5 PROCESÓW (po RAM-ie) ===
    top5 = modules.wez_top_procesy_po_ram(NUMBER_OF_PROCESSES)

    text.text(f"Zużycie CPU: {cpu_usage}%\n", "succ" if cpu_usage <= 50 else "warn" if cpu_usage <= 70 else "err")
    text.text(f"Zużycie GPU: {gpu_usage}%\n", "succ" if gpu_usage <= 50 else "warn" if gpu_usage <= 85 else "err")
    text.text(f"Zużycie RAM: {ram_used_gb}/{ram_total_gb}GB - {ram_percent}%\n", "succ" if ram_percent <= 50 else "warn" if ram_percent <= 80 else "err")
    text.text(f"\nTop 5 procesów pod RAM:")
    for id, process in enumerate(top5):
        text.text(f"\n    #{id + 1}: {process[0]} {process[1]}MB")
    app.update_idletasks()
    app.after(delay, start)

pynvml.nvmlInit()
start()
app.mainloop()
pynvml.nvmlShutdown()
