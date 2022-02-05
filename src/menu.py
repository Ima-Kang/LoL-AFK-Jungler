import tkinter as tk
import json
from tkinter import ttk, filedialog, Text
from tkinter.messagebox import showinfo
from run import run_app, Settings
import os
settings = Settings()

def add_path():
    settings.config = filedialog.askdirectory()
    config_path.set(f"Path: {settings.config}")

def kill_window(root, e_name, e_games):
    root.destroy()
    settings_json ={
    "name" : e_name.get(),
    "games" : e_games.get(),
    "record" : settings.record,
    "config" : settings.config
    }

    json_obj = json.dumps(settings_json)
    with open("..\settings\settings.json", "w") as outfile:
        outfile.write(json_obj)

    run_app(Settings(settings.record, e_name.get(), e_games.get(), settings.config))

def set_record(record_text):
    settings.record = not settings.record
    record_text.set(f"Record: On" if settings.record else f"Record: Off")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x225")
    root.resizable(False, False)
    root.title('LoL AFK Jungler')
    root.iconphoto(False, tk.PhotoImage(file=r'..\res\nunu & willump.png'))

    e_name = tk.StringVar()
    e_games = tk.IntVar()
    record_text = tk.StringVar()
    settings.record = False
    config_path = tk.StringVar()
    settings.config = ""

    try:
        settings_dict = json.load(open("..\settings\settings.json"))
        e_name.set(settings_dict["name"])
        e_games.set(settings_dict["games"])
        record_text.set(settings_dict["record"])
        settings.record = settings_dict["record"]
        path = settings_dict["config"]
        config_path.set(f"Path: {path}")
        settings.config = settings_dict["config"]
    except:
        pass
    
    record_text.set(f"Record: On" if settings.record else f"Record: Off")
    record = lambda: set_record(record_text)
    start_bot = lambda: kill_window(root, e_name, e_games)

    app = ttk.Frame(root)
    app.pack(padx=10, pady=10, fill='x', expand=True)

    L1 = ttk.Label(app, text="User Name")
    L1.pack(fill='x', expand=True)

    E1 = ttk.Entry(app, textvariable=e_name)
    E1.pack(fill='x', expand=True)
    E1.focus()

    L2 = ttk.Label(app, text="Number of Games")
    L2.pack(fill='x', expand=True)

    E2 = ttk.Entry(app, textvariable=e_games)
    E2.pack(fill='x', expand=True)

    config_button = ttk.Button(app, text="Set config path", command=add_path)
    config_button.pack(fill='x', expand=True, pady=5)
    L3 = ttk.Label(app, textvariable=config_path)
    L3.pack(fill='x', expand=True)

    record_button = ttk.Button(app, textvariable=record_text, command=record)
    record_button.pack(fill='x', expand=True, pady=5)

    run_app_button = ttk.Button(app, text="Run", command=start_bot)
    run_app_button.pack(fill='x', expand=True, pady=5)

    root.mainloop()