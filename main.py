import customtkinter as ctk
import subprocess
import threading
import shutil
import socket
import sys
import os
import re
import ctypes
import webbrowser
import traceback
import locale
import urllib.request
import time
import winreg 
from PIL import Image 

# --- 关键修复：设置 Windows 任务栏图标 ---
try:
    myappid = 'gradient.parallax.launcher.zero.v1' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

# --- 风格配置 ---
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("dark-blue") 

# 颜色盘
COLOR_BG = "#E3E3E3"       
COLOR_CARD = "#F5F5F5"     
COLOR_TEXT = "#2B2B2B"     

# 字体配置
FONT_CN_BOLD = ("Microsoft YaHei UI", 16, "bold")
FONT_CN_NORMAL = ("Microsoft YaHei UI", 12)
FONT_EN_PIXEL = ("Consolas", 10, "bold") 
FONT_EN_SUB = ("Arial", 9)
FONT_LOGO_BIG = ("Consolas", 16, "bold") 

DOWNLOAD_URL = "https://github.com/GradientHQ/parallax_win_cli/releases/latest/download/Parallax_Win_Setup.exe"

# --- 3D 像素字体生成器 ---
class PixelFont3D:
    def __init__(self):
        self.map = {
            'A': [" ### ", "#   #", "#####", "#   #", "#   #"], 'B': ["#### ", "#   #", "#### ", "#   #", "#### "],
            'C': [" ####", "#    ", "#    ", "#    ", " ####"], 'D': ["#### ", "#   #", "#   #", "#   #", "#### "],
            'E': [" #####", "#    ", "#### ", "#    ", "#####"], 'F': ["#####", "#    ", "#### ", "#    ", "#    "],
            'G': [" ####", "#    ", "#  ##", "#   #", " ####"], 'H': ["#   #", "#   #", "#####", "#   #", "#   #"],
            'I': ["###", " # ", " # ", " # ", "###"], 'J': ["  ###", "   # ", "   # ", "#  # ", " ##  "],
            'K': ["#   #", "#  # ", "###  ", "#  # ", "#   #"], 'L': ["#    ", "#    ", "#    ", "#    ", "#####"],
            'M': ["#   #", "## ##", "# # #", "#   #", "#   #"], 'N': ["#   #", "##  #", "# # #", "#  ##", "#   #"],
            'O': [" ### ", "#   #", "#   #", "#   #", " ### "], 'P': ["#### ", "#   #", "#### ", "#    ", "#    "],
            'Q': [" ### ", "#   #", "# # #", " ### ", "    #"], 'R': ["#### ", "#   #", "#### ", "#  # ", "#   #"],
            'S': [" ####", "#    ", " ### ", "    #", "#### "], 'T': ["#####", "  #  ", "  #  ", "  #  ", "  #  "],
            'U': ["#   #", "#   #", "#   #", "#   #", " ### "], 'V': ["#   #", "#   #", "#   #", " # # ", "  #  "],
            'W': ["#   #", "#   #", "# # #", "## ##", "#   #"], 'X': ["#   #", " # # ", "  #  ", " # # ", "#   #"],
            'Y': ["#   #", " # # ", "  #  ", "  #  ", "  #  "], 'Z': ["#####", "   # ", "  #  ", " #   ", "#####"],
            ' ': ["  "], '-': ["     ", "     ", " ### ", "     ", "     "],
            '0': [" ### ", "#  ##", "# # #", "##  #", " ### "], '1': ["  #  ", " ##  ", "  #  ", "  #  ", "#####"],
            '2': [" ### ", "#   #", "  ## ", " #   ", "#####"], '3': ["#### ", "    #", "  ## ", "    #", "#### "],
            '4': ["#  # ", "#  # ", "#####", "   # ", "   # "], '5': ["#####", "#    ", "#### ", "    #", "#### "],
            '6': [" ### ", "#    ", "#### ", "#   #", " ### "], '7': ["#####", "   # ", "  #  ", " #   ", "#    "],
            '8': [" ### ", "#   #", " ### ", "#   #", " ### "], '9': [" ### ", "#   #", " ####", "    #", " ### "]
        }

    def get_text_3d(self, text):
        text = text.upper()
        flat_grid = []
        char_height = 5
        for row_idx in range(char_height):
            row_str = ""
            for char in text:
                if char in self.map:
                    char_matrix = self.map[char]
                    if row_idx < len(char_matrix):
                        row_str += char_matrix[row_idx] + "  "
                    else:
                        row_str += " " * len(char_matrix[0]) + "  "
                else:
                    row_str += "     "
            flat_grid.append(row_str)
        if not flat_grid: return ""
        max_width = max(len(r) for r in flat_grid)
        flat_grid = [r.ljust(max_width) for r in flat_grid]
        output_lines = []
        width = len(flat_grid[0])
        height = len(flat_grid)
        for y in range(height + 1):
            line_str = ""
            for x in range(width + 1):
                is_solid = False
                if y < height and x < width:
                    if flat_grid[y][x] != ' ': is_solid = True
                is_shadow = False
                if y > 0 and x > 0:
                    if flat_grid[y-1][x-1] != ' ': is_shadow = True
                if is_solid: line_str += "█"
                elif is_shadow: line_str += "▒" 
                else: line_str += " "
            output_lines.append(line_str)
        return "\n".join(output_lines)

