import tkinter as tk
import json
from tkinter import ttk
from tkinter.messagebox import showinfo
from run import run_app, Settings

settings = Settings()

def kill_window(root, e_name, e_games):
    root.destroy()
    settings_json ={
    "name" : e_name.get(),
    "games" : e_games.get(),
    "record" : settings.record
    }

    json_obj = json.dumps(settings_json)
    with open("settings.json", "w") as outfile:
        outfile.write(json_obj)

    run_app(Settings(settings.record, e_name.get(), e_games.get()))

def set_record(record_text):
    settings.record = not settings.record
    record_text.set(f"Record: On" if settings.record else f"Record: Off")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x175")
    root.resizable(False, False)
    root.title('LoL AFK Jungler')
    root.iconphoto(False, tk.PhotoImage(file=r'..\res\nunu & willump.png'))

    e_name = tk.StringVar()
    e_games = tk.IntVar()
    settings.record = False
    record_text = tk.StringVar()

    try:
        settings_dict = json.load(open("settings.json"))
        e_name.set(settings_dict["name"])
        e_games.set(settings_dict["games"])
        settings.record = settings_dict["record"]
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

    
    record_button = ttk.Button(app, textvariable=record_text, command=record)
    record_button.pack(fill='x', expand=True, pady=5)

    run_app_button = ttk.Button(app, text="Run", command=start_bot)
    run_app_button.pack(fill='x', expand=True, pady=5)

    root.mainloop()