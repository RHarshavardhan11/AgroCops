import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # Requires: pip install Pillow
import serial
import serial.tools.list_ports
import threading
import random
import time
import sys
import os
from datetime import datetime, timedelta

# --- MATPLOTLIB IMPORTS ---
import matplotlib
matplotlib.use("TkAgg") 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# --- CONFIGURATION ---
SERIAL_PORT = 'COM8'    # <--- CHECK YOUR PORT
BAUD_RATE = 115200
LIVE_SENSOR_ID = (3, 4) 
GRID_ROWS = 10         
GRID_COLS = 10         

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SensorPopup:
    """Detailed View: Handles Active, Offline, and Inactive States"""
    def __init__(self, parent, r, c, is_real, real_data_ref, is_connected, is_active_sim):
        self.top = tk.Toplevel(parent)
        self.top.geometry("900x700") 
        self.top.configure(bg="#1e1e1e")
        
        self.r = r
        self.c = c
        self.is_real = is_real
        self.real_data_ref = real_data_ref
        self.is_connected = is_connected
        self.is_active_sim = is_active_sim
        
        # DETERMINE MODE
        self.is_inactive_mode = False
        
        # 1. Real Sensor but Disconnected OR 2. Fake Sensor that is Grey
        if (is_real and not is_connected) or (not is_real and not is_active_sim):
            self.is_inactive_mode = True
            self.top.title(f"SENSOR S-{r}-{c} | INACTIVE")
        else:
            self.top.title(f"LIVE MONITOR: SENSOR S-{r}-{c}")

        self.setup_dashboard()

    def setup_dashboard(self):
        # --- INITIAL DATA GENERATION ---
        self.x_data = list(range(50))
        self.y_data = []
        self.timestamps = []
        
        now = datetime.now()
        
        # If Inactive, flatline at 0
        if self.is_inactive_mode:
            base = 0
        else:
            base = 300
            if self.is_real and self.real_data_ref.get('gas', 0) > 1000: base = 1200 
        
        for i in range(50):
            t = now - timedelta(seconds=(49-i))
            self.timestamps.append(t.strftime("%H:%M:%S"))
            if self.is_inactive_mode:
                self.y_data.append(0)
            else:
                self.y_data.append(base + random.randint(-20, 20))

        # Initial Gauge Values
        if self.is_inactive_mode:
            self.temp_val = 0
            self.hum_val = 0
        else:
            self.temp_val = 28.5
            self.hum_val = 65
            if self.is_real:
                self.temp_val = self.real_data_ref.get('temp', 28.5)
                self.hum_val = 70

        # --- UI LAYOUT ---
        self.header_frame = tk.Frame(self.top, bg="#1e1e1e")
        self.header_frame.pack(fill="x", pady=10)
        
        tk.Label(self.header_frame, text=f"SENSOR ID: S-{self.r}-{self.c}", font=("Segoe UI", 18, "bold"), 
                 bg="#1e1e1e", fg="white").pack(side="left", padx=20)
        
        # STATUS TEXT LOGIC
        if self.is_inactive_mode:
            s_text = "STATUS: MODULE INACTIVE"
            s_fg = "#555555" # Grey
        else:
            s_text = "STATUS: NOMINAL"
            s_fg = "#00ff00"

        self.status_lbl = tk.Label(self.header_frame, text=s_text, font=("Consolas", 16, "bold"), 
                 bg="#1e1e1e", fg=s_fg)
        self.status_lbl.pack(side="right", padx=20)

        # GAUGES
        gauge_frame = tk.Frame(self.top, bg="#1e1e1e")
        gauge_frame.pack(fill="x", pady=5)
        self.gauge_canvas = tk.Canvas(gauge_frame, width=400, height=150, bg="#1e1e1e", highlightthickness=0)
        self.gauge_canvas.pack()
        self.draw_gauges()

        # CHART
        chart_frame = tk.Frame(self.top, bg="#1e1e1e")
        chart_frame.pack(fill="both", expand=True, padx=15, pady=5)
        self.setup_chart(chart_frame)

        self.update_loop()

    def draw_gauges(self):
        self.gauge_canvas.delete("all")
        self.draw_single_gauge(50, 20, "Temperature", self.temp_val, "°C", 0, 50)
        self.draw_single_gauge(250, 20, "Humidity", self.hum_val, "%", 0, 100)

    def draw_single_gauge(self, x, y, title, value, unit, min_v, max_v):
        self.gauge_canvas.create_arc(x, y, x+130, y+130, start=150, extent=-240, style="arc", outline="#333", width=10)
        
        # Only draw colored arc if value > 0
        if value > 0:
            angle = -240 * (value / max_v)
            color = "#00ff00"
            if title == "Temperature" and value > 35: color = "orange"
            if title == "Temperature" and value > 40: color = "red"
            self.gauge_canvas.create_arc(x, y, x+130, y+130, start=150, extent=angle, style="arc", outline=color, width=10)
        
        self.gauge_canvas.create_text(x+65, y+65, text=f"{value}{unit}", fill="white", font=("Arial", 16, "bold"))
        self.gauge_canvas.create_text(x+65, y+90, text=title, fill="#aaa", font=("Arial", 10))

    def setup_chart(self, parent):
        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.fig.patch.set_facecolor('#1e1e1e')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#2d2d2d')
        
        # If inactive, line is grey. Else cyan.
        c_color = "#555555" if self.is_inactive_mode else "#00d4ff"
        self.line, = self.ax.plot(self.x_data, self.y_data, color=c_color, linewidth=2)
        
        self.ax.set_title("Live Spoilage Risk (Real-Time)", color='white', fontsize=10)
        self.ax.grid(True, color='#444444', linestyle='--', linewidth=0.5)
        self.ax.tick_params(colors='#aaaaaa')
        self.ax.set_ylim(0, 1500)

        self.annot = self.ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="black", ec="white", alpha=0.9),
                            color="white", fontsize=9)
        self.annot.set_visible(False)

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.mpl_connect("motion_notify_event", self.hover)

        toolbar = NavigationToolbar2Tk(self.canvas, parent)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update_loop(self):
        # 1. GET NEW VALUE
        if self.is_inactive_mode:
            new_val = 0
            self.temp_val = 0
            self.hum_val = 0
        elif self.is_real:
            new_val = self.real_data_ref.get('gas', 0)
            self.temp_val = self.real_data_ref.get('temp', 0)
            self.hum_val = 70 + random.randint(-2, 2)
        else:
            # Active Simulated
            new_val = 300 + random.randint(-20, 20)
            if random.random() > 0.95: new_val += 100 
            self.temp_val = 28.5 + random.uniform(-0.5, 0.5)
            self.hum_val = 65 + random.randint(-1, 1)

        self.temp_val = round(self.temp_val, 1)

        # 2. UPDATE CHART ARRAYS
        self.y_data.pop(0)
        self.y_data.append(new_val)
        self.timestamps.pop(0)
        self.timestamps.append(datetime.now().strftime("%H:%M:%S"))

        self.line.set_ydata(self.y_data)
        
        # AUTO-SCALE LOGIC (Only if active)
        if not self.is_inactive_mode:
            current_max = max(self.y_data)
            if current_max > 1400:
                self.ax.set_ylim(0, current_max + 500)
            else:
                self.ax.set_ylim(0, 1500)
        
        self.canvas.draw()
        
        # 3. UPDATE COLORS / TEXT
        if self.is_inactive_mode:
            self.line.set_color("#555555")
            # Don't change text, keep it "INACTIVE"
        else:
            if new_val > 1000:
                self.line.set_color("#ff3333")
                status, s_col = "CRITICAL SPOILAGE", "#ff3333"
            elif new_val > 400:
                self.line.set_color("orange")
                status, s_col = "WARNING: VOC RISING", "orange"
            else:
                self.line.set_color("#00d4ff")
                status, s_col = "STATUS: NOMINAL", "#00ff00"
            self.status_lbl.config(text=status, fg=s_col)

        self.draw_gauges()
        self.top.after(1000, self.update_loop)

    def hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            cont, ind = self.line.contains(event)
            if cont:
                idx = ind["ind"][0]
                self.annot.xy = (self.x_data[idx], self.y_data[idx])
                text = f"Time: {self.timestamps[idx]}\nLevel: {self.y_data[idx]}"
                self.annot.set_text(text)
                self.annot.set_visible(True)
                self.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.canvas.draw_idle()

class AgroDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("AgroCops - ENTERPRISE MONITORING")
        self.root.geometry("1100x750")
        self.root.configure(bg="#121212")

        self.real_data = {'temp': 0.0, 'gas': 0}
        self.hardware_connected = False
        self.simulated_active_status = {} 

        # HEADER
        tk.Label(root, text="AGROCOPS CENTRAL COMMAND", font=("Segoe UI", 24, "bold"), bg="#121212", fg="#00ff00").pack(pady=20)
        
        # --- CHANGED: ALWAYS SHOW 'MONITORING' ---
        self.status_label = tk.Label(root, text="SYSTEM STATUS: MONITORING", font=("Consolas", 14), bg="#121212", fg="#00ff00")
        self.status_label.pack(pady=5)

        # GRID
        self.grid_frame = tk.Frame(root, bg="#121212")
        self.grid_frame.pack(expand=True, fill="both", padx=40, pady=20)
        
        self.sensors = {}
        for r in range(GRID_ROWS):
            self.grid_frame.rowconfigure(r, weight=1)
            for c in range(GRID_COLS):
                self.grid_frame.columnconfigure(c, weight=1)
                
                bg_col = "#333333"
                if (r,c) == LIVE_SENSOR_ID: bg_col = "#444444" 
                
                lbl = tk.Label(self.grid_frame, text=f"S-{r}-{c}", bg=bg_col, fg="white", 
                             width=6, height=2, font=("Arial", 9, "bold"))
                lbl.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
                lbl.bind("<Button-1>", lambda e, r=r, c=c: self.open_details(r, c))
                self.sensors[(r, c)] = lbl
                self.simulated_active_status[(r, c)] = False 

        self.running = True
        threading.Thread(target=self.simulate_others, daemon=True).start()
        threading.Thread(target=self.read_serial_data, daemon=True).start()

    def open_details(self, r, c):
        is_real = ((r, c) == LIVE_SENSOR_ID)
        is_active_sim = self.simulated_active_status.get((r, c), False)
        SensorPopup(self.root, r, c, is_real, self.real_data, self.hardware_connected, is_active_sim)

    def update_sensor(self, r, c, color):
        if (r, c) in self.sensors:
            self.sensors[(r, c)].configure(bg=color)
            if color in ["#333333", "#444444"]:
                self.simulated_active_status[(r, c)] = False
            else:
                self.simulated_active_status[(r, c)] = True

    def simulate_others(self):
        while self.running:
            for r in range(GRID_ROWS):
                for c in range(GRID_COLS):
                    if (r, c) == LIVE_SENSOR_ID: continue
                    if random.random() > 0.98:
                        self.update_sensor(r, c, "#F57C00")
                        self.root.after(800, lambda r=r, c=c: self.update_sensor(r, c, "#006400"))
            time.sleep(0.5) 

    def read_serial_data(self):
        print(f"\n--- ATTEMPTING CONNECTION TO {SERIAL_PORT} ---")
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            ser.dtr = False
            ser.rts = False
            time.sleep(0.1)
            ser.dtr = False 
            
            print("--- SUCCESS: CONNECTED! ---\n")
            self.hardware_connected = True
            # We don't change the main label text anymore, just keep it 'MONITORING'
            
            while self.running:
                if ser.in_waiting > 0:
                    try:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if line: print(f"RECEIVED: {line}")

                        if "Gas Level:" in line:
                            parts = line.split("|")
                            temp_str = parts[0].split(":")[1].strip()
                            self.real_data['temp'] = float(temp_str)
                            
                            gas_str = parts[1].split(":")[1].strip()
                            val = int(gas_str)
                            self.real_data['gas'] = val
                            if val == 0: continue 
                            
                            r, c = LIVE_SENSOR_ID
                            if val > 1000:
                                self.update_sensor(r, c, "#D32F2F")
                            elif val > 400:
                                self.update_sensor(r, c, "#F57C00")
                            else:
                                self.update_sensor(r, c, "#388E3C")
                    except Exception:
                        pass
        except Exception as e:
            print(f"❌ CONNECTION ERROR: {e}")
            self.hardware_connected = False
            
            # --- SILENT FAILOVER ---
            # 1. Main Status stays "SYSTEM STATUS: MONITORING" (Don't change it to red)
            # 2. Only S-3-4 turns Grey to show it is offline
            r, c = LIVE_SENSOR_ID
            self.update_sensor(r, c, "#444444")
            # -----------------------

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("AgroCops - Launch")
        self.root.geometry("600x400")
        self.root.configure(bg="#121212")
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width/2) - (600/2)
        y = (screen_height/2) - (400/2)
        root.geometry('%dx%d+%d+%d' % (600, 400, x, y))

        center_frame = tk.Frame(root, bg="#121212")
        center_frame.pack(expand=True)

        try:
            img_path = resource_path("logo.png")
            original_img = Image.open(img_path)
            resized_img = original_img.resize((150, 150), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(resized_img)
            
            logo_label = tk.Label(center_frame, image=self.logo_img, bg="#121212")
            logo_label.pack(pady=(20, 20))
        except Exception as e:
            tk.Label(center_frame, text="[LOGO MISSING]", fg="red", bg="#121212").pack(pady=50)

        tk.Label(center_frame, text="AGROCOPS CENTRAL COMMAND", font=("Segoe UI", 20, "bold"), 
                 bg="#121212", fg="#00ff00").pack()
        
        tk.Label(center_frame, text="Smart Harvest Security System", font=("Arial", 10), 
                 bg="#121212", fg="#aaaaaa").pack(pady=5)

        self.btn = tk.Button(center_frame, text="INITIALIZE SYSTEM", font=("Arial", 12, "bold"),
                  bg="#006400", fg="white", activebackground="#00ff00", 
                  relief="flat", width=20, height=2, command=self.launch_dashboard)
        self.btn.pack(pady=40)

    def launch_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        AgroDashboard(self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = SplashScreen(root)
    root.mainloop()