pixel_font = PixelFont3D()

class ParallaxLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Parallax") 
        self.geometry("1150x850") 
        self.resizable(True, True)
        self.configure(fg_color=COLOR_BG)

        if os.path.exists("app.ico"):
            try: self.iconbitmap("app.ico")
            except: pass

        self.process = None      
        self.chat_process = None 
        self.is_running = False
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.detected_peer_id = ctk.StringVar(value="等待生成 / Waiting...")
        self.chat_service_status = ctk.StringVar(value="未启动 / Stopped")
        
        self.show_loading_page("系统初始化中...\nINITIALIZING...")
        self.after(100, self.startup_sequence)

    # --- 图片加载 ---
    def load_image(self, path, size=(64, 64)):
        if os.path.exists(path):
            try: return ctk.CTkImage(Image.open(path), size=size)
            except: pass
        return None

    # --- UI 组件工厂 ---
    def create_pixel_header(self, parent, text, big=False):
        pixel_art = pixel_font.get_text_3d(text)
        font_style = FONT_LOGO_BIG if big else FONT_EN_PIXEL
        label = ctk.CTkLabel(parent, text=pixel_art, font=font_style, text_color="#333333", justify="left")
        label.pack(pady=(10, 0), anchor="w")
        return label

    def create_bilingual_label(self, parent, text_cn, text_en, text_color=None, font_size=16):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        l1 = ctk.CTkLabel(container, text=text_cn, font=("Microsoft YaHei UI", font_size, "bold"), text_color=text_color)
        l1.pack(anchor="w")
        if text_en:
            l2 = ctk.CTkLabel(container, text=text_en, font=("Arial", max(8, font_size-4)), text_color="gray")
            l2.pack(anchor="w")
        return container

    def create_bilingual_card(self, parent, title_cn, title_en, desc_cn, icon_text, icon_img_path, command, color_hover):
        card_frame = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=0, border_width=2, border_color="#B0B0B0")
        header = ctk.CTkFrame(card_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        img_obj = self.load_image(icon_img_path, size=(50, 50))
        if img_obj:
            ctk.CTkLabel(header, text="", image=img_obj).pack(side="left")
        else:
            ctk.CTkLabel(header, text=icon_text, font=("Arial", 45), text_color="#333").pack(side="left")
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=15)
        ctk.CTkLabel(title_box, text=title_cn, font=("Microsoft YaHei UI", 20, "bold"), text_color="#222").pack(anchor="w")
        ctk.CTkLabel(title_box, text=title_en, font=("Consolas", 12, "bold"), text_color="#666").pack(anchor="w")
        ctk.CTkLabel(card_frame, text=desc_cn, font=("Microsoft YaHei UI", 13), text_color="#555", wraplength=280, justify="left").pack(padx=20, pady=(0, 20), anchor="w")
        btn = ctk.CTkButton(card_frame, text="[ 启动 / START ]", font=("Consolas", 14, "bold"), 
                            fg_color="#444", hover_color="#222", text_color="white",
                            height=45, corner_radius=0, command=command)
        btn.pack(fill="x", padx=20, pady=(0, 20))
        return card_frame

    def startup_sequence(self):
        try:
            self.lift()
            self.attributes('-topmost', True)
            self.after(50, lambda: self.attributes('-topmost', False))
            if not self.is_admin(): self.show_admin_warning()
            else: self.start_async_check()
        except Exception as e: self.show_error_popup(str(e))

    def show_error_popup(self, msg):
        ctypes.windll.user32.MessageBoxW(0, msg, "System Error", 0x10)

    def is_admin(self):
        try: return ctypes.windll.shell32.IsUserAnAdmin()
        except: return False

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except: return "127.0.0.1"

    def clear_frame(self):
        for widget in self.winfo_children(): widget.destroy()

    def show_loading_page(self, message):
        self.clear_frame()
        loading_frame = ctk.CTkFrame(self, fg_color="transparent")
        loading_frame.pack(expand=True)
        pixel_art = pixel_font.get_text_3d("PARALLAX")
        ctk.CTkLabel(loading_frame, text=pixel_art, font=FONT_LOGO_BIG, text_color="#444").pack(pady=10)
        ctk.CTkLabel(loading_frame, text=message, font=FONT_CN_NORMAL, text_color="#333").pack(pady=10)
        self.loading_bar = ctk.CTkProgressBar(loading_frame, width=350, height=12, corner_radius=0, progress_color="#444")
        self.loading_bar.pack(pady=20)
        self.loading_bar.configure(mode="indeterminate")
        self.loading_bar.start()

    def start_async_check(self):
        threading.Thread(target=self._run_async_check_logic, daemon=True).start()

    # --- 核心检测逻辑 ---
    def _run_async_check_logic(self):
        # 1. 检测 WSL
        wsl_ready = self.check_wsl_ready()
        if not wsl_ready:
            self.after(0, self.show_wsl_setup_page)
            return

        # 2. 检测 Parallax CLI
        has_cli = shutil.which("parallax") is not None
        if not has_cli:
            self.after(0, self.show_download_guide_page)
            return

        # 3. 检测依赖 (使用 check 确保依赖正常)
        deps_ready = self.check_parallax_deps_strict()
        if not deps_ready:
            self.after(0, self.show_dependency_install_page)
            return

        # 4. All Pass
        self.after(0, self.show_role_selection)

    def kill_process_tree(self, proc):
        if proc and proc.poll() is None:
            try: subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except: pass

    def kill_current_process(self):
        self.kill_process_tree(self.chat_process)
        self.chat_process = None
        self.chat_service_status.set("未启动 / Stopped")
        self.kill_process_tree(self.process)
        self.process = None
        try: subprocess.Popen("wsl --shutdown", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
        except: pass
        self.is_running = False

    def on_closing(self):
        self.kill_current_process()
        self.destroy()
        sys.exit(0)

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        if hasattr(self, 'notification_label'):
            self.notification_label.configure(text="已复制 / Copied")
            self.after(2000, lambda: self.notification_label.configure(text=""))

    def check_wsl_ready(self):
        try: return subprocess.run("wsl -l -v", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08000000).returncode == 0
        except: return False

    # 严格依赖检测
    def check_parallax_deps_strict(self):
        try: 
            return subprocess.run("parallax check", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08000000).returncode == 0
        except: return False

    # --- 刷新环境变量 ---
    def refresh_path(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment') as key:
                user_path, _ = winreg.QueryValueEx(key, 'Path')
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment') as key:
                system_path, _ = winreg.QueryValueEx(key, 'Path')
            os.environ['PATH'] = f"{user_path};{system_path};{os.environ['PATH']}"
            self.append_log(">>> Environment variables refreshed.\n")
        except Exception as e:
            self.append_log(f"Refresh Env Failed: {e}\n")

    # --- 页面：WSL 安装 (Step 1) [修正版：显示输出] ---
    def show_wsl_setup_page(self):
        self.clear_frame()
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=(50, 30))
        self.create_pixel_header(header, "STEP 1: WSL", big=True).pack()
        ctk.CTkLabel(header, text="WSL 环境准备", font=FONT_CN_BOLD, text_color=COLOR_TEXT).pack(pady=(10, 0))

        content = ctk.CTkFrame(self, fg_color="white", border_width=2, border_color="#ccc", corner_radius=0)
        content.pack(padx=50, fill="x")
        ctk.CTkLabel(content, text="检测到系统未安装 WSL。这是运行本地 AI 的基础组件。\nWSL environment is missing.", font=FONT_CN_NORMAL, text_color="#d35400").pack(pady=20)
        
        self.log_textbox = ctk.CTkTextbox(content, width=600, height=150, font=FONT_EN_PIXEL, fg_color="#eee", text_color="#333")
        self.log_textbox.pack(pady=10)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        self.wsl_btn = ctk.CTkButton(btn_frame, text="🐧 一键安装 Ubuntu 22.04", font=("Microsoft YaHei UI", 14, "bold"),
                                     fg_color="#333", hover_color="#111", height=45, width=250, corner_radius=0,
                                     command=self.start_wsl_install_thread)
        self.wsl_btn.pack(side="left", padx=10)
        
        self.wsl_next_btn = ctk.CTkButton(btn_frame, text="验证并下一步 >", font=("Microsoft YaHei UI", 14, "bold"),
                                          fg_color="#27ae60", height=45, width=200, corner_radius=0, 
                                          command=self.verify_wsl_and_proceed) 
        self.wsl_next_btn.pack(side="left", padx=10)

    def verify_wsl_and_proceed(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", ">>> Verifying WSL status...\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
        self.update()
        
        if self.check_wsl_ready():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", ">>> WSL Check Passed! Moving next...\n")
            self.log_textbox.configure(state="disabled")
            self.after(1000, self.start_async_check) 
        else:
            ctypes.windll.user32.MessageBoxW(0, "未检测到 WSL 或 Ubuntu。\n如果您刚完成安装，请尝试重启电脑。", "Check Failed", 0x10)

    def start_wsl_install_thread(self):
        self.wsl_btn.configure(state="disabled")
        threading.Thread(target=self.run_wsl_install, daemon=True).start()

    def run_wsl_install(self):
        self.append_log(">>> Launching WSL Installer...\n")
        try:
            # 使用系统编码，捕获输出并显示在 UI
            sys_encoding = locale.getpreferredencoding()
            process = subprocess.Popen(
                "wsl --install -d Ubuntu-22.04", 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                encoding=sys_encoding, 
                errors='replace', 
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            for line in process.stdout:
                self.append_log(line)
            
            process.wait()
            
            if process.returncode == 0:
                self.append_log("\n>>> WSL Install command finished successfully.\n")
                self.append_log(">>> IMPORTANT: You may need to RESTART your computer.\n")
            else:
                self.append_log(f"\n>>> Install failed with code {process.returncode}.\n")
                self.wsl_btn.configure(state="normal")
                
        except Exception as e:
            self.append_log(f"Error: {e}\n")
            self.wsl_btn.configure(state="normal")

    # --- 页面：下载引导 (Step 2) ---
    def show_download_guide_page(self):
        self.clear_frame()
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=(50, 30))
        self.create_pixel_header(header, "STEP 2: CLI", big=True).pack()
        ctk.CTkLabel(header, text="安装基础程序", font=FONT_CN_BOLD, text_color=COLOR_TEXT).pack(pady=(10, 0))

        content = ctk.CTkFrame(self, fg_color="white", border_width=2, border_color="#ccc", corner_radius=0)
        content.pack(padx=50, fill="x")
        
        ctk.CTkLabel(content, text="检测到本机缺少 Parallax 基础服务。\nParallax CLI missing.", font=FONT_CN_NORMAL, text_color="#555").pack(pady=20)
        
        self.log_textbox = ctk.CTkTextbox(content, width=600, height=150, font=FONT_EN_PIXEL, fg_color="#eee", text_color="#333")
        self.log_textbox.pack(pady=10)
        self.append_log("Waiting for download...\n")
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        self.download_btn = ctk.CTkButton(btn_frame, text="⬇️ 自动下载并安装", font=("Microsoft YaHei UI", 14, "bold"), 
                      fg_color="#333", hover_color="#111", height=45, width=200, corner_radius=0,
                      command=self.start_download_thread)
        self.download_btn.pack(side="left", padx=10)
        
        self.next_btn = ctk.CTkButton(btn_frame, text="验证并下一步 >", font=("Microsoft YaHei UI", 14, "bold"),
                      fg_color="#27ae60", hover_color="#2ecc71", height=45, width=200, corner_radius=0,
                      command=self.verify_cli_and_proceed)
        self.next_btn.pack(side="left", padx=10)

    def verify_cli_and_proceed(self):
        self.refresh_path() 
        if shutil.which("parallax"):
            self.start_async_check()
        else:
            ctypes.windll.user32.MessageBoxW(0, "未检测到 parallax 命令。\n请确保安装程序已运行完毕。", "Check Failed", 0x10)

    def start_download_thread(self):
        self.download_btn.configure(state="disabled")
        threading.Thread(target=self.run_download_install, daemon=True).start()

    def run_download_install(self):
        save_path = os.path.join(os.environ["TEMP"], "Parallax_Win_Setup.exe")
        self.append_log(f">>> Downloading: {DOWNLOAD_URL}\n")
        try:
            def report_progress(block_num, block_size, total_size):
                if total_size > 0:
                    percent = int((block_num * block_size / total_size) * 100)
                    if percent % 10 == 0 and percent <= 100:
                        self.append_log(f"Downloading... {percent}%\n")

            urllib.request.urlretrieve(DOWNLOAD_URL, save_path, report_progress)
            self.append_log(">>> Download Complete. Launching Installer...\n")
            subprocess.Popen(save_path, shell=True)
        except Exception as e: self.append_log(f"Error: {e}\n")

    # --- 页面：依赖配置 (Step 3) ---
    def show_dependency_install_page(self):
        self.clear_frame()
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=(50, 30))
        self.create_pixel_header(header, "STEP 3: DEPS", big=True).pack()
        ctk.CTkLabel(header, text="配置 AI 环境", font=FONT_CN_BOLD, text_color=COLOR_TEXT).pack(pady=(10, 0))

        content = ctk.CTkFrame(self, fg_color="white", border_width=2, border_color="#ccc", corner_radius=0)
        content.pack(padx=50, fill="x")
        
        ctk.CTkLabel(content, text="基础程序已就绪。现在需要安装 AI 运行库 (torch 等)。\nEnvironment configuration required.", font=FONT_CN_NORMAL, text_color="#555").pack(pady=20)

        self.log_textbox = ctk.CTkTextbox(content, width=600, height=200, font=FONT_EN_PIXEL, fg_color="#eee", text_color="#333")
        self.log_textbox.pack(pady=20)
        
        self.install_btn = ctk.CTkButton(self, text="🚀 开始配置 / START", font=("Microsoft YaHei UI", 14, "bold"), 
                                         fg_color="#333", hover_color="#111", height=50, width=250, corner_radius=0,
                                         command=self.start_install_thread)
        self.install_btn.pack(pady=30)

    def start_install_thread(self):
        self.install_btn.configure(state="disabled")
        threading.Thread(target=self.run_install_command, daemon=True).start()

    def run_install_command(self):
        self.append_log(">>> Executing: parallax install\n")
        self.append_log(">>> This may take a while (installing python env)...\n")
        try:
            process = subprocess.Popen("parallax install", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding=locale.getpreferredencoding(), errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            for line in process.stdout: self.append_log(line)
            process.wait()
            
            if process.returncode == 0:
                self.append_log("\n>>> Configuration Complete!\n")
                self.after(2000, self.start_async_check) 
            else:
                self.append_log("\n[Error] Installation failed.\n")
                self.install_btn.configure(state="normal")
        except Exception as e:
            self.append_log(f"Error: {e}\n")

    def append_log(self, text):
        try:
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", text)
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")
        except: pass

    # --- 角色选择 (保持不变) ---
    def show_role_selection(self):
        self.clear_frame()
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(pady=(50, 30))
        self.create_pixel_header(title_frame, "PARALLAX", big=True).pack()
        ctk.CTkLabel(title_frame, text="选择本机功能模式", font=FONT_CN_BOLD, text_color="gray").pack()
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(expand=True)
        self.create_bilingual_card(cards, "主脑节点", "MASTER NODE", 
                                   "作为 AI 核心，提供运算调度与服务。\nCore scheduling & Service provider.", 
                                   "🧠", "master.png", 
                                   lambda: self.show_running_page("master"), "#DDDDDD").pack(side="left", padx=20)
        self.create_bilingual_card(cards, "算力节点", "WORKER NODE", 
                                   "贡献显卡算力，加入集群进行计算。\nContribute GPU power to cluster.", 
                                   "💪", "worker.png",
                                   lambda: self.show_running_page("worker"), "#DDDDDD").pack(side="left", padx=20)

    # --- 运行界面 (保持不变) ---
    def show_running_page(self, role):
        self.clear_frame()
        self.role = role
        nav = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="white", border_width=0)
        nav.pack(fill="x", side="top")
        back_btn = ctk.CTkButton(nav, text="🛑 停止 / STOP", width=120, height=35, 
                                 fg_color="#c0392b", hover_color="#e74c3c", font=("Consolas", 12, "bold"), corner_radius=0,
                                 command=self.stop_and_back)
        back_btn.pack(side="left", padx=20, pady=12)
        role_txt = "MASTER" if role == "master" else "WORKER"
        self.create_pixel_header(nav, role_txt).pack(side="left", padx=20)
        self.notification_label = ctk.CTkLabel(nav, text="", text_color="#27ae60", font=("Microsoft YaHei UI", 12, "bold"))
        self.notification_label.pack(side="right", padx=20)
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        left_col = ctk.CTkFrame(content, fg_color="#111", corner_radius=0, border_width=2, border_color="#333")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 20))
        ctk.CTkLabel(left_col, text=" SYSTEM LOGS ", font=("Consolas", 12), fg_color="#333", text_color="white", corner_radius=0).pack(anchor="w")
        self.console_out = ctk.CTkTextbox(left_col, font=("Consolas", 10), fg_color="#111", text_color="#00FF00")
        self.console_out.pack(fill="both", expand=True, padx=2, pady=2)

        if role == "master":
            right_col = ctk.CTkFrame(content, width=380, fg_color="white", corner_radius=0, border_width=2, border_color="#ccc")
            right_col.pack(side="right", fill="y")
            right_col.pack_propagate(False)
            ctk.CTkLabel(right_col, text=" STATUS INFO ", font=("Consolas", 12), fg_color="#ccc", text_color="#333", corner_radius=0).pack(fill="x", anchor="w")
            info_box = ctk.CTkFrame(right_col, fg_color="transparent")
            info_box.pack(fill="x", padx=15, pady=15)
            local_ip = self.get_local_ip()
            self.create_bilingual_label(info_box, "本机 IP / Local IP", local_ip, "#333", 12).pack(fill="x", pady=5)
            self.create_bilingual_label(info_box, "节点 ID / Peer ID", "", "#333", 12).pack(fill="x", pady=(10,0))
            self.peer_id_btn = ctk.CTkButton(info_box, textvariable=self.detected_peer_id, 
                                           fg_color="#eee", text_color="#333", hover_color="#ddd",
                                           font=("Consolas", 10), height=30, corner_radius=0, state="disabled")
            self.peer_id_btn.pack(fill="x", pady=5)
            self.peer_id_btn.bind("<Button-1>", lambda e: self.copy_to_clipboard(self.detected_peer_id.get()) if "Wait" not in self.detected_peer_id.get() else None)
            ctk.CTkButton(info_box, text="🌐 打开管理后台 / Dashboard", font=("Microsoft YaHei UI", 12), 
                          fg_color="#2c3e50", hover_color="#34495e", height=40, corner_radius=0,
                          command=lambda: webbrowser.open("http://localhost:3001")).pack(fill="x", pady=15)
            ctk.CTkLabel(right_col, text=" SERVICES ", font=("Consolas", 12), fg_color="#ccc", text_color="#333", corner_radius=0).pack(fill="x", anchor="w")
            svc_box = ctk.CTkFrame(right_col, fg_color="transparent")
            svc_box.pack(fill="x", padx=15, pady=15)
            self.chat_btn = ctk.CTkButton(svc_box, text="📱 开启局域网共享 / Start Chat", 
                                        font=("Microsoft YaHei UI", 12, "bold"), height=50, corner_radius=0,
                                        fg_color="#8e44ad", hover_color="#9b59b6",
                                        image=self.load_image("chat.png", (24,24)),
                                        state="disabled", command=self.toggle_chat_server)
            self.chat_btn.pack(fill="x", pady=5)
            ctk.CTkLabel(svc_box, text="Allow LAN devices to access AI service.\n允许局域网设备访问。", 
                         font=("Arial", 10), text_color="gray", justify="left").pack(anchor="w")
            self.chat_link_label = ctk.CTkLabel(svc_box, textvariable=self.chat_service_status, text_color="#d35400", font=("Consolas", 10))
            self.chat_link_label.pack(pady=5, anchor="w")

        if role == "master":
            self.console_out.insert("0.0", "Initializing Master Node...\n")
            self.start_parallax_process("parallax run --host 0.0.0.0")
            
        elif role == "worker":
            self.console_out.destroy() 
            self.console_out = ctk.CTkTextbox(left_col, font=("Consolas", 10), fg_color="#111", text_color="#00FF00")
            self.console_out.pack(fill="both", expand=True, padx=2, pady=2)
            self.console_out.insert("0.0", "WAITING FOR CONFIGURATION...\n")
            right_col = ctk.CTkFrame(content, width=350, fg_color="white", corner_radius=0, border_width=2, border_color="#ccc")
            right_col.pack(side="right", fill="y")
            right_col.pack_propagate(False)
            ctk.CTkLabel(right_col, text=" CONNECTION ", font=("Consolas", 12), fg_color="#ccc", text_color="#333", corner_radius=0).pack(fill="x", anchor="w")
            conn_box = ctk.CTkFrame(right_col, fg_color="transparent")
            conn_box.pack(fill="x", padx=15, pady=15)
            self.create_bilingual_label(conn_box, "局域网自动发现", "LAN Auto-Discovery", "#333", 14).pack(anchor="w")
            ctk.CTkButton(conn_box, text="自动加入 / Auto Join", height=40, corner_radius=0, font=FONT_CN_BOLD,
                          fg_color="#2980b9", hover_color="#3498db",
                          command=lambda: self.start_connect_process(left_col, role, "")).pack(fill="x", pady=10)
            ctk.CTkLabel(conn_box, text="- OR -", text_color="gray").pack(pady=10)
            self.create_bilingual_label(conn_box, "指定 ID 连接 (公网)", "Connect by Peer ID", "#333", 14).pack(anchor="w")
            self.ip_entry = ctk.CTkEntry(conn_box, placeholder_text="Paste ID here...", height=35, corner_radius=0, border_color="#999")
            self.ip_entry.pack(fill="x", pady=5)
            ctk.CTkButton(conn_box, text="连接 / Connect", height=40, corner_radius=0, font=FONT_CN_BOLD,
                          fg_color="#27ae60", hover_color="#2ecc71",
                          command=lambda: self.start_connect_process(left_col, role, self.ip_entry.get())).pack(fill="x", pady=10)

    def toggle_chat_server(self):
        if self.chat_process:
            self.kill_process_tree(self.chat_process)
            self.chat_process = None
            self.chat_service_status.set("未启动 / Stopped")
            self.chat_btn.configure(text="📱 开启局域网共享 / Start Chat", fg_color="#8e44ad")
        else:
            cmd = "parallax chat --host 0.0.0.0"
            self.console_log(f"\n[System] Starting Chat Server...\nCMD: {cmd}\n")
            try:
                sys_encoding = locale.getpreferredencoding()
                self.chat_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding=sys_encoding, errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
                self.chat_btn.configure(text="🛑 停止共享服务 / Stop", fg_color="#c0392b")
                link = f"http://{self.get_local_ip()}:3002"
                self.chat_service_status.set(f"Running at: {link}")
            except Exception as e:
                self.console_log(f"\n❌ Error: {e}\n")

    def start_connect_process(self, log_parent, role, raw_input):
        clean_address = raw_input.strip().split()[-1] if raw_input else ""
        for w in log_parent.winfo_children(): w.destroy()
        self.console_out = ctk.CTkTextbox(log_parent, font=("Consolas", 10), fg_color="#111", text_color="#00FF00")
        self.console_out.pack(fill="both", expand=True)
        cmd = f"parallax join -s {clean_address}" if clean_address else "parallax join"
        self.start_parallax_process(cmd)

    def start_parallax_process(self, cmd):
        if self.is_running: return
        self.is_running = True
        threading.Thread(target=self._run_process, args=(cmd,), daemon=True).start()

    def _run_process(self, cmd):
        self.console_log(f">>> Service Start: {cmd}\n")
        browser_opened = False
        sys_encoding = locale.getpreferredencoding()
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding=sys_encoding, errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            self.process = process
            for line in self.process.stdout:
                self.console_log(line)
                if self.role == 'master':
                    match = re.search(r"peer id:\s*([a-zA-Z0-9]+)", line, re.IGNORECASE)
                    if match:
                        found_id = match.group(1)
                        self.detected_peer_id.set(found_id)
                        self.peer_id_btn.configure(state="normal", fg_color="#eee", text=f"{found_id}", text_color="#333")
                        if hasattr(self, 'chat_btn'): self.chat_btn.configure(state="normal")
                    if not browser_opened and ("3001" in line or "Uvicorn running" in line):
                        self.after(1500, lambda: webbrowser.open("http://localhost:3001"))
                        browser_opened = True
            self.process.wait()
            self.is_running = False
            self.console_log("\n>>> Process Exited.\n")
        except Exception as e:
            self.console_log(f"\n❌ Error: {e}")
            self.is_running = False

    def console_log(self, text):
        try:
            self.console_out.configure(state="normal")
            self.console_out.insert("end", text)
            self.console_out.see("end")
            self.console_out.configure(state="disabled")
        except: pass

    def stop_and_back(self):
        self.show_role_selection()
        threading.Thread(target=self.kill_current_process, daemon=True).start()

    def show_admin_warning(self):
        self.clear_frame()
        container = ctk.CTkFrame(self, fg_color="white", corner_radius=10, border_width=2, border_color="#e0e0e0")
        container.pack(expand=True, padx=20, pady=20)
        ctk.CTkLabel(container, text="⚠️ 权限不足", font=("Microsoft YaHei UI", 24, "bold"), text_color="#c0392b").pack(pady=(30, 5))
        ctk.CTkLabel(container, text="Permission Denied", font=("Arial", 14), text_color="gray").pack(pady=(0, 20))
        ctk.CTkLabel(container, text="Parallax 需要系统权限来管理网络和后台服务\n请右键本程序 -> 以管理员身份运行", font=("Microsoft YaHei UI", 14)).pack(pady=10)
        ctk.CTkButton(container, text="退出程序\nExit", height=50, command=self.on_closing).pack(pady=20, padx=50, fill="x")

if __name__ == "__main__":
    try:
        app = ParallaxLauncher()
        app.mainloop()
    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0, traceback.format_exc(), "Error", 0x10)