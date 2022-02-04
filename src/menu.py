from os import kill
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from run import run_app, Settings

settings = Settings()

def kill_window(root, e_record, e_name, e_games):
    root.destroy()
    run_app(Settings(settings.record, e_name.get(), e_games.get()))

def set_record(record):
    settings.record = not record

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x175")
    root.resizable(False, False)
    root.title('LoL AFK Jungler')
    e_name = tk.StringVar()
    e_games = tk.IntVar()
    e_record = False

    record = lambda: set_record(e_record)
    start_bot = lambda: kill_window(root, e_record, e_name, e_games)

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

    record_button = ttk.Button(app, text="Record", command=record)
    record_button.pack(fill='x', expand=True, pady=5)

    run_app_button = ttk.Button(app, text="Run", command=start_bot)
    run_app_button.pack(fill='x', expand=True, pady=5)

    root.mainloop()