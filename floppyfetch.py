import re
import os
import platform
import socket
import subprocess
import GPUtil
from datetime import datetime
import psutil
from screeninfo import get_monitors
from rich import box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from concurrent.futures import ThreadPoolExecutor
import argparse

def get_uptime():
    boot_time = psutil.boot_time()
    now = datetime.now().timestamp()
    uptime_seconds = int(now - boot_time)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{days} days {hours} hours {minutes} minutes"
    return uptime_str

def get_shell():
    if platform.system() == "Windows":
        if "PROMPT" in os.environ and not "PSModulePath" in os.environ:
            return "Command Prompt"

        try:
            import psutil
            parent = psutil.Process(os.getppid())
            parent_name = parent.name().lower()

            if "powershell" in parent_name or "pwsh" in parent_name:
                return "PowerShell"
            elif "cmd" in parent_name or "cmd.exe" in parent_name:
                return "Command Prompt"
            else:
                return parent_name
        except (ImportError, Exception):
            if "PSModulePath" in os.environ:
                return "PowerShell"
            else:
                return "Command Prompt"
    else:
        shell = os.environ.get('SHELL', '')
        return os.path.basename(shell) if shell else 'Unknown'

def get_de():
    if platform.system() == "Windows":
        return "Windows Desktop"
    else:
        de = os.environ.get('DESKTOP_SESSION') or os.environ.get('XDG_CURRENT_DESKTOP')
        return de if de else 'N/A'

def get_resolution():
    try:
        monitors = get_monitors()
        resolutions = [f"{m.width}x{m.height}" for m in monitors]
        return ','.join(resolutions)
    except Exception:
        return 'N/A'

def get_packages():
    if platform.system() == "Windows":
        try:
            scoop_apps = os.path.expanduser("~\\scoop\\apps")
            if os.path.exists(scoop_apps):
                count = sum(1 for item in os.listdir(scoop_apps)
                           if os.path.isdir(os.path.join(scoop_apps, item)))
                return str(f"{count - 1} (scoop)")
            return "0"
        except Exception:
            return "N/A"
    else:
        return "N/A"

def get_os():
    try:
        os_name = platform.system()
        os_details = platform.platform()
        os_info = f"{os_name} ({os_details})"
        return os_info
    except Exception:
        return "Unknown OS"

def get_cpu_wmic():
    try:
        command = "wmic cpu get Name /value"
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate(timeout=0.5)
        if error:
            return platform.processor()
        output_str = output.decode("utf-8").strip()
        match = re.search(r'Name=(.+)', output_str)
        if match:
            return match.group(1).strip()
        return platform.processor()
    except Exception:
        return platform.processor()

def get_cpu():
    if platform.system() == 'Windows':
        return get_cpu_wmic()
    else:
        try:
            return psutil.cpu_info()._asdict().get('brand_raw', platform.processor())
        except (ImportError, AttributeError):
            return platform.processor()

def get_ram():
    vm = psutil.virtual_memory()
    total_gb = vm.total / (1024 ** 3)
    used_gb = vm.used / (1024 ** 3)
    percent = vm.percent
    return f"{used_gb:.2f} GiB / {total_gb:.2f} GiB ({percent}%)"

def get_gpu():
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output("wmic path win32_VideoController get name",
                                           shell=True,
                                           timeout=0.5)

            lines = [line.strip() for line in output.decode().strip().split('\n') if line.strip()]

            if len(lines) >= 2:
                return lines[1]

            output = subprocess.check_output("wmic path win32_VideoController get caption",
                                           shell=True,
                                           timeout=0.5)

            lines = [line.strip() for line in output.decode().strip().split('\n') if line.strip()]
            if len(lines) >= 2:
                return lines[1]

        except Exception:
            try:
                import threading
                import time

                result = ["N/A"]

                def get_gputil_gpu():
                    try:
                        import GPUtil
                        gpus = GPUtil.getGPUs()
                        if gpus:
                            result[0] = gpus[0].name
                    except:
                        pass

                thread = threading.Thread(target=get_gputil_gpu)
                thread.daemon = True
                thread.start()
                thread.join(0.3)

                return result[0]
            except:
                pass

    return "N/A"

