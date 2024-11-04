#——————运行库——————
import zipfile
import hashlib
import sys
import tkinter as tk
from tkinter import filedialog
import winreg
import shutil
import json
from tkinter import messagebox
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Back, Style
import colorama
import psutil
import webbrowser
import threading  # 确保导入 threading 模块
import queue  # 确保导入 queue 模块
from tkinter.ttk import Progressbar
import pygame
import requests
import io
import random
from tkinter import ttk
from tkinter import scrolledtext
import locale

# ————变量初始化————
url = None
base_path = None  # 文件路径
game_path = None # 游戏路径
fileurl = None  #云端链接
filepath = None #临时存储文件路径
version_config = '0.6' #配置文件版本 切记需要更改创建配置文件方法内版本
version_downconfig = '0.4' #下载配置文件版本 切记需要更改创建配置文件方法内版本
app_id = "2325290" #光遇游戏ID

#---定义下载变量----
colorama.init(autoreset=True)
down_1 = None
down_2 = None
down_3 = None
down_4 = None
down_5 = None
#线路测速
urls = [
    'https://gitee.com/xiao-zhu245/filespeedmeasurement/releases/download/main/test.txt',
    'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/%E6%B5%8B%E9%80%9F%E6%96%87%E4%BB%B6/test.txt',
    'https://github.com/yxsj245/Filespeedmeasurement/releases/download/main/test.txt',
    'https://mirror.ghproxy.com/https://github.com/yxsj245/Filespeedmeasurement/releases/download/main/test.txt',
]

# ——————方法库——————

# 加载配置文件
def load_config(file_path="data/config.json"):
    """
    读取 JSON 配置文件的内容。如果文件不存在，则返回 None。
    """
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return None
def load_downconfig(file_path="data/down.json"):
    """
    读取 JSON 配置文件的内容。如果文件不存在，则返回 None。
    """
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return None

# 创建配置文件
def create_default_config(file_path="data/config.json", default_config=None):
    """
    创建一个默认的 JSON 配置文件，如果文件不存在。
    可以传递一个默认配置的字典，如果没有提供，则使用预定义的默认配置。
    """
    if default_config is None:
        default_config = {
            "version":"0.6",
            "first": True,
            "game_path": None,
            "data_path": None,
            "Downloadsource": None,
            "region":None
        }

    # 提取文件目录
    directory = os.path.dirname(file_path)

    # 如果目录不存在，创建目录
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 如果文件不存在，创建文件并写入默认配置
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(default_config, file, indent=4, ensure_ascii=False)
# 创建下载配置文件
def create_default_downconfig(file_path="data/down.json", default_config=None):
    """
    创建一个默认的 JSON 配置文件，如果文件不存在。
    可以传递一个默认配置的字典，如果没有提供，则使用预定义的默认配置。
    """
    if default_config is None:
        default_config = {
            "version": "0.4",
            "downloadurl":{
                "gitee":[
                    'https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/TSM.zip',
                    'https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/sml-pc.zip',
                    'https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/TSM_font.zip',
                    'https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/TSMmap-ZH_CN.zip',
                    'https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/VC_redist.x64.exe'
                ],
                "cloudflare":[
                    'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/TSM%E7%BB%84%E4%BB%B6/TSM.zip',
                    'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/TSM%E7%BB%84%E4%BB%B6/sml-pc.zip',
                    'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/TSM%E7%BB%84%E4%BB%B6/TSM_font.zip',
                    'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/TSM%E7%BB%84%E4%BB%B6/TSMmap-ZH_CN.zip',
                    'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/TSM%E7%BB%84%E4%BB%B6/VC_redist.x64.exe',
                    'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/TSM%E7%BB%84%E4%BB%B6/TSM_font_TC.zip'
                ],
                'Mirrorghproxy':[
                    'https://mirror.ghproxy.com/https://github.com/XeTrinityz/ThatSkyMod/releases/latest/download/TSM.zip',
                    'https://mirror.ghproxy.com/https://github.com/lukas0x1/sml-pc/releases/latest/download/sml-pc.zip',
                    'https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/TSM_font.zip',
                    'https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/TSMmap-ZH_CN.zip',
                    'https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/VC_redist.x64.exe'
                ],
                'github':[
                    'https://github.com/XeTrinityz/ThatSkyMod/releases/latest/download/TSM.zip',
                    'https://github.com/lukas0x1/sml-pc/releases/latest/download/sml-pc.zip',
                    'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/TSM%E7%BB%84%E4%BB%B6/TSM_font.zip',
                    'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/TSM%E7%BB%84%E4%BB%B6/TSMmap-ZH_CN.zip',
                    'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/TSM%E7%BB%84%E4%BB%B6/VC_redist.x64.exe'
                ],
                "other":[]
            },
            "check":[
                'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/data.json',
                'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/down.json'
            ]
        }

    # 提取文件目录
    directory = os.path.dirname(file_path)

    # 如果目录不存在，创建目录
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 如果文件不存在，创建文件并写入默认配置
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(default_config, file, indent=4, ensure_ascii=False)

#更新json方法
def update_config_value(key, value, file_path="data/config.json"):
    """
    更新 JSON 配置文件中指定键的值。
    如果文件不存在，自动创建默认配置文件并更新指定值。
    """
    # 读取现有配置
    with open(file_path, 'r', encoding='utf-8') as file:
        config = json.load(file)

    # 更新指定键的值
    config[key] = value

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4, ensure_ascii=False)

# 获取游戏安装注册表
def get_game_install_location():

    try:
        # 注册表路径
        registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 2325290"
        value_name = "InstallLocation"

        # 尝试以 64 位视图访问注册表
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0,
                                     winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        except FileNotFoundError:
            # 如果 64 位视图失败，尝试以 32 位视图访问
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0,
                                     winreg.KEY_READ | winreg.KEY_WOW64_32KEY)

        # 读取数值
        install_location, reg_type = winreg.QueryValueEx(reg_key, value_name)
        return install_location
    except FileNotFoundError:
        messagebox.showwarning('错误','注册表项或数值名称不存在。(注意：目前这并不代表程序无法运行)')
    except Exception as e:
        messagebox.showerror('错误','读取注册表时发生错误(注意：目前这并不代表程序无法运行)')
    return None

# 选择目录
def select_directory(title):
    # 创建根窗口，但不显示它
    root = tk.Tk()
    root.withdraw()  # 隐藏根窗口

    # 打开目录选择对话框
    selected_directory = filedialog.askdirectory(title=title)

    # 打印选中的目录
    if selected_directory:
        return selected_directory
    else:
        messagebox.showerror('错误','没有选择目录')
        sys.exit(1)  # 终止程序运行并返回状态码1

