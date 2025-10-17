# file_generation_tool.py
# GUI tool to generate large files with progress, speed, ETA, and stop control
# Lets user choose folder via system file picker
# Default file name: "tool generated file.txt"

import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

stop_flag = False  # Global stop signal


def make_big_file(filepath, size_value, unit, progress_var, speed_label, eta_label, start_button, stop_button):
    global stop_flag
    bytes_per_gb = 1024 * 1024 * 1024
    bytes_per_mb = 1024 * 1024

    target_size = int(size_value * (bytes_per_gb if unit == "GB" else bytes_per_mb))
    chunk_size = 100 * 1024 * 1024  # 100 MB chunks
    chunk = ("A" * chunk_size).encode("ascii")

    written = 0
    start_time = time.time()
    progress_var.set(0)
    stop_flag = False

    try:
        with open(filepath, "wb") as f:
            while written < target_size and not stop_flag:
                to_write = min(chunk_size, target_size - written)
                f.write(chunk[:to_write])
                written += to_write

                # Update progress
                progress = (written / target_size) * 100
                progress_var.set(progress)

                # Calculate speed & ETA
                elapsed = time.time() - start_time
                speed = (written / (1024 * 1024)) / elapsed if elapsed > 0 else 0  # MB/s
                remaining_bytes = target_size - written
                remaining_time = remaining_bytes / (speed * 1024 * 1024) if speed > 0 else 0

                speed_label.config(text=f"Speed: {speed:,.2f} MB/s")
                eta_label.config(text=f"ETA: {remaining_time/60:.2f} min")
                root.update_idletasks()

        if stop_flag:
            # Delete partial file if stopped
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    messagebox.showinfo("Stopped", f"⏹ File generation stopped.\nPartial file deleted.")
                except Exception as e:
                    messagebox.showwarning("Warning", f"Stopped, but failed to delete file:\n{e}")
        else:
            messagebox.showinfo("Done!", f"✅ File created:\n{filepath}")

    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)


def select_folder():
    folder = filedialog.askdirectory(title="Choose a folder to save the file")
    if folder:
        folder_var.set(folder)


def start_generation():
    global stop_flag
    stop_flag = False
    try:
        size_value = float(size_entry.get())
        if size_value <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid positive number.")
        return

    folder = folder_var.get()
    if not folder:
        messagebox.showerror("No Folder Selected", "Please choose a folder first.")
        return

    unit = unit_var.get()
    filepath = os.path.join(folder, "tool generated file.txt")

    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    progress_var.set(0)

    threading.Thread(
        target=make_big_file,
        args=(filepath, size_value, unit, progress_var, speed_label, eta_label, start_button, stop_button),
        daemon=True,
    ).start()


def stop_generation():
    global stop_flag
    stop_flag = True


# ---------------- GUI ----------------
root = tk.Tk()
root.title("File Generation Tool")
root.geometry("480x340")
root.resizable(False, False)

tk.Label(root, text="File Generation Tool", font=("Segoe UI", 14, "bold")).pack(pady=5)

# Folder selection
folder_frame = tk.Frame(root)
folder_frame.pack(pady=5)

folder_var = tk.StringVar()
folder_entry = tk.Entry(folder_frame, textvariable=folder_var, width=40, font=("Segoe UI", 10))
folder_entry.grid(row=0, column=0, padx=5)
browse_button = tk.Button(folder_frame, text="Browse...", command=select_folder, font=("Segoe UI", 10))
browse_button.grid(row=0, column=1, padx=5)

# File size selection
frame = tk.Frame(root)
frame.pack(pady=5)

tk.Label(frame, text="File Size:", font=("Segoe UI", 11)).grid(row=0, column=0, padx=5)
size_entry = tk.Entry(frame, width=10, font=("Segoe UI", 11), justify="center")
size_entry.insert(0, "26")
size_entry.grid(row=0, column=1, padx=5)

unit_var = tk.StringVar(value="GB")
unit_selector = ttk.Combobox(
    frame, textvariable=unit_var, values=["MB", "GB"], width=5, state="readonly", font=("Segoe UI", 10)
)
unit_selector.grid(row=0, column=2, padx=5)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

start_button = tk.Button(
    button_frame,
    text="Generate File",
    font=("Segoe UI", 11, "bold"),
    command=start_generation,
    bg="#4CAF50",
    fg="white",
    width=14,
)
start_button.grid(row=0, column=0, padx=5)

stop_button = tk.Button(
    button_frame,
    text="Stop",
    font=("Segoe UI", 11, "bold"),
    command=stop_generation,
    bg="#E53935",
    fg="white",
    width=8,
    state=tk.DISABLED,
)
stop_button.grid(row=0, column=1, padx=5)

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, length=380, variable=progress_var)
progress_bar.pack(pady=8)

# Status labels
speed_label = tk.Label(root, text="Speed: 0 MB/s", font=("Segoe UI", 10))
speed_label.pack()
eta_label = tk.Label(root, text="ETA: -- min", font=("Segoe UI", 10))
eta_label.pack()

tk.Label(
    root, text="(Generates large ASCII files quickly)", font=("Segoe UI", 9, "italic"), fg="gray"
).pack(pady=6)

root.mainloop()