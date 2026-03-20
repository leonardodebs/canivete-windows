import customtkinter
import os
import psutil
import socket
import platform
import subprocess
import threading
import time
import ctypes

# Configuração de Aparência
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

def is_admin():
    """Verifica se o usuário tem privilégios de administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def get_wmi_info(query_type):
    """Obtém info de hardware via PowerShell (mais moderno e confiável que wmic)"""
    commands = {
        "manufacturer": "(Get-CimInstance Win32_ComputerSystem).Manufacturer",
        "model": "(Get-CimInstance Win32_ComputerSystem).Model",
        "serial": "(Get-CimInstance Win32_BIOS).SerialNumber",
        "bios": "(Get-CimInstance Win32_BIOS).SMBIOSBIOSVersion"
    }
    
    cmd = f"powershell -ExecutionPolicy Bypass -Command \"{commands.get(query_type, '')}\""
    
    try:
        # Tenta executar via PowerShell
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('cp1252').strip()
        if output:
            return output
        return "Não Identificado"
    except Exception as e:
        # Fallback simples caso PowerShell falhe por algum motivo de política extrema
        return "Indisponível (Erro)"

# -----------------------------------------------------------------------------
# Módulo de Redes
# -----------------------------------------------------------------------------
class RedesFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        header = customtkinter.CTkLabel(header_frame, text="Network Troubleshooting Tool", font=customtkinter.CTkFont(size=22, weight="bold"))
        header.pack(side="left")

        admin_color = "#2ecc71" if is_admin() else "#e67e22"
        admin_text = "Admin: ATIVO" if is_admin() else "Admin: LIMITADO"
        self.admin_label = customtkinter.CTkLabel(header_frame, text=admin_text, text_color=admin_color, font=customtkinter.CTkFont(size=12))
        self.admin_label.pack(side="right")

        toolbar = customtkinter.CTkFrame(self)
        toolbar.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.target_entry = customtkinter.CTkEntry(toolbar, placeholder_text="Destino (ex: google.com)", width=250)
        self.target_entry.pack(side="left", padx=10, pady=10)

        self.ping_btn = customtkinter.CTkButton(toolbar, text="Ping", width=80, command=lambda: self.run_cmd("ping -n 4"))
        self.ping_btn.pack(side="left", padx=5)

        self.tracert_btn = customtkinter.CTkButton(toolbar, text="Tracert", width=80, command=lambda: self.run_cmd("tracert -d"))
        self.tracert_btn.pack(side="left", padx=5)

        self.nslookup_btn = customtkinter.CTkButton(toolbar, text="NSLookup", width=80, command=lambda: self.run_cmd("nslookup"))
        self.nslookup_btn.pack(side="left", padx=5)

        customtkinter.CTkLabel(toolbar, text="|", text_color="gray40").pack(side="left", padx=10)

        self.ipconfig_btn = customtkinter.CTkButton(toolbar, text="IPConfig", fg_color="#34495e", width=80, command=lambda: self.run_cmd("ipconfig /all", use_target=False))
        self.ipconfig_btn.pack(side="left", padx=5)

        self.flush_btn = customtkinter.CTkButton(toolbar, text="Flush DNS", fg_color="#c0392b", width=80, command=lambda: self.run_cmd("ipconfig /flushdns", use_target=False))
        self.flush_btn.pack(side="left", padx=5)

        self.output_text = customtkinter.CTkTextbox(self, font=("Consolas", 12), fg_color="#1a1a1a")
        self.output_text.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")

    def run_cmd(self, command, use_target=True):
        target = self.target_entry.get().strip()
        if use_target and not target: return
        full_command = f"{command} {target}" if use_target else command
        self.output_text.insert("end", f"\n--- EXECUTANDO: {full_command} ---\n")
        threading.Thread(target=self._execute_thread, args=(full_command,), daemon=True).start()

    def _execute_thread(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
        for line in process.stdout:
            self.output_text.insert("end", line)
            self.output_text.see("end")

    def update_console(self, text):
        self.output_text.insert("end", text)
        self.output_text.see("end")

# -----------------------------------------------------------------------------
# Módulo de Usuários
# -----------------------------------------------------------------------------
class UsuariosFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        header = customtkinter.CTkLabel(self, text="Gestão de Usuários e Acessos", font=customtkinter.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, padx=40, pady=(40, 20), sticky="nw")

        session_frame = customtkinter.CTkFrame(self)
        session_frame.grid(row=1, column=0, padx=40, pady=10, sticky="ew")
        
        try: current_user = os.getlogin()
        except: current_user = os.environ.get('USERNAME', 'N/A')
            
        is_adm = "SIM" if is_admin() else "NÃO"
        info_text = f"👤 Usuário: {current_user}  |  🛡️ Admin: {is_adm}"
        customtkinter.CTkLabel(session_frame, text=info_text, font=customtkinter.CTkFont(size=14, weight="bold")).pack(side="left", padx=20, pady=15)

        actions_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=2, column=0, padx=40, pady=10, sticky="ew")

        customtkinter.CTkButton(actions_frame, text="Listar Usuários Locais", command=lambda: self.run_cmd("net user")).pack(side="left", padx=(0, 10))
        customtkinter.CTkButton(actions_frame, text="Info Completa (WhoAmI)", fg_color="#34495e", command=lambda: self.run_cmd("whoami /all")).pack(side="left", padx=10)

        self.user_output = customtkinter.CTkTextbox(self, font=("Consolas", 12), fg_color="#1a1a1a")
        self.user_output.grid(row=3, column=0, padx=40, pady=(10, 40), sticky="nsew")

    def run_cmd(self, cmd):
        self.user_output.delete("0.0", "end")
        self.user_output.insert("end", f"--- {cmd.upper()} ---\n")
        threading.Thread(target=self._run_thread, args=(cmd,), daemon=True).start()

    def _run_thread(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
        for line in process.stdout:
            self.user_output.insert("end", line)
            self.user_output.see("end")

# -----------------------------------------------------------------------------
# Módulo de Pastas
# -----------------------------------------------------------------------------
class PastasFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        header = customtkinter.CTkLabel(self, text="Análise de Pastas e Permissões", font=customtkinter.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, padx=40, pady=(40, 20), sticky="nw")

        # Seleção de Caminho
        path_frame = customtkinter.CTkFrame(self)
        path_frame.grid(row=1, column=0, padx=40, pady=10, sticky="ew")
        
        self.path_entry = customtkinter.CTkEntry(path_frame, placeholder_text="C:\\Caminho\\da\\Pasta", width=400)
        self.path_entry.pack(side="left", padx=10, pady=15)
        
        customtkinter.CTkButton(path_frame, text="Selecionar...", width=100, command=self.browse_folder).pack(side="left", padx=5)

        # Ferramentas Rápidas
        tools_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        tools_frame.grid(row=2, column=0, padx=40, pady=10, sticky="ew")

        customtkinter.CTkButton(tools_frame, text="Calcular Tamanho", command=self.start_size_calc).pack(side="left", padx=(0, 10))
        customtkinter.CTkButton(tools_frame, text="Limpar TEMP", fg_color="#c0392b", command=self.clean_temp).pack(side="left", padx=10)

        # Output
        self.folder_output = customtkinter.CTkTextbox(self, font=("Consolas", 12), fg_color="#1a1a1a")
        self.folder_output.grid(row=3, column=0, padx=40, pady=(10, 40), sticky="nsew")

    def browse_folder(self):
        path = customtkinter.filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path.replace("/", "\\"))

    def start_size_calc(self):
        path = self.path_entry.get().strip()
        if not path or not os.path.exists(path): return
        self.folder_output.delete("0.0", "end")
        self.folder_output.insert("end", f"--- CALCULANDO TAMANHO: {path} ---\n")
        threading.Thread(target=self._calc_size_thread, args=(path,), daemon=True).start()

    def _calc_size_thread(self, path):
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            size_gb = total_size / (1024**3)
            self.folder_output.insert("end", f"\nTamanho Total: {size_gb:.2f} GB\n")
        except Exception as e:
            self.folder_output.insert("end", f"\nErro: {str(e)}")

    def clean_temp(self):
        path = os.environ.get('TEMP')
        self.folder_output.insert("end", f"\n--- LIMPANDO TEMP: {path} ---\n")
        for root, dirs, files in os.walk(path):
            for f in files:
                try: os.remove(os.path.join(root, f))
                except: pass
        self.folder_output.insert("end", "\nLImpeza concluída com sucesso.\n")

# -----------------------------------------------------------------------------
# Módulo de Inventário de Hardware
# -----------------------------------------------------------------------------
class HardwareFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        
        header = customtkinter.CTkLabel(self, text="Inventário de Hardware", font=customtkinter.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, padx=40, pady=(40, 30), sticky="nw")

        # Container de informações
        info_container = customtkinter.CTkFrame(self)
        info_container.grid(row=1, column=0, padx=40, pady=10, sticky="ew")
        
        # Consultas de Hardware (via PowerShell)
        model = get_wmi_info("model")
        serial = get_wmi_info("serial")
        bios = get_wmi_info("bios")
        manufacturer = get_wmi_info("manufacturer")
        
        # Estilização das Labels
        self.add_info_item(info_container, "🏢 Fabricante:", manufacturer, 0)
        self.add_info_item(info_container, "📦 Modelo do PC:", model, 1)
        self.add_info_item(info_container, "🔑 Serial / Service Tag:", serial, 2, highlight=True)
        self.add_info_item(info_container, "📑 Versão da BIOS:", bios, 3)

        # Botão de refresh
        customtkinter.CTkButton(self, text="Atualizar Inventário", command=lambda: master.select_frame("inventario")).grid(row=2, column=0, padx=40, pady=30, sticky="w")

    def add_info_item(self, container, label_text, value_text, row, highlight=False):
        color = "#3b8ed0" if highlight else "white"
        lbl = customtkinter.CTkLabel(container, text=label_text, font=customtkinter.CTkFont(size=14, weight="bold"))
        lbl.grid(row=row, column=0, padx=(20, 10), pady=15, sticky="w")
        
        val = customtkinter.CTkLabel(container, text=value_text, text_color=color, font=customtkinter.CTkFont(size=14))
        val.grid(row=row, column=1, padx=10, pady=15, sticky="w")

# -----------------------------------------------------------------------------
# Módulo de Sistema
# -----------------------------------------------------------------------------
class SistemaFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        
        header = customtkinter.CTkLabel(self, text="Monitor de Recursos", font=customtkinter.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, padx=40, pady=(40, 20), sticky="nw")

        self.os_label = customtkinter.CTkLabel(self, text=f"💻 {platform.node()} | {platform.system()} {platform.release()}", font=customtkinter.CTkFont(size=14))
        self.os_label.grid(row=1, column=0, padx=40, pady=5, sticky="nw")

        self.cpu_label = customtkinter.CTkLabel(self, text="Uso de CPU: 0%", font=customtkinter.CTkFont(size=14))
        self.cpu_label.grid(row=2, column=0, padx=40, pady=(20, 5), sticky="nw")
        self.cpu_progress = customtkinter.CTkProgressBar(self, width=500)
        self.cpu_progress.grid(row=3, column=0, padx=40, pady=5, sticky="nw")

        # RAM
        self.ram_label = customtkinter.CTkLabel(self, text="Uso de RAM: 0%", font=customtkinter.CTkFont(size=14))
        self.ram_label.grid(row=4, column=0, padx=40, pady=(20, 5), sticky="nw")
        self.ram_progress = customtkinter.CTkProgressBar(self, width=500)
        self.ram_progress.grid(row=5, column=0, padx=40, pady=5, sticky="nw")

        # Seção de Discos Locais
        customtkinter.CTkLabel(self, text="Armazenamento Local:", font=customtkinter.CTkFont(size=16, weight="bold")).grid(row=6, column=0, padx=40, pady=(30, 10), sticky="nw")
        
        self.disk_widgets = {} # {mountpoint: (label, progressbar)}
        self.render_disks()

        self.update_stats()

    def render_disks(self):
        """Detecta e cria widgets para todos os discos fixos"""
        try:
            row_index = 7
            for part in psutil.disk_partitions():
                if 'fixed' in part.opts or part.fstype:
                    try:
                        usage = psutil.disk_usage(part.mountpoint)
                        lbl = customtkinter.CTkLabel(self, text=f"Disco {part.mountpoint} (0%)", font=customtkinter.CTkFont(size=13))
                        lbl.grid(row=row_index, column=0, padx=50, pady=(10, 2), sticky="nw")
                        
                        prog = customtkinter.CTkProgressBar(self, width=450)
                        prog.grid(row=row_index + 1, column=0, padx=50, pady=(0, 10), sticky="nw")
                        
                        self.disk_widgets[part.mountpoint] = (lbl, prog)
                        row_index += 2
                    except: continue
        except: pass

    def update_stats(self):
        try:
            # CPU e RAM
            cpu = psutil.cpu_percent()
            self.cpu_label.configure(text=f"Uso de CPU: {cpu}%")
            self.cpu_progress.set(cpu / 100)
            
            ram = psutil.virtual_memory().percent
            self.ram_label.configure(text=f"Uso de RAM: {ram}%")
            self.ram_progress.set(ram / 100)

            # Discos
            for mount, (lbl, prog) in self.disk_widgets.items():
                try:
                    usage = psutil.disk_usage(mount)
                    free_gb = usage.free / (1024**3)
                    lbl.configure(text=f"Disco {mount} - {usage.percent}% usado ({free_gb:.1f} GB livres)")
                    prog.set(usage.percent / 100)
                except: pass
        except: pass
        self.after(2000, self.update_stats) # 2 segundos para o disco está ótimo

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Canivete Suiço para Windows")
        self.geometry("1100x700")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = customtkinter.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        customtkinter.CTkLabel(self.sidebar, text="🛠️ Ferramentas", font=customtkinter.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=20, pady=30)

        self.btns = {
            "redes": self._nav_btn("🔌 Redes", 1, "redes"),
            "usuarios": self._nav_btn("👥 Usuários", 2, "usuarios"),
            "pastas": self._nav_btn("📂 Pastas", 3, "pastas"),
            "sistema": self._nav_btn("🖥️ Sistema", 4, "sistema"),
            "inventario": self._nav_btn("📝 Inventário", 5, "inventario")
        }

        self.main_content = None
        self.select_frame("sistema")

    def _nav_btn(self, text, row, name):
        btn = customtkinter.CTkButton(self.sidebar, text=text, anchor="w", height=45, corner_radius=10, font=customtkinter.CTkFont(size=14, weight="bold"), command=lambda: self.select_frame(name))
        btn.grid(row=row, column=0, padx=15, pady=5, sticky="ew")
        return btn

    def select_frame(self, name):
        for b_name, btn in self.btns.items():
            if b_name == name: btn.configure(fg_color=("gray75", "gray25"), border_width=2, border_color="#3b8ed0")
            else: btn.configure(fg_color="transparent", border_width=0)

        if self.main_content: self.main_content.destroy()

        if name == "redes": self.main_content = RedesFrame(self, fg_color="transparent")
        elif name == "usuarios": self.main_content = UsuariosFrame(self, fg_color="transparent")
        elif name == "pastas": self.main_content = PastasFrame(self, fg_color="transparent")
        elif name == "sistema": self.main_content = SistemaFrame(self, fg_color="transparent")
        elif name == "inventario": self.main_content = HardwareFrame(self, fg_color="transparent")
        
        self.main_content.grid(row=0, column=1, sticky="nsew")

if __name__ == "__main__":
    app = App()
    app.mainloop()