def get_host():
    return socket.gethostname()

def get_kernel():
    if platform.system() == "Windows":
        return platform.version()
    else:
        return platform.release()

def fetch_data_parallel():
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            'os_info': executor.submit(get_os),
            'host': executor.submit(get_host),
            'kernel': executor.submit(get_kernel),
            'uptime': executor.submit(get_uptime),
            'packages': executor.submit(get_packages),
            'shell': executor.submit(get_shell),
            'resolution': executor.submit(get_resolution),
            'de': executor.submit(get_de),
            'cpu': executor.submit(get_cpu),
            'gpu': executor.submit(get_gpu),
            'memory': executor.submit(get_ram)
        }

        results = {}
        for key, future in futures.items():
            try:
                results[key] = future.result()
            except Exception as e:
                results[key] = f"Error: {str(e)}"

        return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fetch system information with custom border colors and logos.")
    parser.add_argument("-color", type=str, nargs='+', default=["yellow"], help="Border colors for the panel")
    parser.add_argument("-logo", type=str, nargs='+', default=["0"], help="Logos for the ASCII art")
    args = parser.parse_args()

    console = Console()

    data = fetch_data_parallel()

    table = Table(show_header=False, box=None, padding=(0, 1))
    label_color = 'bold cyan'
    value_color = 'white'

    table.add_row(Text(''))
    table.add_row(Text('OS:', style=label_color), Text(data['os_info'], style=value_color))
    table.add_row(Text('Host:', style=label_color), Text(data['host'], style=value_color))
    table.add_row(Text('Kernel:', style=label_color), Text(data['kernel'], style=value_color))
    table.add_row(Text('Uptime:', style=label_color), Text(data['uptime'], style=value_color))
    table.add_row(Text('Packages:', style=label_color), Text(data['packages'], style=value_color))
    table.add_row(Text('Shell:', style=label_color), Text(data['shell'], style=value_color))
    table.add_row(Text('Resolution:', style=label_color), Text(data['resolution'], style=value_color))
    table.add_row(Text('DE/WM:', style=label_color), Text(data['de'], style=value_color))
    table.add_row(Text('CPU:', style=label_color), Text(data['cpu'], style=value_color))
    table.add_row(Text('GPU:', style=label_color), Text(data['gpu'], style=value_color))
    table.add_row(Text('RAM:', style=label_color), Text(data['memory'], style=value_color))

    # Define logos
    logos = {
        "0": """
 _________________
| | ___________ |o|
| | ___________ | |
| | ___________ | |
| | ___________ | |
| |_____________| |
|     _______     |
|    |       |   ||
| DD |       |   V|
|____|_______|____|
        """,
        "1": r"""
    / ======= \
   / _________ \
  | ___________ |
  | | -       | |
  | |         | |
  | |_________| |
  \_____________/
  / ''''''''''' \
 / ::::::::::::: \
(_________________)
        """,
        "2": r"""

     ,==.-------.  
    (    ) ====  \  
    ||  | [][][] |  
  ,8||  | [][][] |  
  8 ||  | [][][] |  
  8 (    ) O O O /  
  '88`=='-------'  

        """
    }

    # Use the first logo from the list
    logo_key = args.logo[0]
    logo_text = Text(logos.get(logo_key, logos["0"]), style=args.color[0])

    logo_panel = Panel.fit(logo_text, border_style=args.color[0], padding=(0, 2))
    layout = Table.grid(expand=True)
    layout.add_column(justify="left", ratio=1)
    layout.add_column(justify="left", ratio=2)
    layout.add_row(logo_panel, table)
    console.print(Align.left(layout))
