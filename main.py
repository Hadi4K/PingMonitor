import customtkinter as ctk
import subprocess
import threading
import queue
import re
import platform
import urllib.request
from pathlib import Path

APP_NAME = "Ping Monitor"
APP_VERSION = "1.0.0"


# =========================================================
# SETTINGS
# =========================================================

DEFAULT_TARGETS = {
    "Google": "8.8.8.8",
    "Cloudflare": "1.1.1.1",
    "Quad9": "9.9.9.9",
    "OpenDNS": "208.67.222.222",

    "MyTeamSpeak": "46.38.138.68",
    "Soft98": "79.127.127.35",
    "Server Minecraft": "185.141.105.216",

    # Example public CS2 dedicated server
    "CS2 Server": "138.201.131.228",
}

GOOD_PING = 50
MEDIUM_PING = 100

BG = "#08080D"
PANEL = "#111119"
PANEL_2 = "#171720"

PURPLE = "#8B5CF6"
PURPLE_DARK = "#6D28D9"

WHITE = "#F5F5F7"
GRAY = "#8A8A98"

GREEN = "#22C55E"
YELLOW = "#EAB308"
RED = "#EF4444"


# =========================================================
# APP
# =========================================================

class PingMonitor:

    def __init__(self, root):

        self.root = root

        self.running = False
        self.process = None

        self.result_queue = queue.Queue()

        self.sent = 0
        self.received = 0

        self.log_visible = False

        self.setup_window()
        self.create_ui()

        self.root.after(100, self.process_queue)

        # Get public IP in background
        threading.Thread(
            target=self.get_public_ip,
            daemon=True
        ).start()

    # =====================================================
    # WINDOW
    # =====================================================

    def setup_window(self):

        self.root.title(f"{APP_NAME} v{APP_VERSION}")

        self.root.geometry("950x670")

        self.root.minsize(950, 670)
        self.root.maxsize(950, 670)

        self.root.configure(
            fg_color=BG
        )

        # App icon (works from source and from the PyInstaller bundle).
        try:
            base_dir = Path(__file__).resolve().parent
            icon_path = base_dir / "PingMonitor.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass

    # =====================================================
    # UI
    # =====================================================

    def create_ui(self):

        # Main container
        self.main = ctk.CTkFrame(
            self.root,
            fg_color=BG,
            corner_radius=20
        )

        self.main.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        # =================================================
        # LEFT SIDE
        # =================================================

        self.left = ctk.CTkFrame(
            self.main,
            fg_color=BG,
            corner_radius=18
        )

        self.left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(15, 8),
            pady=15
        )

        # Title
        ctk.CTkLabel(
            self.left,
            text="PING MONITOR",
            font=("Segoe UI", 25, "bold"),
            text_color=WHITE
        ).pack(
            pady=(10, 2)
        )

        ctk.CTkLabel(
            self.left,
            text="Real-time network latency monitor",
            font=("Segoe UI", 10),
            text_color=GRAY
        ).pack(
            pady=(0, 20)
        )

        # =================================================
        # TARGET
        # =================================================

        target_frame = ctk.CTkFrame(
            self.left,
            fg_color=PANEL,
            corner_radius=15,
            border_width=1,
            border_color=PURPLE_DARK
        )

        target_frame.pack(
            fill="x",
            padx=5
        )

        ctk.CTkLabel(
            target_frame,
            text="TARGET",
            font=("Segoe UI", 9, "bold"),
            text_color=GRAY
        ).pack(
            anchor="w",
            padx=15,
            pady=(10, 3)
        )

        self.target_var = ctk.StringVar(
            value="Google — 8.8.8.8"
        )

        self.target_menu = ctk.CTkComboBox(
            target_frame,
            values=[
                f"{name} — {ip}"
                for name, ip in DEFAULT_TARGETS.items()
            ],
            variable=self.target_var,
            state="readonly",
            height=38,
            corner_radius=10,
            border_width=1,
            border_color=PURPLE_DARK,
            fg_color=PANEL_2,
            button_color=PURPLE_DARK,
            button_hover_color=PURPLE,
            dropdown_fg_color=PANEL_2,
            dropdown_hover_color=PURPLE_DARK,
            text_color=WHITE,
            font=("Segoe UI", 11)
        )

        self.target_menu.pack(
            fill="x",
            padx=10,
            pady=(0, 12)
        )

        # Custom IP
        self.custom_ip = ctk.CTkEntry(
            target_frame,
            placeholder_text="Or enter a custom IP...",
            height=35,
            corner_radius=10,
            border_color="#292936",
            fg_color="#0D0D13",
            text_color=WHITE
        )

        self.custom_ip.pack(
            fill="x",
            padx=10,
            pady=(0, 12)
        )

        # =================================================
        # PING DISPLAY
        # =================================================

        self.ping_frame = ctk.CTkFrame(
            self.left,
            fg_color=PANEL,
            corner_radius=18,
            border_width=1,
            border_color=PURPLE
        )

        self.ping_frame.pack(
            fill="x",
            padx=5,
            pady=15
        )

        ctk.CTkLabel(
            self.ping_frame,
            text="CURRENT PING",
            font=("Segoe UI", 10, "bold"),
            text_color=GRAY
        ).pack(
            pady=(13, 0)
        )

        self.ping_label = ctk.CTkLabel(
            self.ping_frame,
            text="—",
            font=("Segoe UI", 40, "bold"),
            text_color=WHITE
        )

        self.ping_label.pack()

        self.status_label = ctk.CTkLabel(
            self.ping_frame,
            text="READY",
            font=("Segoe UI", 10, "bold"),
            text_color=GRAY
        )

        self.status_label.pack(
            pady=(0, 13)
        )

        # =================================================
        # STATS
        # =================================================

        stats = ctk.CTkFrame(
            self.left,
            fg_color=BG
        )

        stats.pack(
            fill="x",
            padx=1
        )

        self.loss_label = self.create_stat(
            stats,
            "PACKET LOSS",
            "0%"
        )

        self.sent_label = self.create_stat(
            stats,
            "PACKETS SENT",
            "0"
        )

        self.received_label = self.create_stat(
            stats,
            "RECEIVED",
            "0"
        )

        # =================================================
        # BUTTONS
        # =================================================

        buttons = ctk.CTkFrame(
            self.left,
            fg_color=BG
        )

        buttons.pack(
            pady=18
        )

        self.start_button = ctk.CTkButton(
            buttons,
            text="START",
            command=self.start_ping,
            width=160,
            height=55,
            corner_radius=14,
            fg_color=PANEL_2,
            hover_color=PURPLE_DARK,
            border_width=1,
            border_color=PURPLE,
            font=("Segoe UI", 20, "bold")
        )

        self.start_button.pack(
            side="left",
            padx=5
        )

        self.stop_button = ctk.CTkButton(
            buttons,
            text="STOP",
            command=self.stop_ping,
            width=160,
            height=55,
            corner_radius=14,
            fg_color=PANEL_2,
            hover_color=PURPLE_DARK,
            border_width=1,
            border_color=PURPLE,
            font=("Segoe UI", 20, "bold")
        )

        self.stop_button.pack(
            side="left",
            padx=5
        )

        # =================================================
        # PUBLIC IP
        # =================================================

        public_frame = ctk.CTkFrame(
            self.left,
            fg_color=PANEL,
            corner_radius=12
        )

        public_frame.pack(
            fill="x",
            padx=5,
            pady=(0, 5)
        )

        ctk.CTkLabel(
            public_frame,
            text="PUBLIC IP",
            font=("Segoe UI", 12, "bold"),
            text_color=GRAY
        ).pack(
            side="left",
            padx=(12, 5),
            pady=9
        )

        self.public_ip_label = ctk.CTkLabel(
            public_frame,
            text="Checking...",
            font=("Segoe UI", 16, "bold"),
            text_color=WHITE
        )

        self.public_ip_label.pack(
            side="left"
        )

        # =================================================
        # RIGHT LOG PANEL
        # =================================================

        self.log_panel = ctk.CTkFrame(
            self.main,
            fg_color="#050508",
            corner_radius=16,
            border_width=1,
            border_color="#282832",
            width=270
        )

        self.log_panel.pack(
            side="right",
            fill="y",
            padx=(8, 15),
            pady=15
        )

        self.log_panel.pack_propagate(False)

        # Header
        header = ctk.CTkFrame(
            self.log_panel,
            fg_color="#0B0B10",
            corner_radius=12
        )

        header.pack(
            fill="x",
            padx=8,
            pady=8
        )

        ctk.CTkLabel(
            header,
            text="LIVE LOG",
            font=("Consolas", 10, "bold"),
            text_color=GREEN
        ).pack(
            side="left",
            padx=10,
            pady=8
        )

        self.log_box = ctk.CTkTextbox(
            self.log_panel,
            fg_color="#050508",
            text_color=GREEN,
            border_width=0,
            corner_radius=10,
            font=("Consolas", 20),
            scrollbar_button_color="#24242D",
            scrollbar_button_hover_color=PURPLE_DARK
        )

        self.log_box.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(0, 8)
        )

        self.log_box.configure(
            state="disabled"
        )

        # Initially visible
        self.add_log("PING MONITOR")
        self.add_log("----------------")
        self.add_log("Waiting for start...")

    # =====================================================
    # STAT BOX
    # =====================================================

    def create_stat(self, parent, title, value):

        frame = ctk.CTkFrame(
            parent,
            fg_color=PANEL,
            corner_radius=12,
            border_width=1,
            border_color="#282832"
        )

        frame.pack(
            side="left",
            expand=True,
            fill="x",
            padx=3
        )

        ctk.CTkLabel(
            frame,
            text=title,
            font=("Segoe UI", 8, "bold"),
            text_color=GRAY
        ).pack(
            pady=(9, 1)
        )

        label = ctk.CTkLabel(
            frame,
            text=value,
            font=("Segoe UI", 13, "bold"),
            text_color=WHITE
        )

        label.pack(
            pady=(0, 9)
        )

        return label

    # =====================================================
    # START
    # =====================================================

    def start_ping(self):

        if self.running:
            return

        custom = self.custom_ip.get().strip()

        if custom:
            ip = custom
            target_name = "Custom"
        else:
            selected = self.target_var.get()

            if " — " in selected:
                target_name, ip = selected.split(
                    " — ",
                    1
                )
            else:
                ip = selected
                target_name = "Custom"

        # Reset counters
        self.sent = 0
        self.received = 0

        self.sent_label.configure(text="0")
        self.received_label.configure(text="0")
        self.loss_label.configure(text="0%")

        self.ping_label.configure(
            text="—",
            text_color=WHITE
        )

        self.status_label.configure(
            text="CONNECTING...",
            text_color=YELLOW
        )

        self.start_button.configure(
            text="RUNNING",
            text_color=GREEN
        )

        self.running = True

        self.clear_log()

        self.add_log(f"TARGET: {target_name}")
        self.add_log(f"IP: {ip}")
        self.add_log("----------------")

        threading.Thread(
            target=self.ping_loop,
            args=(ip,),
            daemon=True
        ).start()

    # =====================================================
    # STOP
    # =====================================================

    def stop_ping(self):

        self.running = False

        if self.process:

            try:
                self.process.kill()
            except:
                pass

            self.process = None

        # Reset counters
        self.sent = 0
        self.received = 0

        self.sent_label.configure(text="0")
        self.received_label.configure(text="0")
        self.loss_label.configure(text="0%")

        self.start_button.configure(
            text="START",
            text_color=WHITE
        )

        self.status_label.configure(
            text="STOPPED",
            text_color=GRAY
        )

        self.add_log("----------------")
        self.add_log("PING STOPPED")

    # =====================================================
    # PING LOOP
    # =====================================================

    def ping_loop(self, ip):

        system = platform.system().lower()

        if system == "windows":

            command = [
                "ping",
                ip,
                "-t"
            ]

        else:

            command = [
                "ping",
                ip
            ]

        try:

            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                creationflags=(subprocess.CREATE_NO_WINDOW if system == "windows" else 0),
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            for line in self.process.stdout:

                if not self.running:
                    break

                line = line.strip()

                # Ping successful
                match = re.search(
                    r"(?:time[=<])\s*(\d+)\s*ms",
                    line,
                    re.IGNORECASE
                )

                if match:

                    ping = int(
                        match.group(1)
                    )

                    self.result_queue.put(
                        ("success", ping)
                    )

                elif (
                    "Request timed out" in line
                    or
                    "Destination host unreachable" in line
                ):

                    self.result_queue.put(
                        ("timeout", None)
                    )

        except Exception as error:

            self.result_queue.put(
                ("error", str(error))
            )

    # =====================================================
    # QUEUE
    # =====================================================

    def process_queue(self):

        try:

            while True:

                result = self.result_queue.get_nowait()

                if result[0] == "success":

                    self.handle_ping(
                        result[1]
                    )

                elif result[0] == "timeout":

                    self.handle_timeout()

                elif result[0] == "error":

                    self.handle_error(
                        result[1]
                    )

        except queue.Empty:
            pass

        self.root.after(
            100,
            self.process_queue
        )

    # =====================================================
    # SUCCESS
    # =====================================================

    def handle_ping(self, ping):

        if not self.running:
            return

        self.sent += 1
        self.received += 1

        loss = (
            (self.sent - self.received)
            / self.sent
        ) * 100

        self.sent_label.configure(
            text=str(self.sent)
        )

        self.received_label.configure(
            text=str(self.received)
        )

        self.loss_label.configure(
            text=f"{loss:.0f}%"
        )

        # Determine color
        if ping <= GOOD_PING:

            color = GREEN
            status = "GOOD"

        elif ping <= MEDIUM_PING:

            color = YELLOW
            status = "MEDIUM"

        else:

            color = RED
            status = "HIGH"

        self.ping_label.configure(
            text=f"{ping} ms",
            text_color=color
        )

        self.status_label.configure(
            text=status,
            text_color=color
        )

        # Log
        self.add_log(
            f"{ping:>4} ms",
            color
        )

    # =====================================================
    # TIMEOUT
    # =====================================================

    def handle_timeout(self):

        if not self.running:
            return

        self.sent += 1

        loss = (
            (self.sent - self.received)
            / self.sent
        ) * 100

        self.sent_label.configure(
            text=str(self.sent)
        )

        self.received_label.configure(
            text=str(self.received)
        )

        self.loss_label.configure(
            text=f"{loss:.0f}%"
        )

        self.ping_label.configure(
            text="TIMEOUT",
            text_color=RED
        )

        self.status_label.configure(
            text="PACKET LOST",
            text_color=RED
        )

        self.add_log(
            "TIMEOUT",
            RED
        )

    # =====================================================
    # ERROR
    # =====================================================

    def handle_error(self, error):

        self.stop_ping()

        self.ping_label.configure(
            text="ERROR",
            text_color=RED
        )

        self.status_label.configure(
            text="CHECK IP",
            text_color=RED
        )

        self.add_log(
            "ERROR",
            RED
        )

    # =====================================================
    # LOG
    # =====================================================

    def add_log(self, text, color=None):

        if color is None:
            color = GREEN

        self.log_box.configure(
            state="normal"
        )

        tag = f"tag_{color}"

        self.log_box.tag_config(
            tag,
            foreground=color
        )

        self.log_box.insert(
            "end",
            text + "\n",
            tag
        )

        self.log_box.see(
            "end"
        )

        self.log_box.configure(
            state="disabled"
        )

    def clear_log(self):

        self.log_box.configure(
            state="normal"
        )

        self.log_box.delete(
            "1.0",
            "end"
        )

        self.log_box.configure(
            state="disabled"
        )

    # =====================================================
    # PUBLIC IP
    # =====================================================

    def get_public_ip(self):

        try:

            public_ip = urllib.request.urlopen(
                "https://api.ipify.org",
                timeout=5
            ).read().decode()

            self.root.after(
                0,
                lambda: self.public_ip_label.configure(
                    text=public_ip
                )
            )

        except:

            self.root.after(
                0,
                lambda: self.public_ip_label.configure(
                    text="Unavailable"
                )
            )

    # =====================================================
    # CLOSE
    # =====================================================

    def on_close(self):

        self.running = False

        if self.process:

            try:
                self.process.kill()
            except:
                pass

        self.root.destroy()


# =========================================================
# START APP
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()

app = PingMonitor(root)

root.protocol(
    "WM_DELETE_WINDOW",
    app.on_close
)

root.mainloop()