# 下载文件方法
def start_download_window(url, save_path):
    print(url)
    # 创建下载窗口
    download_window = tk.Toplevel()
    download_window.title("文件下载")

    # 强制聚焦窗口
    # download_window.attributes('-topmost', True)
    # download_window.grab_set()
    # download_window.focus_force()

    # 创建进度条和相关标签
    progress_var = tk.DoubleVar()
    speed_var = tk.StringVar()
    percent_var = tk.StringVar()

    progress_bar = Progressbar(download_window, variable=progress_var, maximum=100)
    progress_bar.pack(pady=20)

    speed_label = tk.Label(download_window, textvariable=speed_var)
    speed_label.pack(pady=5)

    percent_label = tk.Label(download_window, textvariable=percent_var)
    percent_label.pack(pady=5)

    # 创建队列用于线程间通信
    update_queue = queue.Queue()
    stop_download = threading.Event()  # 事件标志，用于停止下载

    def update_progress():
        while not update_queue.empty():
            progress, speed, percent = update_queue.get()
            progress_var.set(progress)
            speed_var.set(speed)
            percent_var.set(percent)
            download_window.update_idletasks()

    def download_file_with_progress():
        try:
            # 检查并创建保存文件的目录
            directory = os.path.dirname(save_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # 发送 HTTP GET 请求获取文件信息
            response = requests.get(url, stream=True, allow_redirects=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            start_time = time.time()

            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if stop_download.is_set():  # 检查是否需要停止下载
                        return
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)

                        progress = (downloaded_size / total_size) * 100
                        elapsed_time = time.time() - start_time
                        speed = downloaded_size / (1024 * 1024 * elapsed_time) if elapsed_time > 0 else 0

                        update_queue.put((
                            progress,
                            f"下载速度：{speed:.2f} MB/s",
                            f"下载进度：{progress:.2f}% 文件下载信息：({downloaded_size / (1024 * 1024):.2f} MB / {total_size / (1024 * 1024):.2f} MB)"
                        ))

            download_window.destroy()

        except requests.exceptions.RequestException as e:
            print(e)
            messagebox.showerror('致命错误', '下载文件时出现错误')
            sys.exit(1)

    # 窗口关闭时设置停止下载标志
    def on_closing():
        stop_download.set()  # 设置停止下载标志
        download_window.destroy()

    download_window.protocol("WM_DELETE_WINDOW", on_closing)  # 绑定窗口关闭事件

    # 创建线程以运行下载
    download_thread = threading.Thread(target=download_file_with_progress)
    download_thread.start()

    # 运行主循环，更新进度
    while download_thread.is_alive():
        update_progress()
        download_window.update()

# 线路测速
def download_files(urls):
    def download_file(url):
        start_time = time.time()
        total_bytes = 0
        speeds = []

        try:
            with requests.get(url, stream=True, timeout=5) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    total_bytes += len(chunk)
                    elapsed_time = time.time() - start_time

                    if elapsed_time >= 20:
                        break

                    if int(elapsed_time) > len(speeds):
                        speed_mb = total_bytes / (elapsed_time * 1024 * 1024)
                        speeds.append(speed_mb)

            average_speed = sum(speeds) / len(speeds) if speeds else 0
            return url, average_speed, time.time() - start_time
        except requests.RequestException:
            return None  # 返回None表示请求失败

    fastest_url = None
    fastest_time = float('inf')

    with ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(download_file, url): url for url in urls}

        for future in as_completed(future_to_url):
            result = future.result()
            if result:  # 只有成功的请求才考虑
                url, average_speed, elapsed_time = result
                if elapsed_time < fastest_time:
                    fastest_time = elapsed_time
                    fastest_url = url

    return fastest_url  # 仅返回最快的URL

# 云端拉取json方法
def fetch_json_from_url(url):
    try:
        response = requests.get(url, timeout=10)  # 设置超时时间为10秒
        response.raise_for_status()  # 检查请求是否成功
        config = response.json()  # 解析JSON数据
    except requests.exceptions.RequestException as e:
        messagebox.showerror('错误',f"从获取JSON时出错 {url}: {e}")
def fetch_json_from_url(url):
    try:
        response = requests.get(url, timeout=30)  # 设置超时时间为10秒
        response.raise_for_status()  # 如果请求失败则抛出HTTPError异常
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror('错误',f"ERROR:从云端拉取文件信息失败: {e}")
        messagebox.showinfo('注意','跳过鉴权文件信息，无法保证文件完整，这可能会导致TSM不在预期内运行。')
        return None

# 校验MD5
def calculate_md5(file_path, buffer_size=8192):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        chunk = f.read(buffer_size)
        while chunk:
            md5_hash.update(chunk)
            chunk = f.read(buffer_size)
    return md5_hash.hexdigest()
def verify_md5(file_path, expected_md5):
    try:
        file_md5 = calculate_md5(file_path)
        # 忽略大小写比较MD5值
        if file_md5.lower() == expected_md5.lower():
            return True
        else:
            messagebox.showwarning('警告',f"WARN:文件信息校验码不匹配: {file_path}")
            messagebox.showinfo('提示','可能是您下载了错误的版本或者下载过程中文件出现损坏。请重新下载上行路径输出的末尾的文件替换到此目录。如果是新版本更新可能没有及时更新云端文件信息所致，您可以按任意键跳过。但是这将可能导致TSM不在预期内运行。')
            return True
    except FileNotFoundError:
        messagebox.showerror('程序错误',f"ERROR:文件缺失: {file_path};在最新版本中，此错误不应当出现，请联系作者排查。")
        sys.exit(1)  # 终止程序运行并返回状态码1

# 拼接路径
def create_full_path(base_path, file_name):
    # 确保base_path以斜杠结尾，然后拼接文件名
    if not base_path.endswith('/'):
        base_path += '/'
    full_path = base_path + file_name
    return full_path

# 解压文件的方法
def unzip_file(zip_path, extract_to):
    # 检查文件是否为zip格式
    if zipfile.is_zipfile(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 解压缩所有文件到目标目录
            zip_ref.extractall(extract_to)
    else:
        messagebox.showerror('致命错误','指定的文件不是有效的ZIP文件')

# 检测Sky进程
def monitor_process():
    process_name = "Sky.exe"

    # 一直检测直到检测到 sky.exe 进程
    while True:
        # 检测是否有名为 sky.exe 的进程
        process_exists = any(proc.name() == process_name for proc in psutil.process_iter())

        if process_exists:
            # print(f"检测到 {process_name}")
            start_time = time.time()

            # 开始计时20秒，期间每秒检测一次进程是否存在
            while time.time() - start_time < 20:
                process_exists = any(proc.name() == process_name for proc in psutil.process_iter())

                if not process_exists:
                    return True  # 返回成功，进程在20秒内退出

                time.sleep(1)

            return False  # 返回失败，进程未在20秒内退出
        else:
            # 如果没检测到进程，继续每秒检查
            time.sleep(1)

# 卸载TSM
def delete_files_and_directories(target_directory):
    # 要删除的文件和目录的名称
    files_to_delete = [
        "libcurl.dll",
        "powrprof.dll",
        "sml_config.json"
    ]

    directories_to_delete = [
        "fonts",
        "mods"
    ]

    # 删除文件
    for file_name in files_to_delete:
        file_path = os.path.join(target_directory, file_name)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                pass
                # print(Fore.RED+f"ERROR:文件未找到: {file_path}")
        except Exception as e:
            messagebox.showerror('致命错误','删除文件时出现错误')
            sys.exit(1)

    # 删除目录
    for dir_name in directories_to_delete:
        dir_path = os.path.join(target_directory, dir_name)
        try:
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)
                # print(Fore.BLUE + f"INFO:已删除目录: {dir_path}")
            else:
                pass
                # print(Fore.RED+f"ERROR:目录未找到: {dir_path}")
        except Exception as e:
            messagebox.showerror('致命错误','删除目录时出现错误')
            sys.exit(1)

# 删除非游戏文件

def delete_feifiles_and_directories_with_confirmation(target_directory):
    # 不删除的文件和文件夹
    files_to_keep = [
        "steam_api64.dll", "Sky.res", "Sky.log", "Sky.lib",
        "Sky.exe", "fmodstudio.dll", "fmod.dll", "crashpad_handler.exe"
    ]

    directories_to_keep = [
        "data", "crash_reports"
    ]

    # 收集所有将要删除的文件和文件夹
    files_to_delete = []
    directories_to_delete = []

    # 遍历目标目录中的所有文件和文件夹
    for root, dirs, files in os.walk(target_directory):
        # 检查当前目录是否在保留的文件夹中
        dirs[:] = [d for d in dirs if d not in directories_to_keep]

        # 遍历文件，排除保留文件
        for file_name in files:
            if file_name not in files_to_keep:
                files_to_delete.append(os.path.join(root, file_name))

        # 只添加不在保留列表中的目录，并忽略目录内的内容
        for dir_name in dirs:
            directories_to_delete.append(os.path.join(root, dir_name))
        # 跳过深入遍历这些目录
        dirs[:] = []

    # 创建顶层确认窗口
    def create_confirmation_window():
        confirmation_window = tk.Toplevel()
        confirmation_window.title("文件删除确认")
        confirmation_window.geometry("600x400")

        # 显示将要删除的文件和目录
        text_area = scrolledtext.ScrolledText(confirmation_window, width=70, height=20)
        text_area.pack(padx=10, pady=10)

        text_area.insert(tk.END, "以下文件和目录将被删除:\n\n文件:\n")
        for file_path in files_to_delete:
            text_area.insert(tk.END, file_path + "\n")

        text_area.insert(tk.END, "\n目录:\n")
        for dir_path in directories_to_delete:
            text_area.insert(tk.END, dir_path + "\n")

        # 删除操作
        def delete_files_and_directories():
            try:
                # 删除文件
                for file_path in files_to_delete:
                    if os.path.isfile(file_path):
                        os.remove(file_path)

                # 强制删除目录（不检查是否为空）
                for dir_path in directories_to_delete:
                    shutil.rmtree(dir_path, ignore_errors=True)

                messagebox.showinfo("成功", "所有指定文件和目录已成功删除")
                confirmation_window.destroy()  # 删除完成后关闭顶层窗口
            except Exception as e:
                messagebox.showerror("错误", f"删除过程中出现错误: {e}")
                confirmation_window.destroy()  # 出现错误后关闭顶层窗口

        # 确认删除按钮
        confirm_button = ttk.Button(confirmation_window, text="确认删除", command=delete_files_and_directories)
        confirm_button.pack(pady=10)

        # 取消按钮
        cancel_button = ttk.Button(confirmation_window, text="取消", command=confirmation_window.destroy)
        cancel_button.pack(pady=10)

    # 如果有要删除的文件或目录，显示确认窗口
    if len(files_to_delete) > 0 or len(directories_to_delete) > 0:
        create_confirmation_window()
    else:
        messagebox.showinfo("提示", "没有可删除的文件或目录。")

