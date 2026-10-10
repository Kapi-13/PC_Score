import psutil
import win32api
from json import load

cache = {}
process_ram: None | int = None

def pobierz_pelna_nazwe(proc: psutil.Process) -> str:
    try:
        name = proc.name()
        if name == "System Idle Process":
            return name
        sciezka_exe = proc.exe()
        if name in cache:
            return cache[name]
        else:
            print("Brak w bazie danych")
            info = win32api.GetFileVersionInfo(sciezka_exe, "\\")
            lang, codepage = win32api.GetFileVersionInfo(
                sciezka_exe, r"\VarFileInfo\Translation"
            )[0]
            str_info_path = f"\\StringFileInfo\\{lang:04x}{codepage:04x}\\FileDescription"
            pelna_nazwa = str(win32api.GetFileVersionInfo(sciezka_exe, str_info_path))
            if pelna_nazwa.strip():
                cache[name] = pelna_nazwa
                return pelna_nazwa
            else:
                cache[name] = name
                return proc.name()
    except Exception as e:
        print(f"error: {repr(e)} i {e}")
        cache[proc.name()] = proc.name()
        return proc.name()

def read_profiles() -> tuple[int, int|None, int|None]:
    with open("data/profiles.json", "r", encoding="utf-8") as file:
        global process_ram
        data = load(file)
        actual_profil = data["actual_profil"]

        profil_data = data["profiles"][actual_profil]
        ram_round = profil_data["ram_round"]

        delay = profil_data["delay"]
        pc_ram = None if ram_round[0] == 0 else ram_round[0]
        process_ram = None if ram_round[1] == 0 else ram_round[1]
        round_cpu_ram = profil_data["round_cpu_and_ram_percent"]

        return delay,pc_ram,round_cpu_ram

def wez_top_procesy_po_ram(number: int) ->list[tuple[str, float]]:
    global process_ram
    processes:list[tuple[str,float]] = []
    for proc in psutil.process_iter(["name", "memory_info"]):
        try:
            ram_mb = round(proc.info["memory_info"].rss / (1024**2), process_ram)
            process_name = pobierz_pelna_nazwe(proc)
            processes.append((process_name.strip("'"), ram_mb))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    top5 = sorted(processes, key=lambda x: x[1], reverse=True)[:number]
    return top5