# 删除指定目录下的文件
def delete_all_files_in_directory(directory_path):
    # 检查指定路径是否为目录
    if os.path.isdir(directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                # 如果是文件，则删除
                if os.path.isfile(file_path):
                    os.remove(file_path)
                # 如果是目录，则删除整个目录
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                messagebox.showerror('致命错误',f"删除 {file_path} 时出错: {e}")
                sys.exit(1)
    else:
        pass
        # print(f"{directory_path} 不是一个有效的目录")

# 下载文件
def download_file(url, save_path):
    try:
        # 检查并创建保存文件的目录
        directory = os.path.dirname(save_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 发送 HTTP GET 请求获取文件信息
        response = requests.get(url, stream=True, allow_redirects=True)
        response.raise_for_status()  # 检查请求是否成功

        # 将下载的文件写入目标路径
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    except requests.exceptions.RequestException:
        return  # 捕获请求错误并简单返回

# 播放音频
def music(url):
    # 初始化 pygame
    pygame.mixer.init()
    # 从 URL 下载 MP3 文件
    response = requests.get(url)
    # 将 MP3 文件加载到 pygame 中
    mp3_data = io.BytesIO(response.content)
    pygame.mixer.music.load(mp3_data)
    # 设置音量
    pygame.mixer.music.set_volume(0.2)
    # 播放 MP3 文件
    pygame.mixer.music.play()
    # 等待播放结束
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# 移动文件
def move_files_and_directories(game_path, files_to_delete, directories_to_delete, destination_path):
    # 创建目标路径（如果不存在）
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    # 移动文件
    for file_name in files_to_delete:
        file_path = os.path.join(game_path, file_name)
        if os.path.exists(file_path):
            shutil.move(file_path, destination_path)
        else:
            pass
            # print(Fore.RED+ f"ERROR:找不到文件: {file_name}")

    # 移动文件夹
    for dir_name in directories_to_delete:
        dir_path = os.path.join(game_path, dir_name)
        if os.path.exists(dir_path):
            shutil.move(dir_path, destination_path)
        else:
            pass
            # print(Fore.RED+ f"ERROR:找不到目录： {dir_name}")

# 列出所有进程
def check_process_exists(process_name):
    # 遍历所有进程
    for proc in psutil.process_iter(['name']):
        try:
            # 检查进程名是否匹配
            if proc.info['name'].lower() == process_name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

# 获取当前工作目录文件
def check_file_exists(filename):
    # 获取当前工作目录
    current_directory = os.getcwd()
    # 构造完整路径
    file_path = os.path.join(current_directory, filename)
    # 检查文件是否存在
    return os.path.isfile(file_path)

#---重载方法---
# 重载下载源
def downreload():
    global down_1
    global down_2
    global down_3
    global down_4
    global down_5
    jsondata = load_config()
    downdata = load_downconfig()
    if jsondata['Downloadsource'] == 'gitee':
        # print(Style.BRIGHT + Fore.CYAN + 'INFO:温馨提示：当前下载线路采用分流模式,TSM组件会受到作者上传速度影响,如需下载最新版可以使用序号4功能')
        down_1 = downdata['downloadurl']['gitee'][0]
        down_2 = downdata['downloadurl']['gitee'][1]
        down_3 = downdata['downloadurl']['gitee'][2]
        down_4 = downdata['downloadurl']['gitee'][3]
        down_5 = downdata['downloadurl']['gitee'][4]
    elif jsondata['Downloadsource'] == 'cloudflare':
        # print(Style.BRIGHT + Fore.CYAN + 'INFO:温馨提示：当前下载线路采用分流模式,TSM组件会受到作者上传速度影响,如需下载最新版可以使用序号4功能')
        down_1 = downdata['downloadurl']['cloudflare'][0]
        down_2 = downdata['downloadurl']['cloudflare'][1]
        down_3 = downdata['downloadurl']['cloudflare'][2]
        down_4 = downdata['downloadurl']['cloudflare'][3]
        down_5 = downdata['downloadurl']['cloudflare'][4]
    elif jsondata['Downloadsource'] == 'Mirrorghproxy':
        # print(Style.BRIGHT + Fore.CYAN + 'INFO:温馨提示：当前下载线路采用github,一键功能下载到的TSM组件为最新版')
        down_1 = downdata['downloadurl']['Mirrorghproxy'][0]
        down_2 = downdata['downloadurl']['Mirrorghproxy'][1]
        down_3 = downdata['downloadurl']['Mirrorghproxy'][2]
        down_4 = downdata['downloadurl']['Mirrorghproxy'][3]
        down_5 = downdata['downloadurl']['Mirrorghproxy'][4]
    elif jsondata['Downloadsource'] == 'github':
        # print(Style.BRIGHT + Fore.CYAN + 'INFO:温馨提示：当前下载线路采用github,一键功能下载到的TSM组件为最新版')
        down_1 = downdata['downloadurl']['github'][0]
        down_2 = downdata['downloadurl']['github'][1]
        down_3 = downdata['downloadurl']['github'][2]
        down_4 = downdata['downloadurl']['github'][3]
        down_5 = downdata['downloadurl']['github'][4]
    else:
        down_1 = downdata['downloadurl']['other'][0]
        down_2 = downdata['downloadurl']['other'][1]
        down_3 = downdata['downloadurl']['other'][2]
        down_4 = downdata['downloadurl']['other'][3]
        down_5 = downdata['downloadurl']['other'][4]

# ——————运行方法库——————
# 环境初始化
def initialization():
    mainmenu.withdraw()
    #变量初始化
    def Variable():
        try:
            jsondata = load_config()
            downdata = load_downconfig()
            filepath = jsondata['data_path']
            game_path = jsondata['game_path']
            base_path = filepath
            url = downdata['check'][0]
            global down_1
            global down_2
            global down_3
            global down_4
            global down_5
            if jsondata['Downloadsource'] == 'gitee':
                # print(Style.BRIGHT + Fore.CYAN + 'INFO:温馨提示：当前下载线路采用分流模式,TSM组件会受到作者上传速度影响,如需下载最新版可以使用序号4功能')
                down_1 = downdata['downloadurl']['gitee'][0]
                down_2 = downdata['downloadurl']['gitee'][1]
                down_3 = downdata['downloadurl']['gitee'][2]
                down_4 = downdata['downloadurl']['gitee'][3]
                down_5 = downdata['downloadurl']['gitee'][4]
            elif jsondata['Downloadsource'] == 'cloudflare':
                # print(Style.BRIGHT + Fore.CYAN + 'INFO:温馨提示：当前下载线路采用分流模式,TSM组件会受到作者上传速度影响,如需下载最新版可以使用序号4功能')
                down_1 = downdata['downloadurl']['cloudflare'][0]
                down_2 = downdata['downloadurl']['cloudflare'][1]
                down_3 = downdata['downloadurl']['cloudflare'][2]
                down_4 = downdata['downloadurl']['cloudflare'][3]
                down_5 = downdata['downloadurl']['cloudflare'][4]
            elif jsondata['Downloadsource'] == 'Mirrorghproxy':
                # print(Style.BRIGHT + Fore.CYAN + 'INFO:温馨提示：当前下载线路采用github,一键功能下载到的TSM组件为最新版')
                down_1 = downdata['downloadurl']['Mirrorghproxy'][0]
                down_2 = downdata['downloadurl']['Mirrorghproxy'][1]
                down_3 = downdata['downloadurl']['Mirrorghproxy'][2]
                down_4 = downdata['downloadurl']['Mirrorghproxy'][3]
                down_5 = downdata['downloadurl']['Mirrorghproxy'][4]
            elif jsondata['Downloadsource'] == 'github':
                # print(Style.BRIGHT + Fore.CYAN + 'INFO:温馨提示：当前下载线路采用github,一键功能下载到的TSM组件为最新版')
                down_1 = downdata['downloadurl']['github'][0]
                down_2 = downdata['downloadurl']['github'][1]
                down_3 = downdata['downloadurl']['github'][2]
                down_4 = downdata['downloadurl']['github'][3]
                down_5 = downdata['downloadurl']['github'][4]
            else:
                down_1 = downdata['downloadurl']['other'][0]
                down_2 = downdata['downloadurl']['other'][1]
                down_3 = downdata['downloadurl']['other'][2]
                down_4 = downdata['downloadurl']['other'][3]
                down_5 = downdata['downloadurl']['other'][4]
        except KeyError:
            os.remove('data/config.json')
            os.remove('data/down.json')
            messagebox.showwarning('警告', '检测到配置文件与主程序不兼容或损坏,已删除,请重新运行程序')
            sys.exit(0)
        if jsondata['version'] != version_config:
            os.remove('data/config.json')
            messagebox.showwarning('警告', '检测到配置文件与主程序不兼容或损坏,已删除,请重新运行程序')
            sys.exit(0)
        if downdata['version'] != version_downconfig:
            os.remove('data/down.json')
            messagebox.showwarning('警告', '检测到配置文件与主程序不兼容或损坏,已删除,请重新运行程序')
            sys.exit(0)
        mainmenu.deiconify()

    # 初始化
    def initializat():
        def WindowEvent():
            sys.exit(0)
        # 创建子窗口
        initiali = tk.Toplevel()
        initiali.title('TSM包管理器4.5_环境初始化')

        # 变量
        current_locale = None #系统区域语言

        contents = tk.StringVar()
        Temporaryfiles = tk.StringVar()
        Downloadsource = tk.StringVar()

        # print(Downloadsource.get())


        # 运行主程序
        game_path = get_game_install_location()
        if game_path == None:
            messagebox.showwarning('获取游戏路径失败', '由于注册表问题无法获取游戏路径,请手动选择游戏的根目录')
            game_path = select_directory(Fore.BLUE + "INFO:请选择游戏根目录")
            contents.set(game_path)
        else:
            contents.set(game_path)

        # 获取临时文件夹路径
        temp_dir = os.environ.get('TEMP') or os.environ.get('TMP')
        # 拼接TSMdownload文件夹
        tsm_download_path = os.path.join(temp_dir, "TSMdownload")
        Temporaryfiles.set(tsm_download_path)



        try:
            locale.setlocale(locale.LC_ALL, '')
            current_locale = locale.getlocale()
        except Exception as e:
            messagebox.showerror('错误','读取系统区域语言失败')

        # 运行方法库
        # 更改游戏目录
        def run():
            game_path = select_directory("选择游戏根目录")
            contents.set(game_path)

        # 更改下载目录
        def run2():
            filepath = select_directory("选择目录")
            Temporaryfiles.set(filepath)

        # 更改下载源
        def run3():
            linshi1.config(state=tk.DISABLED,text='正在进行中')
            def main():
                fastest = download_files(urls)
                # fastest = 'https://gitee.com/xiao-zhu245/filespeedmeasurement/releases/download/main/test.txt'
                if fastest:
                    if fastest == 'https://mirror.ghproxy.com/https://github.com/yxsj245/Filespeedmeasurement/releases/download/main/test.txt':
                        Downloadsource.set('Mirrorghproxy')
                        linshi1.config(state=tk.NORMAL, text='重新检测')
                        # update_config_value('Downloadsource', 'Mirrorghproxy')
                    elif fastest == 'https://github.com/yxsj245/Filespeedmeasurement/releases/download/main/test.txt':
                        Downloadsource.set('github')
                        linshi1.config(state=tk.NORMAL, text='重新检测')
                        # update_config_value('Downloadsource', 'github')
                    elif fastest == 'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/%E6%B5%8B%E9%80%9F%E6%96%87%E4%BB%B6/test.txt':
                        Downloadsource.set('cloudflare')
                        linshi1.config(state=tk.NORMAL, text='重新检测')
                        # update_config_value('Downloadsource', 'cloudflare')
                    elif fastest == 'https://gitee.com/xiao-zhu245/filespeedmeasurement/releases/download/main/test.txt':
                        Downloadsource.set('gitee')
                        linshi1.config(state=tk.NORMAL, text='重新检测')
                        # update_config_value('Downloadsource', 'gitee')

            thread1 = threading.Thread(target=main)
            thread1.start()

        # 应用更改
        def Stop():
            update_config_value('game_path', contents.get())
            update_config_value('data_path', Temporaryfiles.get())
            update_config_value('Downloadsource', Downloadsource.get())
            update_config_value('first', False)
            initiali.destroy()
            mainmenu.deiconify()
            Variable()


        tk.Label(initiali,text='游戏目录：',font=('微软雅黑',12)).grid(row=1,column=1)
        tk.Entry(initiali,width=70,font=('微软雅黑',12),state='read',textvariable=contents).grid(row=1,column=2)

        tk.Label(initiali, text='临时文件存储目录：', font=('微软雅黑', 12)).grid(row=2, column=1)
        tk.Entry(initiali, width=70, font=('微软雅黑', 12), state='read', textvariable=Temporaryfiles).grid(row=2, column=2)

        tk.Label(initiali, text='下载源：', font=('微软雅黑', 12)).grid(row=3, column=1)
        combobox = ttk.Combobox(initiali, textvariable=Downloadsource, state="readonly", width=70)
        combobox['values'] = ['gitee', 'cloudflare', 'Mirrorghproxy', 'github', 'other']
        combobox.grid(row=3, column=2)
        try:
            if current_locale[0]!= 'Chinese (Simplified)_China':
                initiali.after(1, lambda: combobox.set('cloudflare'))
                update_config_value('region', '繁体中文')
            else:
                initiali.after(1, lambda: combobox.set('Mirrorghproxy'))
                update_config_value('region','简体中文')
        except Exception as e:
            messagebox.showwarning('警告','由于无法读取系统区域语言,默认采用中国代理')
            initiali.after(1, lambda: combobox.set('Mirrorghproxy'))

        ttk.Button(initiali,text='更改目录',command=run, padding=(10, 5)).grid(row=1, column=3)
        ttk.Button(initiali,text='更改目录',command=run2, padding=(10, 5)).grid(row=2, column=3)
        linshi1 = ttk.Button(initiali, text='检测最优线路', command=run3, padding=(10, 5))
        linshi1.grid(row=3, column=3)

        ttk.Button(initiali, text='确认所有配置', command=Stop, padding=(10, 5)).grid(row=4, column=1)

        initiali.protocol('WM_DELETE_WINDOW', WindowEvent)

    config = load_config()
    if config is None:
        create_default_config()
        config = load_config()
    # 初始下载配置文件
    down = load_downconfig()
    if down is None:
        create_default_downconfig()
        config = load_downconfig()
    if load_config()['first']:
        initializat()
    else:
        Variable()

# 运行环境检测
def checkzation():
    if check_process_exists('Sky.exe'):
        messagebox.showwarning('警告','检测到游戏正在运行，为保证程序功能运行正常，请您关闭游戏后操作。')
    if check_file_exists('Sky.exe'):
        messagebox.showwarning('警告', '检测到您将程序放置在游戏目录，这将会导致SML启动，为保证程序功能运行正常，请您放置在除游戏根目录外的其它任意目录')
        sys.exit(0)

# 故障排除
def Troubleshooting():
    mainmenu.attributes('-alpha',0.5)
    mainmenu.attributes('-topmost', False)
    # 初始化变量
    jsondata = load_config()
    filepath = jsondata['data_path']
    Troubwindow = tk.Toplevel()
    Troubwindow.title("故障排除")
    Troubwindow.geometry("500x100")
    def run1():
        tk.Label(Troubwindow, text='开始下载VC运行库,稍后请点击安装后重启电脑再次尝试启动游戏', font=('微软雅黑', 13),bg='yellow',fg='red').place(relx=0.5, y=50, anchor='center')
        def download_and_run():
            fileurl = down_5
            save_path = os.path.join(filepath, "VC_redist.x64.exe")
            start_download_window(fileurl, save_path)
            exe_path = os.path.join(filepath, "VC_redist.x64.exe")
            subprocess.run(exe_path)
        # 创建并启动线程
        thread = threading.Thread(target=download_and_run)
        thread.start()  # 开始执行下载和运行任务
    def run2():
        webbrowser.open(
            "https://tsmpackagemanager.skymusicscore.asia/WEB/#/docs/TSM%E5%B7%B2%E7%9F%A5%E9%97%AE%E9%A2%98")

    def WindowEvent():
        mainmenu.attributes('-alpha', 1)
        mainmenu.focus_force()  # 强制聚焦
        Troubwindow.destroy()

    ttk.Button(Troubwindow, text='游戏启动后没有显示任何窗口', command=run1, padding=(10, 5)).grid(row=1,column=1)
    ttk.Button(Troubwindow, text='游戏启动后出现游戏窗口但很快消失', command=run2, padding=(10, 5)).grid(row=1,column=2)
    Troubwindow.protocol('WM_DELETE_WINDOW',WindowEvent)

#一键安装TSM
def OneclickinstallationTSM():
    stop_event = threading.Event()
    def main():
        stop_event.clear()
        while not stop_event.is_set():
            # 初始化变量
            jsondata = load_config()
            downdata = load_downconfig()
            filepath = jsondata['data_path']
            game_path = jsondata['game_path']
            regionoption = jsondata['region']
            base_path = filepath
            url = downdata['check'][0]
            # print(Fore.BLUE + "INFO:开始下载文件")

            # ————调试注释————
            # 下载TSM.zip
            fileurl = down_1
            save_path = os.path.join(filepath, "TSM.zip")
            start_download_window(fileurl,save_path)

            # 下载sml-pc.zip
            if stop_event.is_set(): return
            fileurl = down_2
            save_path = os.path.join(filepath, "sml-pc.zip")
            start_download_window(fileurl,save_path)

            # 下载TSM_font.zip
            if stop_event.is_set(): return
            if regionoption == '简体中文':
                fileurl = down_3
                save_path = os.path.join(filepath, "TSM_font.zip")
                start_download_window(fileurl,save_path)
            else:
                fileurl = downdata['downloadurl']['cloudflare'][5]
                save_path = os.path.join(filepath, "TSM_font.zip")
                start_download_window(fileurl,save_path)

            # 下载TSMmap-ZH_CN.zip
            if stop_event.is_set(): return
            fileurl = down_4
            save_path = os.path.join(filepath, "TSMmap-ZH_CN.zip")
            start_download_window(fileurl,save_path)
            # ————调试注释————
            #————调试注释————
            if stop_event.is_set(): return
            if regionoption == '简体中文':
                installOne.config(state=tk.DISABLED, text='正在校验文件')
                json_data = fetch_json_from_url(url)
                # 如果成功获取到JSON数据，则进行文件校验
                if json_data:
                    for item in json_data:
                        filename = item.get("filename")
                        expected_md5 = item.get("md5")

                        if filename and expected_md5:
                            file_path = os.path.join(base_path, filename)  # 拼接基础路径和文件名
                            if verify_md5(file_path, expected_md5):
                                None
                            else:
                                sys.exit(1)  # 如果MD5不匹配，终止程序
                        else:
                            pass
                            # print(Fore.RED+"ERROR:JSON数据中缺少文件名或MD5值，跳过该项。")
            # ————调试注释————

            # print(Fore.BLUE + "INFO:文件信息校验完毕。")

            # ————调试注释————
            # print(Fore.BLUE + "INFO:开始解压文件")
            installOne.config(state=tk.DISABLED, text='正在解压')
            # 解压sml-pc.zip
            file_name = 'sml-pc.zip'  # 替换为你的文件名
            full_path = create_full_path(base_path, file_name)
            unzip_file(create_full_path(base_path, file_name),game_path)
            # 解压TSM.zip
            file_name = 'TSM.zip'  # 替换为你的文件名
            full_path = create_full_path(base_path, file_name)
            game_path_mod = game_path +'/mods'
            unzip_file(create_full_path(base_path, file_name),game_path_mod)
            # 解压TSM_font.zip
            file_name = 'TSM_font.zip'  # 替换为你的文件名
            full_path = create_full_path(base_path, file_name)
            unzip_file(create_full_path(base_path, file_name),game_path)
            # 解压TSMmap-ZH_CN.zip
            file_name = 'TSMmap-ZH_CN.zip'  # 替换为你的文件名
            full_path = create_full_path(base_path, file_name)
            unzip_file(create_full_path(base_path, file_name),game_path)
            xuanze = messagebox.askokcancel('安装完毕','是否启动游戏？')
            if xuanze:
                # print(Fore.BLUE + "INFO:调用steam启动游戏中...")
                installOne.config(state=tk.DISABLED, text='正在监控游戏')
                os.startfile(f"steam://rungameid/{app_id}")
                # print(Fore.BLUE + "INFO:开始监控游戏进程")
                result = monitor_process()
                if result:
                    xuanze = messagebox.askquestion('警告', '检测到游戏进程在启动后结束,是否运行故障排除向导？')
                    if xuanze == 'yes':
                        stop_event.set()
                        installOne.config(state=tk.NORMAL, text='一键安装', command=OneclickinstallationTSM)
                        Troubleshooting()
                    else:
                        stop_event.set()
                        installOne.config(state=tk.NORMAL, text='一键安装', command=OneclickinstallationTSM)
                        mainmenu.attributes('-alpha', 1)
                        mainmenu.focus_force()  # 强制聚焦
                else:
                    stop_event.set()
                    # print(Fore.BLUE + "游戏启动成功")
                    installOne.config(state=tk.NORMAL, text='一键安装', command=OneclickinstallationTSM)
                    mainmenu.attributes('-alpha', 1)
                    mainmenu.focus_force()  # 强制聚焦
            else:
                stop_event.set()
                installOne.config(state=tk.NORMAL, text='一键安装', command=OneclickinstallationTSM)
                mainmenu.attributes('-alpha', 1)
                mainmenu.focus_force()  # 强制聚焦

    # 停止线程
    def stop():
        stop_event.set()
        installOne.config(state=tk.NORMAL, text='一键安装', command=OneclickinstallationTSM)

    installOne.config(text='停止安装任务',command=stop)

    thread1 = threading.Thread(target=main)
    thread1.start()
    # ————调试注释————

# 从本地文件安装
def Localfileinstallation():
    installTwo.config(state=tk.DISABLED, text='请选择目录')
    def main():
        # 初始化变量
        jsondata = load_config()
        game_path = jsondata['game_path']

        base_path=select_directory("请选择TSM文件下载的目录")
        installTwo.config(state=tk.DISABLED, text='正在解压')
        # 解压sml-pc.zip
        file_name = 'sml-pc.zip'  # 替换为你的文件名
        full_path = create_full_path(base_path, file_name)
        unzip_file(create_full_path(base_path, file_name), game_path)
        # 解压TSM.zip
        file_name = 'TSM.zip'  # 替换为你的文件名
        full_path = create_full_path(base_path, file_name)
        game_path_mod = game_path + '/mods'
        unzip_file(create_full_path(base_path, file_name), game_path_mod)
        # 解压TSM_font.zip
        file_name = 'TSM_font.zip'  # 替换为你的文件名
        full_path = create_full_path(base_path, file_name)
        unzip_file(create_full_path(base_path, file_name), game_path)
        # 解压TSMmap-ZH_CN.zip
        file_name = 'TSMmap-ZH_CN.zip'  # 替换为你的文件名
        full_path = create_full_path(base_path, file_name)
        unzip_file(create_full_path(base_path, file_name), game_path)
        xuanze = messagebox.askokcancel('安装完毕','是否启动游戏？')
        if xuanze:
            installTwo.config(state=tk.DISABLED, text='正在监控游戏')
            os.startfile(f"steam://rungameid/{app_id}")
            result = monitor_process()
            if result:
                xuanze = messagebox.askquestion('警告', '检测到游戏进程在启动后结束,是否运行故障排除向导？')
                if xuanze == 'yes':
                    installTwo.config(state=tk.NORMAL, text='从本地安装')
                    Troubleshooting()
                else:
                    installTwo.config(state=tk.NORMAL, text='从本地安装')
                    mainmenu.attributes('-alpha', 1)
                    mainmenu.focus_force()  # 强制聚焦
            else:
                installTwo.config(state=tk.NORMAL, text='从本地安装')
                mainmenu.attributes('-alpha', 1)
                mainmenu.focus_force()  # 强制聚焦
        else:
            installTwo.config(state=tk.NORMAL, text='从本地安装')
            mainmenu.attributes('-alpha', 1)
            mainmenu.focus_force()  # 强制聚焦
    thread1 = threading.Thread(target=main)
    thread1.start()
# 更新TSM
def UpdateTSM():
    stop_event = threading.Event()
    stop_even2 = threading.Event()

    mainmenu.attributes('-alpha',0.5)
    mainmenu.attributes('-topmost', False)
    # 初始化变量
    jsondata = load_config()
    filepath = filepath = jsondata['data_path']
    filepath = jsondata['data_path']
    game_path = jsondata['game_path']
    regionoption = jsondata['region']
    base_path = filepath
    downdata = load_downconfig()

    UpdateTSM = tk.Toplevel()
    UpdateTSM.title("更新TSM")

    # 更新汉化组件
    def run():
        stop_event.clear()
        def main():
            while not stop_event.is_set():
                # 下载TSM_font.zip
                if regionoption == '简体中文':
                    fileurl = down_3
                    save_path = os.path.join(filepath, "TSM_font.zip")
                    start_download_window(fileurl, save_path)
                else:
                    fileurl = downdata['downloadurl']['cloudflare'][5]
                    save_path = os.path.join(filepath, "TSM_font.zip")
                    start_download_window(fileurl, save_path)
                # 下载TSMmap-ZH_CN.zip
                if stop_event.is_set(): return
                fileurl = down_4
                save_path = os.path.join(filepath, "TSMmap-ZH_CN.zip")
                start_download_window(fileurl, save_path)
                # 解压TSM_font.zip
                if stop_event.is_set(): return
                linshi1.config(state=tk.DISABLED, text='正在解压文件')
                file_name = 'TSM_font.zip'  # 替换为你的文件名
                full_path = create_full_path(base_path, file_name)
                unzip_file(create_full_path(base_path, file_name), game_path)
                # 解压TSMmap-ZH_CN.zip
                file_name = 'TSMmap-ZH_CN.zip'  # 替换为你的文件名
                full_path = create_full_path(base_path, file_name)
                unzip_file(create_full_path(base_path, file_name), game_path)
                linshi1.config(state=tk.NORMAL, text='更新汉化组件', command=run)
                stop_event.set()
                messagebox.showinfo('成功','安装成功')
                linshi2.config(state=tk.NORMAL)
                UpdateTSM.attributes('-alpha', 1)
                UpdateTSM.focus_force()  # 强制聚焦

        # 停止线程
        def stop():
            stop_event.set()
            linshi1.config(state=tk.NORMAL, text='更新汉化组件', command=run)
            linshi2.config(state=tk.NORMAL)

        linshi1.config(text='停止任务',command=stop)
        linshi2.config(state=tk.DISABLED)
        thread1 = threading.Thread(target=main)
        thread1.start()

    # 更新TSM组件
    def run2():
        stop_even2.clear()
        def main():
            while not stop_even2.is_set():
                # 下载TSM.zip
                fileurl = downdata['downloadurl']['Mirrorghproxy'][0]
                save_path = os.path.join(filepath, "TSM.zip")
                start_download_window(fileurl, save_path)
                # 下载sml-pc.zip
                if stop_even2.is_set(): return
                fileurl = downdata['downloadurl']['Mirrorghproxy'][1]
                save_path = os.path.join(filepath, "sml-pc.zip")
                start_download_window(fileurl, save_path)
                # 解压sml-pc.zip
                if stop_even2.is_set(): return
                linshi2.config(state=tk.DISABLED, text='正在解压')
                file_name = 'sml-pc.zip'  # 替换为你的文件名
                full_path = create_full_path(base_path, file_name)
                unzip_file(create_full_path(base_path, file_name), game_path)
                # 解压TSM.zip
                file_name = 'TSM.zip'  # 替换为你的文件名
                full_path = create_full_path(base_path, file_name)
                game_path_mod = game_path + '/mods'
                unzip_file(create_full_path(base_path, file_name), game_path_mod)
                linshi2.config(state=tk.NORMAL, text='更新TSM组件', command=run2)
                stop_even2.set()
                linshi1.config(state=tk.NORMAL)
                messagebox.showinfo('成功', '安装成功:默认没有中文，如有需要请重新运行脚本选择下载汉化。')
                UpdateTSM.attributes('-alpha', 1)
                UpdateTSM.focus_force()  # 强制聚焦

        # 停止线程
        def stop():
            stop_even2.set()
            linshi2.config(state=tk.NORMAL, text='更新TSM组件', command=run2)
            linshi1.config(state=tk.NORMAL)

        linshi2.config(text='停止任务',command=stop)
        linshi1.config(state=tk.DISABLED)
        thread1 = threading.Thread(target=main)
        thread1.start()

    def WindowEvent():
        mainmenu.attributes('-alpha', 1)
        mainmenu.focus_force()  # 强制聚焦
        UpdateTSM.destroy()

    linshi1 = ttk.Button(UpdateTSM, text='更新汉化组件', command=run, padding=(11, 5))
    linshi1.grid(row=1,column=1)
    linshi2 = ttk.Button(UpdateTSM, text='更新TSM组件', command=run2, padding=(11, 5))
    linshi2.grid(row=1,column=2)
    UpdateTSM.protocol('WM_DELETE_WINDOW', WindowEvent)

#卸载TSM
def UninstallTSM():
    mainmenu.attributes('-alpha',0.5)
    mainmenu.attributes('-topmost', False)
    UninstaTSM = tk.Toplevel()
    UninstaTSM.title("卸载TSM")

    #初始化变量
    jsondata = load_config()
    game_path = jsondata['game_path']

    # 标准卸载
    def run():
        delete_files_and_directories(game_path)
        messagebox.showinfo('成功', '卸载完毕')

    #彻底下载
    def run2():
        xuanze = messagebox.askyesno('警告','此项功能用于由于个人手动安装出现文件放错位置情况下不知道如何删除时使用。此方法将采用非游戏文件外的所有文件进行删除,但是可能会随游戏更新迭代造成游戏文件变多,如果使用后游戏无法正常启动,请使用steam校验本地文件进行修复。')
        if xuanze:
            delete_feifiles_and_directories_with_confirmation(game_path)
        else:
            UninstaTSM.focus_force()  # 强制聚焦
    def WindowEvent():
        mainmenu.attributes('-alpha', 1)
        mainmenu.focus_force()  # 强制聚焦
        UninstaTSM.destroy()

    ttk.Button(UninstaTSM, text='标准卸载', command=run, padding=(11, 5)).grid(row=1, column=1)
    ttk.Button(UninstaTSM, text='彻底卸载', command=run2, padding=(11, 5)).grid(row=1, column=2)
    UninstaTSM.protocol('WM_DELETE_WINDOW', WindowEvent)

# 重置TSM
def ResetTSM():
    jsondata = load_config()
    game_path = jsondata['game_path']

    try:
        os.remove(os.path.join(game_path, 'mods', 'TSM Resources', 'Theme.json'))
        os.remove(os.path.join(game_path, 'mods', 'TSM Resources', 'TSM.json'))
        messagebox.showinfo('成功','重置完毕')
    except FileNotFoundError as e:
        messagebox.showwarning('警告', 'TSM已经在默认状态了')
    except Exception as e:
        messagebox.showwarning('致命错误', '删除文件时发生错误')
        sys.exit(1)
# 安装其他版本
def OtherVersions():
    mainmenu.attributes('-alpha',0.5)
    mainmenu.attributes('-topmost', False)
    OtherVersiTSM = tk.Toplevel()
    OtherVersiTSM.title("安装其它版本的TSM")

    # 初始化变量
    version = tk.StringVar()

    jsondata = load_config()
    downdata = load_downconfig()
    filepath = jsondata['data_path']
    filepath = jsondata['data_path']
    game_path = jsondata['game_path']
    base_path = filepath

    #下载指定版本
    def run():
        linshi1.config(state=tk.DISABLED,text='正在进行中')
        def main():
            if jsondata['Downloadsource'] == 'github' or jsondata['Downloadsource'] == 'cloudflare':
                # print(Fore.BLUE + "INFO:正在通过GitHub下载")
                url = f"https://github.com/XeTrinityz/ThatSkyMod/releases/download/{version.get()}/TSM.zip"
            else:
                # print(Fore.BLUE + "INFO:正在通过GitHub中国代理加速地址下载")
                url = f"https://ghp.ci/https://github.com/XeTrinityz/ThatSkyMod/releases/download/{version.get()}/TSM.zip"

            # 下载TSM.zip
            save_path = os.path.join(filepath, "TSM.zip")
            start_download_window(url, save_path)
            # 解压TSM.zip
            file_name = 'TSM.zip'  # 替换为你的文件名
            full_path = create_full_path(base_path, file_name)
            game_path_mod = game_path + '/mods'
            unzip_file(create_full_path(base_path, file_name), game_path_mod)
            linshi1.config(state=tk.NORMAL, text='下载')
            messagebox.showinfo('完毕','安装成功')
            OtherVersiTSM.attributes('-alpha', 1)
            OtherVersiTSM.focus_force()  # 强制聚焦

        thread1 = threading.Thread(target=main)
        thread1.start()


    #访问GitHub确认版本号
    def run2():
        webbrowser.open("https://github.com/XeTrinityz/ThatSkyMod/releases")

    def WindowEvent():
        mainmenu.attributes('-alpha', 1)
        mainmenu.focus_force()  # 强制聚焦
        OtherVersiTSM.destroy()

    tk.Label(OtherVersiTSM, text='输入版本号', font=('微软雅黑', 11)).grid(row=1, column=1)
    tk.Entry(OtherVersiTSM,textvariable=version, font=('微软雅黑', 11)).grid(row=1, column=2)
    linshi1 = ttk.Button(OtherVersiTSM, text='下载', command=run, padding=(11, 5))
    linshi1.grid(row=2, column=1)
    ttk.Button(OtherVersiTSM, text='访问GitHub确认版本号', command=run2, padding=(11, 5)).grid(row=2, column=2)
    OtherVersiTSM.protocol('WM_DELETE_WINDOW', WindowEvent)

# 软件设置
def setup():
    mainmenu.attributes('-alpha',0.5)
    mainmenu.attributes('-topmost', False)
    option = tk.Toplevel()
    option.geometry("670x400")
    option.minsize(531, 327)
    option.title("软件设置")

    # 初始化变量
    jsondata = load_config()
    downdata = load_downconfig()
    filepath = jsondata['data_path']
    game_path = jsondata['game_path']
    regionoption = jsondata['region']
    base_path = filepath

    Proxy = jsondata['Downloadsource']
    Proxy_value = tk.StringVar(value=Proxy)
    regionvalue=tk.StringVar(value=regionoption)


    #运行方法库
    # 清除临时下载文件
    def run():
        if messagebox.askquestion('注意',f'删除会将{filepath}目录所有文件删除,请确保目录下没有重要文件') =='yes':
            delete_all_files_in_directory(filepath)
            messagebox.showinfo('成功','删除完毕')
            option.attributes('-alpha', 1)
            option.focus_force()  # 强制聚焦
        else:
            option.attributes('-alpha', 1)
            option.focus_force()  # 强制聚焦

    # 重新检测下载线路
    def run2():
        linshi2.config(state=tk.DISABLED,text='正在进行中...')
        linshi3.config(state=tk.DISABLED)

        def on_closing():
            # 自定义处理逻辑，可以弹出提示信息，或者直接不做任何操作
            messagebox.showwarning("警告", "当前仍然有进行中的任务,为防止程序出错,请等待执行完毕后再关闭")
            option.attributes('-alpha', 1)
            option.focus_force()  # 强制聚焦
        # 进入第二线程进行下载防止主窗口Windows系统认为无响应
        def main():
            option.protocol("WM_DELETE_WINDOW", on_closing)
            fastest = download_files(urls)
            if fastest:
                if fastest == 'https://mirror.ghproxy.com/https://github.com/yxsj245/Filespeedmeasurement/releases/download/main/test.txt':
                    messagebox.showinfo('成功','当前最优线路：github中国代理,与此同时汉化相关组件采用gitee网络')
                    update_config_value('Downloadsource', 'Mirrorghproxy')
                    linshi2.config(state=tk.NORMAL, text='重新检测下载线路')
                    linshi3.config(state=tk.NORMAL)
                    option.protocol("WM_DELETE_WINDOW", WindowEvent)
                    option.attributes('-alpha', 1)
                    option.focus_force()  # 强制聚焦
                elif fastest == 'https://github.com/yxsj245/Filespeedmeasurement/releases/download/main/test.txt':
                    messagebox.showinfo('成功','当前最优线路：github,与此同时汉化相关组件采用gitee网络')
                    update_config_value('Downloadsource', 'github')
                    linshi2.config(state=tk.NORMAL, text='重新检测下载线路')
                    linshi3.config(state=tk.NORMAL)
                    option.protocol("WM_DELETE_WINDOW", WindowEvent)
                    option.attributes('-alpha', 1)
                    option.focus_force()  # 强制聚焦
                elif fastest == 'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/%E6%B5%8B%E9%80%9F%E6%96%87%E4%BB%B6/test.txt':
                    messagebox.showinfo('成功','当前最优线路：cloudflare')
                    update_config_value('Downloadsource', 'cloudflare')
                    linshi2.config(state=tk.NORMAL, text='重新检测下载线路')
                    linshi3.config(state=tk.NORMAL)
                    option.protocol("WM_DELETE_WINDOW", WindowEvent)
                    option.attributes('-alpha', 1)
                    option.focus_force()  # 强制聚焦
                elif fastest == 'https://gitee.com/xiao-zhu245/filespeedmeasurement/releases/download/main/test.txt':
                    messagebox.showinfo('成功','当前最优线路：gitee')
                    update_config_value('Downloadsource', 'gitee')
                    linshi2.config(state=tk.NORMAL, text='重新检测下载线路')
                    linshi3.config(state=tk.NORMAL)
                    option.protocol("WM_DELETE_WINDOW", WindowEvent)
                    option.attributes('-alpha', 1)
                    option.focus_force()  # 强制聚焦

        thread1 = threading.Thread(target=main)
        thread1.start()

    # 更新下载源
    def run3():
        linshi1.config(state=tk.DISABLED,text='正在进行中...')
        # 进入第二线程进行下载防止主窗口Windows系统认为无响应
        def main():
            panduan = fetch_json_from_url(downdata['check'][4])
            if panduan['version'] != version_downconfig:
                messagebox.showwarning('警告','云端配置文件不兼容当前运行程序,请下载最新版程序')
                webbrowser.open("https://www.123865.com/s/4bNtVv-cioKv")
            else:
                fileurl = downdata['check'][4]
                save_path = os.path.join(os.getcwd(), "data",'down.json')
                download_file(fileurl, save_path)
                messagebox.showinfo('成功','下载配置文件成功,请重新运行程序')
                os._exit(0)

        thread1 = threading.Thread(target=main)
        thread1.start()

    # 更改下载文件临时存储目录
    def run4():
        base_path = select_directory(Fore.BLUE + "INFO:请选择文件存放目录")
        update_config_value('data_path', base_path)
        option.attributes('-alpha', 1)
        option.focus_force()  # 强制聚焦

    # 更改游戏目录
    def run5():
        game_path = select_directory(Fore.BLUE + "INFO:请选择游戏根目录")
        update_config_value('game_path', game_path)
        option.attributes('-alpha', 1)
        option.focus_force()  # 强制聚焦

    # 确认更改
    def Apply():
        update_config_value('Downloadsource', Proxy_value.get())
        update_config_value('region', regionvalue.get())
        # 重载方法
        downreload()
        option.destroy()
        mainmenu.attributes('-alpha', 1)
        mainmenu.focus_force()  # 强制聚焦
        # messagebox.showinfo('成功','设置成功,请重启生效.')
        # sys.exit(0)

    def WindowEvent():
        mainmenu.attributes('-alpha', 1)
        mainmenu.focus_force()  # 强制聚焦
        option.destroy()

    # 标题
    tk.Label(option, text='————设置项————', font=('微软雅黑', 16)).place(relx=0.5, y=50, anchor='center')
    tk.Label(option, text='————目录————', font=('微软雅黑', 16)).place(relx=0.5, y=150, anchor='center')
    tk.Label(option, text='————信息————', font=('微软雅黑', 16)).place(relx=0.5, y=250, anchor='center')


    # 按钮
    ttk.Button(option, text='清除临时下载文件', command=run, padding=(10, 5)).place(relx=0.2, y=100,anchor='center')
    linshi2 = ttk.Button(option, text='重新检测下载线路', command=run2, padding=(10, 5))
    linshi2.place(relx=0.4, y=100,anchor='center')
    linshi1 = ttk.Button(option, text='更新下载源', command=run3, padding=(10, 5))
    linshi1.place(relx=0.6, y=100,anchor='center')
    ttk.Button(option, text='更改下载文件临时存储目录', command=run4, padding=(10, 5)).place(relx=0.2, y=200,anchor='center')
    ttk.Button(option, text='更改游戏目录', command=run5, padding=(10, 5)).place(relx=0.5, y=200,anchor='center')

    option.protocol('WM_DELETE_WINDOW', WindowEvent)

    # 动态文本
    tk.Label(option, text='下载源：', font=('微软雅黑', 11)).place(relx=0.1, y=270, anchor='center')
    # 下载源
    combobox = ttk.Combobox(option,textvariable=Proxy_value,state="readonly",width=20)
    combobox['values']=['gitee','cloudflare','Mirrorghproxy','github','other']
    combobox.place(relx=0.3, y=270, anchor='center')
    # 延迟显示
    option.after(1, lambda: combobox.set(Proxy))

    # 区域语言
    tk.Label(option, text='区域语言：', font=('微软雅黑', 11)).place(relx=0.1, y=310, anchor='center')
    region = ttk.Combobox(option, textvariable=regionvalue, state="readonly", width=20)
    region['values'] = ['简体中文','繁体中文']
    region.place(relx=0.3, y=310, anchor='center')
    option.after(1, lambda: region.set(regionoption))

    linshi3 = ttk.Button(option, text='确认', command=Apply, padding=(10, 10),width=50)
    linshi3.place(relx=0.5, y=370, anchor='center')
# 安装VC
def installVC():
    # 初始化变量
    jsondata = load_config()
    filepath = jsondata['data_path']

    # print(Fore.BLUE + 'INFO:开始下载VC')
    fileurl = down_5
    save_path = os.path.join(filepath, "VC_redist.x64.exe")
    start_download_window(fileurl, save_path)
    exe_path = os.path.join(filepath, "VC_redist.x64.exe")
    subprocess.run(exe_path)

    mainmenu.attributes('-alpha', 1)
    mainmenu.focus_force()  # 强制聚焦

# 播放音频
def startMp3():
    stop_event = threading.Event()
    Mp3list=['https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/TSM%E7%BB%84%E4%BB%B6/MP3/%E8%83%A1%E5%B0%8F%E9%B8%A5%20-%20%E7%9B%B8%E8%AE%B8.mp3',
             'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/TSM%E7%BB%84%E4%BB%B6/MP3/Vincent%20Diamante%20-%20Finding%20the%20Horizon.mp3',
             'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/TSM%E7%BB%84%E4%BB%B6/MP3/Vincent%20Diamante%20-%20Returns.mp3']
    def run():
        while not stop_event.is_set():
            if stop_event.is_set(): return
            linshi = random.randint(0, len(Mp3list) - 1)
            music(Mp3list[linshi])

    def stop():
        stop_event.set()
        but1.config(text='播放音乐边听边用', command=startMp3)

    but1.config(text='停止下一首的播放',command=stop)
    mp3 = threading.Thread(target=run)
    mp3.daemon = True
    mp3.start()

# TSM状态
def TSMstateTSM():
    jsondata = load_config()
    game_path = jsondata['game_path']
    if stateTSM.get() == '启用':
        path = os.getcwd()
        path = os.path.join(path, 'TemporaryTSM')
        #
        files_to_delete = [
            "libcurl.dll",
            "powrprof.dll",
            "sml_config.json"
        ]

        directories_to_delete = [
            "fonts",
            "mods"
        ]
        move_files_and_directories(path, files_to_delete, directories_to_delete, game_path)
        messagebox.showinfo('成功','完毕')
    else:
        path = os.getcwd()
        path = os.path.join(path,'TemporaryTSM')
        #
        files_to_delete = [
            "libcurl.dll",
            "powrprof.dll",
            "sml_config.json"
        ]

        directories_to_delete = [
            "fonts",
            "mods"
        ]
        move_files_and_directories(game_path, files_to_delete, directories_to_delete, path)
        messagebox.showinfo('成功','完毕')
#————软件信息————
def github():
    webbrowser.open("https://github.com/yxsj245/TSMpackagemanager")

def gitee():
    webbrowser.open("https://gitee.com/xiao-zhu245/TSMpackagemanager")

def DocumentStation():
    webbrowser.open("https://tsmpackagemanager.skymusicscore.asia/WEB/")

def sponsor():
    webbrowser.open("https://www.goofish.com/item?id=830106258067&spm=widle.12011849.copy.detail&ut_sk=1.ZK1cY5c8vMgDADyNPjuw0sjp_21407387_1728812506853.copy.detail.830106258067.2200699006720")
    webbrowser.open("https://tsmpackagemanager.skymusicscore.asia/WEB/#/docs/%E4%BD%BF%E7%94%A8%E8%AF%BE%E7%A8%8B?id=%e4%b8%ba%e4%bb%80%e4%b9%88%e8%a6%81%e8%b5%9e%e5%8a%a9%ef%bc%9f")

# 主菜单设置
global mainmenu
global but1
global installOne
global installTwo
global stateTSM
mainmenu = tk.Tk()
mainmenu.geometry("600x450")  # 设置窗口大小
mainmenu.minsize(450,382)
mainmenu.title('TSM包管理器4.4')

# 变量
stateTSM=tk.StringVar()


# 检测运行环境
checkzation()
# 运行初始化方法
initialization()

def WindowEvent():
    os._exit(0)


tk.Label(mainmenu, text='————功能区————', font=('微软雅黑', 16)).place(relx=0.5, y=40, anchor='center')
tk.Label(mainmenu, text='————软件区————', font=('微软雅黑', 16)).place(relx=0.5, y=220, anchor='center')

# ——主菜单按钮——
# TSM相关功能
button_padding = (10, 5)
installOne = ttk.Button(mainmenu, text='一键安装', command=OneclickinstallationTSM, padding=button_padding)
installOne.place(relx=0.2, y=90, anchor='center')
installTwo = ttk.Button(mainmenu, text='从本地文件安装', command=Localfileinstallation, padding=button_padding)
installTwo.place(relx=0.4, y=90, anchor='center')
ttk.Button(mainmenu, text='更新', command=UpdateTSM, padding=button_padding).place(relx=0.6, y=90, anchor='center')
ttk.Button(mainmenu, text='一键卸载', command=UninstallTSM, padding=button_padding).place(relx=0.8, y=90, anchor='center')
ttk.Button(mainmenu, text='安装其它版本', command=OtherVersions, padding=button_padding).place(relx=0.2, y=140, anchor='center')
ttk.Button(mainmenu, text='安装VC', command=installVC, padding=button_padding).place(relx=0.4, y=140, anchor='center')
ttk.Button(mainmenu, text='故障排除', command=Troubleshooting, padding=button_padding, width=10).place(relx=0.6, y=140, anchor='center')
ttk.Button(mainmenu, text='重置TSM', command=ResetTSM, padding=button_padding, width=10).place(relx=0.8, y=140, anchor='center')

ttk.Label(mainmenu, text='TSM状态：', padding=button_padding, width=10).place(relx=0.2, y=180, anchor='center')
ttk.Radiobutton(mainmenu,text='启用',variable=stateTSM,value='启用').place(relx=0.3, y=180, anchor='center')
ttk.Radiobutton(mainmenu,text='禁用',variable=stateTSM,value='禁用').place(relx=0.4, y=180, anchor='center')
ttk.Button(mainmenu, text='确认更改', command=TSMstateTSM, padding=button_padding, width=10).place(relx=0.6, y=180, anchor='center')

# 软件信息部分
ttk.Button(mainmenu, text='软件设置', command=setup, padding=(10, 10), width=25).place(relx=0.5, y=260, anchor='center')
ttk.Button(mainmenu, text='前往GitHub查看开源代码', command=github, padding=(10, 10), width=25).place(relx=0.27, y=310, anchor='center')
ttk.Button(mainmenu, text='前往Gitee查看开源代码', command=gitee, padding=(10, 10), width=25).place(relx=0.7, y=310, anchor='center')

ttk.Button(mainmenu, text='软件文档站', command=DocumentStation, padding=(10, 10), width=25).place(relx=0.27, y=360, anchor='center')
ttk.Button(mainmenu, text='前往赞助软件', command=sponsor, padding=(10, 10), width=25).place(relx=0.7, y=360, anchor='center')



but1 = ttk.Button(mainmenu,text='播放音乐边听边用',command=startMp3,padding=(10, 5),width=50)
but1.place(relx=0.5, y=400, anchor='center')

mainmenu.protocol('WM_DELETE_WINDOW', WindowEvent)

# 开启窗口
mainmenu.mainloop()