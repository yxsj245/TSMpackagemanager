#——————运行库——————
import zipfile
import hashlib
import sys
import tkinter as tk
from tkinter import filedialog
import winreg
from tqdm import tqdm
import shutil
import requests
import json
from tkinter import ttk
from tkinter import messagebox
import os
import threading
import pyperclip
from urllib.parse import unquote
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Back, Style
import colorama
import psutil
import webbrowser

#——————方法库——————
# 初始化变量
url = None
base_path = None  # 文件路径
game_path = None # 游戏路径
fileurl = None  #云端链接
filepath = None #临时存储文件路径
version_config = '0.5' #配置文件版本 切记需要更改创建配置文件方法内版本
version_downconfig = '0.1' #下载配置文件版本 切记需要更改创建配置文件方法内版本
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

# 检测Sky进程
def monitor_process():
    process_name = "Sky.exe"

    # 一直检测直到检测到 sky.exe 进程
    while True:
        # 检测是否有名为 sky.exe 的进程
        process_exists = any(proc.name() == process_name for proc in psutil.process_iter())

        if process_exists:
            print(f"检测到 {process_name}，开始计时20秒")
            start_time = time.time()

            # 开始计时20秒，期间每秒检测一次进程是否存在
            while time.time() - start_time < 20:
                process_exists = any(proc.name() == process_name for proc in psutil.process_iter())

                if not process_exists:
                    print(f"{process_name} 已退出")
                    return True  # 返回成功，进程在20秒内退出

                time.sleep(1)

            print(f"{process_name} 在20秒内未退出")
            return False  # 返回失败，进程未在20秒内退出
        else:
            # 如果没检测到进程，继续每秒检查
            time.sleep(1)

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
                if url == 'https://mirror.ghproxy.com/https://github.com/yxsj245/Filespeedmeasurement/releases/download/main/test.txt':
                    print(f"github中国代理网络：下载速度: {average_speed:.2f} MB/s")
                elif url == 'https://github.com/yxsj245/Filespeedmeasurement/releases/download/main/test.txt':
                    print(f"github网络：下载速度: {average_speed:.2f} MB/s")
                elif url == 'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/%E6%B5%8B%E9%80%9F%E6%96%87%E4%BB%B6/test.txt':
                    print(f"cloudflare网络：下载速度: {average_speed:.2f} MB/s")
                elif url == 'https://gitee.com/xiao-zhu245/filespeedmeasurement/releases/download/main/test.txt':
                    print(f"gitee网络：下载速度: {average_speed:.2f} MB/s")
                if elapsed_time < fastest_time:
                    fastest_time = elapsed_time
                    fastest_url = url

    return fastest_url  # 仅返回最快的URL
# 打开Windows资源管理器
def open_directory_in_explorer(directory_path):
    try:
        os.startfile(directory_path)
        print('启动成功')
    except Exception as e:
        print(f"无法打开目录 {directory_path}: {e}")
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
            "version":"0.5",
            "first": True,
            "game_path": None,
            "data_path": None,
            "Downloadsource": None
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
            "version": "0.1",
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
                    'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/TSM%E7%BB%84%E4%BB%B6/VC_redist.x64.exe'
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
                'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/data_hanhua.json',
                'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/%E7%A4%BE%E5%8C%BA%E8%B5%84%E6%BA%90/datadc.json',
                'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/%E7%A4%BE%E5%8C%BA%E8%B5%84%E6%BA%90/datacode.json'
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
        print(Fore.RED+"ERROR:注册表项或数值名称不存在。")
    except Exception as e:
        print(Fore.RED+f"ERROR:读取注册表时发生错误: {e}")
    return None


# 解压文件的方法
def unzip_file(zip_path, extract_to):
    # 检查文件是否为zip格式
    if zipfile.is_zipfile(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 解压缩所有文件到目标目录
            zip_ref.extractall(extract_to)
    else:
        print(Fore.RED+"ERROR:指定的文件不是有效的ZIP文件")

#校验MD5方法
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
            print(Fore.YELLOW + f"WARN:文件信息校验码不匹配: {file_path}")
            print("提示：可能是您下载了错误的版本或者下载过程中文件出现损坏。请重新下载上行路径输出的末尾的文件替换到此目录。如果是新版本更新可能没有及时更新云端文件信息所致，您可以按任意键跳过，但是这将可能导致TSM不在预期内运行。")
            input()
            return True
    except FileNotFoundError:
        print(Fore.RED+f"ERROR:文件缺失: {file_path}")
        print("提示：在最新版本中，此错误不应当出现，请联系作者排查。")
        input()
        sys.exit(1)  # 终止程序运行并返回状态码1

def fetch_json_from_url(url):
    try:
        response = requests.get(url, timeout=30)  # 设置超时时间为10秒
        response.raise_for_status()  # 如果请求失败则抛出HTTPError异常
        return response.json()
    except requests.exceptions.RequestException as e:
        print(Fore.RED+f"ERROR:从云端拉取文件信息失败: {e}")
        print(Fore.YELLOW + "WARN:跳过鉴权文件信息，无法保证文件完整，这可能会导致TSM不在预期内运行。")
        return None

#
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
        print(Fore.RED+"ERROR:没有选择目录")
        input()
        sys.exit(1)  # 终止程序运行并返回状态码1

# 拼接路径
def create_full_path(base_path, file_name):
    # 确保base_path以斜杠结尾，然后拼接文件名
    if not base_path.endswith('/'):
        base_path += '/'
    full_path = base_path + file_name
    return full_path
# 下载文件
def download_file_with_progress(url, save_path):
    try:
        # 检查并创建保存文件的目录
        directory = os.path.dirname(save_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 发送 HTTP GET 请求获取文件信息
        response = requests.get(url, stream=True, allow_redirects=True)
        response.raise_for_status()  # 检查请求是否成功

        # 检查内容类型，确保下载的是 ZIP 文件而不是 HTML 等其他内容
        content_type = response.headers.get('Content-Type')
        if 'text/html' in content_type:
            print(Fore.RED + "ERROR:请求返回了HTML内容，可能URL无效或需要权限。")
            return

        # 获取文件的总大小（字节）
        total_size = int(response.headers.get('content-length', 0))

        # 通过 tqdm 显示进度条
        with open(save_path, 'wb') as file, tqdm(
                desc=save_path,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
        ) as progress_bar:
            # 分块下载文件
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                progress_bar.update(len(chunk))  # 更新进度条

        print(Fore.BLUE + f"INFO:文件已下载到临时存储目录")
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"ERROR:下载文件时出错: {e}")

# 删除文件
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
                print(Fore.BLUE + f"INFO:已删除文件: {file_path}")
            else:
                print(Fore.RED+f"ERROR:文件未找到: {file_path}")
        except Exception as e:
            print(Fore.RED+f"ERROR:删除文件时出错: {file_path}, 错误: {e}")

    # 删除目录
    for dir_name in directories_to_delete:
        dir_path = os.path.join(target_directory, dir_name)
        try:
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)
                print(Fore.BLUE + f"INFO:已删除目录: {dir_path}")
            else:
                print(Fore.RED+f"ERROR:目录未找到: {dir_path}")
        except Exception as e:
            print(Fore.RED+f"ERROR:删除目录时出错: {dir_path}, 错误: {e}")
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
                print(f"删除 {file_path} 时出错: {e}")
    else:
        print(f"{directory_path} 不是一个有效的目录")

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

    # 提示用户确认
    print("以下文件和目录将被删除:")
    print("\n文件:")
    for file_path in files_to_delete:
        print(file_path)
    print("\n目录:")
    for dir_path in directories_to_delete:
        print(dir_path)

    confirmation = input("确认删除这些文件和目录吗？(y/n): ").lower()
    if confirmation != 'y':
        print("取消删除操作。")
        return

    # 删除文件
    for file_path in files_to_delete:
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(Fore.BLUE + f"INFO: 已删除文件: {file_path}")
            else:
                print(Fore.RED+f"ERROR: 文件未找到: {file_path}")
        except Exception as e:
            print(Fore.RED+f"ERROR: 删除文件时出错: {file_path}, 错误: {e}")

    # 删除目录
    for dir_path in directories_to_delete:
        try:
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)
                print(Fore.BLUE + f"INFO: 已删除目录: {dir_path}")
            else:
                print(Fore.RED+f"ERROR: 目录未找到: {dir_path}")
        except Exception as e:
            print(Fore.RED+f"ERROR: 删除目录时出错: {dir_path}, 错误: {e}")
# -------自己的程序执行方法库
# 故障排除
def Troubleshooting(game_path):
    print('=====')
    print(Fore.YELLOW + '按照实际情况，选择开始游戏后的问题')
    print(Fore.GREEN+'1.游戏启动后没有显示任何窗口\n'
                     '2.游戏启动后出现游戏窗口但很快消失')
    print('=====')
    xuanze = input("请输入选项数字: ")
    if xuanze == '1':
        print(Fore.BLUE + "INFO:开始下载VC运行库,稍后请点击安装后重启电脑再次尝试启动游戏")
        fileurl = down_5
        save_path = os.path.join(filepath, "VC_redist.x64.exe")
        download_file_with_progress(fileurl, save_path)
        exe_path = os.path.join(filepath, "VC_redist.x64.exe")
        subprocess.run(exe_path)
    else:
        try:
            os.remove(os.path.join(game_path, 'mods','demo.dll'))
        except FileNotFoundError:
            print(Fore.RED + 'ERROR:文件不存在：可能您已运行过此解决方案')
            input()
            sys.exit(1)
        print(Fore.BLUE + "INFO:修复完毕,正在为您启动游戏")
        os.startfile(f"steam://rungameid/{app_id}")
        print(Fore.BLUE + "INFO:开始监控游戏进程")
        result = monitor_process()
        if result:
            print(Fore.YELLOW + 'WARN:检测到游戏进程在启动后结束,是否进行尝试自动修复？')
            xuanze = input('输入y表示开始修复')
            if xuanze == 'y':
                print(Fore.BLUE + "INFO:开始下载VC运行库,稍后请点击安装后重启电脑再次尝试启动游戏")
                fileurl = down_5
                save_path = os.path.join(filepath, "VC_redist.x64.exe")
                download_file_with_progress(fileurl, save_path)
                exe_path = os.path.join(filepath, "VC_redist.x64.exe")
                subprocess.run(exe_path)

        else:
            print(Fore.BLUE + "游戏启动成功,问题已解决")

#——————程序运行入口——————
print(Fore.BLUE + 'INFO:程序初始化')
print(Fore.YELLOW +'程序版本3.0.1-beta')
# 环境初始化
# 初始配置文件json
config = load_config()
if config is None:
    create_default_config()
    config = load_config()
    print(Fore.BLUE + "INFO:创建程序配置文件")
# 初始下载配置文件
down = load_downconfig()
if down is None:
    create_default_downconfig()
    config = load_downconfig()
    print(Fore.BLUE + "INFO:创建程序下载地址配置文件")
if load_config()['first']:
    print(Fore.BLUE + "INFO:执行初始化设置向导")
    print(Fore.BLUE + "INFO:设置游戏目录(1/2)")
    game_path=get_game_install_location()
    if game_path == None:
        print(Fore.YELLOW + "WARN:获取游戏路径失败，需要手动选择")
        game_path= select_directory(Fore.BLUE + "INFO:请选择游戏根目录")
    else:
        print(Fore.BLUE + "INFO:您的游戏安装目录为：", game_path,
              '\n 是否正确,如果不正确输入n进行手动选择游戏目录,反则按任意键继续...')
        xuanze = input()
        if xuanze == 'n':
            game_path = select_directory(Fore.BLUE + "INFO:请选择游戏根目录")
    update_config_value('game_path', game_path)
    # INFO:设置下载的临时文件存储位置
    filepath=os.getcwd()
    filepath = os.path.join(filepath, 'Downloadedfiles')
    update_config_value('data_path', filepath)
    print(Fore.BLUE + "INFO:正在检测最优线路,预计20秒,请耐心等待..(2/2)")
    # update_config_value('Downloadsource', 'Mirrorghproxy')
    fastest = download_files(urls)
    if fastest:
        if fastest == 'https://mirror.ghproxy.com/https://github.com/yxsj245/Filespeedmeasurement/releases/download/main/test.txt':
            print(Fore.BLUE + 'INFO:当前最优线路：github中国代理,与此同时汉化相关组件采用gitee网络')
            update_config_value('Downloadsource', 'Mirrorghproxy')
        elif fastest == 'https://github.com/yxsj245/Filespeedmeasurement/releases/download/main/test.txt':
            print(Fore.BLUE + 'INFO:当前最优线路：github,与此同时汉化相关组件采用cloudlfare网络')
            update_config_value('Downloadsource', 'github')
        elif fastest == 'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/%E6%B5%8B%E9%80%9F%E6%96%87%E4%BB%B6/test.txt':
            print(Fore.BLUE + 'INFO:当前最优线路：cloudflare')
            update_config_value('Downloadsource', 'cloudflare')
        elif fastest == 'https://gitee.com/xiao-zhu245/filespeedmeasurement/releases/download/main/test.txt':
            print(Fore.BLUE + 'INFO:当前最优线路：gitee')
            update_config_value('Downloadsource', 'gitee')
    print(Fore.BLUE + 'INFO:设置向导完毕。如有设置错误可以在菜单种重新设置')
    update_config_value('first', False)
# 设置变量值
try:
    jsondata = load_config()
    downdata = load_downconfig()
    filepath = jsondata['data_path']
    game_path = jsondata['game_path']
    base_path = filepath
    url = downdata['check'][0]
    #--下载源设置---
    if jsondata['Downloadsource'] == 'gitee':
        print(Style.BRIGHT + Fore.CYAN + 'INFO:温馨提示：当前下载线路采用分流模式,TSM组件会受到作者上传速度影响,如需下载最新版可以使用序号4功能')
        down_1 = downdata['downloadurl']['gitee'][0]
        down_2 = downdata['downloadurl']['gitee'][1]
        down_3 = downdata['downloadurl']['gitee'][2]
        down_4 = downdata['downloadurl']['gitee'][3]
        down_5 = downdata['downloadurl']['gitee'][4]
    elif jsondata['Downloadsource'] == 'cloudflare':
        print(Style.BRIGHT + Fore.CYAN + 'INFO:温馨提示：当前下载线路采用分流模式,TSM组件会受到作者上传速度影响,如需下载最新版可以使用序号4功能')
        down_1 = downdata['downloadurl']['cloudflare'][0]
        down_2 = downdata['downloadurl']['cloudflare'][1]
        down_3 = downdata['downloadurl']['cloudflare'][2]
        down_4 = downdata['downloadurl']['cloudflare'][3]
        down_5 = downdata['downloadurl']['cloudflare'][4]
    elif jsondata['Downloadsource'] == 'Mirrorghproxy':
        print(Style.BRIGHT + Fore.CYAN + 'INFO:温馨提示：当前下载线路采用github,一键功能下载到的TSM组件为最新版')
        down_1 = downdata['downloadurl']['Mirrorghproxy'][0]
        down_2 = downdata['downloadurl']['Mirrorghproxy'][1]
        down_3 = downdata['downloadurl']['Mirrorghproxy'][2]
        down_4 = downdata['downloadurl']['Mirrorghproxy'][3]
        down_5 = downdata['downloadurl']['Mirrorghproxy'][4]
    elif jsondata['Downloadsource'] == 'github':
        print(Style.BRIGHT + Fore.CYAN + 'INFO:温馨提示：当前下载线路采用github,一键功能下载到的TSM组件为最新版')
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
    print(Fore.RED+"ERROR:检测到配置文件与主程序不兼容或损坏,已删除,请重新运行程序")
    input()
    sys.exit(1)
if jsondata['version'] != version_config:
    os.remove('data/config.json')
    print(Fore.RED+"ERROR:检测到“程序配置文件”需要更新,请重新运行程序即可")
    input()
    sys.exit(1)
if downdata['version'] != version_downconfig:
    os.remove('down.json')
    print(Fore.RED+"ERROR:检测到“下载源配置文件”需要更新,请重新运行程序即可")
    input()
    sys.exit(1)
print('=====')
print(Fore.GREEN+"1.【安装/更新】一键安装/更新 所有TSM\n"
      "2.【安装/更新】从本地文件安装TSM\n"
      "4.【更新】更新TSM外挂\n"
      "3.【卸载】一键卸载TSM\n"
      "6.【社区】安装社区插件功能\n"
      "7.【社区】复制社区提供的运行代码\n"
      "8.【程序】设置\n"
      "9.【安装】下载VC运行库(无法启动请使用)\n"
                 "10.【帮助与支持】TSM使用指南")
print('=====')
choice = input("请输入选项数字: ")
if choice == "1":
    print(Fore.BLUE + "INFO:开始下载文件")
    # 下载TSM.zip
    fileurl = down_1
    save_path = os.path.join(filepath, "TSM.zip")
    download_file_with_progress(fileurl, save_path)
    # 下载sml-pc.zip
    fileurl = down_2
    save_path = os.path.join(filepath, "sml-pc.zip")
    download_file_with_progress(fileurl, save_path)
    # 下载TSM_font.zip
    fileurl = down_3
    save_path = os.path.join(filepath, "TSM_font.zip")
    download_file_with_progress(fileurl, save_path)
    # 下载TSMmap-ZH_CN.zip
    fileurl = down_4
    save_path = os.path.join(filepath, "TSMmap-ZH_CN.zip")
    download_file_with_progress(fileurl, save_path)
    print(Fore.BLUE + "INFO:开始校验文件信息")
    # 获取JSON数据
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
                print(Fore.RED+"ERROR:JSON数据中缺少文件名或MD5值，跳过该项。")
    print(Fore.BLUE + "INFO:文件信息校验完毕。")

    print(Fore.BLUE + "INFO:开始解压文件")
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
    print(Fore.BLUE + "INFO:解压完毕，请在steam中启动游戏，如果启动后崩溃请安装VC运行库")
    xuanze = input('输入y启动游戏并检测是否安装成功')
    if xuanze == 'y':
        print(Fore.BLUE + "INFO:调用steam启动游戏中...")
        os.startfile(f"steam://rungameid/{app_id}")
        print(Fore.BLUE + "INFO:开始监控游戏进程")
        result = monitor_process()
        if result:
            print(Fore.YELLOW + 'WARN:检测到游戏进程在启动后结束,是否运行故障排除向导？')
            xuanze = input('输入y进行故障排除')
            if xuanze == 'y':
                Troubleshooting(game_path)

        else:
            print(Fore.BLUE + "游戏启动成功")
    input()
elif choice == "2":
    print(Fore.YELLOW + 'WARN:本地安装将不在进行文件校验，无法保证文件完好无损以及是否为官方版本，请自行斟酌！')
    print(Fore.BLUE + "INFO:请选择TSM文件下载的目录")
    base_path=select_directory("请选择TSM文件下载的目录")
    print(Fore.BLUE + "INFO:开始解压文件")
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
    print(Fore.BLUE + "INFO:解压完毕，请在steam中启动游戏，如果启动后崩溃请安装VC运行库")
    xuanze = input('输入y启动游戏并检测是否安装成功')
    if xuanze == 'y':
        print(Fore.BLUE + "INFO:调用steam启动游戏中...")
        os.startfile(f"steam://rungameid/{app_id}")
        print(Fore.BLUE + "INFO:开始监控游戏进程")
        result = monitor_process()
        if result:
            print(Fore.YELLOW + 'WARN:检测到游戏进程在启动后结束,是否运行故障排除向导？')
            xuanze = input('输入y进行故障排除')
            if xuanze == 'y':
                Troubleshooting(game_path)

        else:
            print(Fore.BLUE + "游戏启动成功")
    input()
elif choice == "3":
    print('=====')
    print(Fore.GREEN+'1.标准卸载(默认)\n'
          '2.彻底卸载(慎用)')
    print('=====')
    xuanze = input("请输入选项数字: ")
    if xuanze == '2':
        print(Back.YELLOW + Fore.RED+'WARN:请注意：此项功能用于由于个人手动安装出现文件放错位置情况下不知道如何删除时使用。此方法将采用非游戏文件外的所有文件进行删除,但是可能会随游戏更新迭代造成游戏文件变多,如果使用后游戏无法正常启动,请使用steam校验本地文件进行修复。')
        xuanze = input('输入y表示确认')
        if xuanze == 'y':
            delete_feifiles_and_directories_with_confirmation(game_path)
    else:
        delete_files_and_directories(game_path)
    print(Fore.BLUE + "INFO:卸载完毕")
elif choice == "4":
    print(Fore.BLUE + "INFO:将通过代理地址加速访问github，您的下载速度会得到很大提升，但可能存在失效和下载失败概率")
    print(Fore.YELLOW + "WARN:由于官方不提供校验码。下载后的文件不会进行文件鉴权，可能存在下载后文件损坏风险。")
    print('请选择需要更新的组件')
    print('=====')
    print(Fore.GREEN+'1.TSM相关组件 '
          '\n 2.汉化相关组件（默认）')
    print('=====')
    xuanze = input("请输入选项数字: ")
    if xuanze == '1':
        # 下载TSM.zip
        fileurl = downdata['downloadurl']['Mirrorghproxy'][0]
        save_path = os.path.join(filepath, "TSM.zip")
        download_file_with_progress(fileurl, save_path)
        # 下载sml-pc.zip
        fileurl = downdata['downloadurl']['Mirrorghproxy'][1]
        save_path = os.path.join(filepath, "sml-pc.zip")
        download_file_with_progress(fileurl, save_path)
        print(Fore.BLUE + "INFO:文件下载完毕")
        print(Fore.BLUE + "INFO:开始解压文件")
        # 解压sml-pc.zip
        file_name = 'sml-pc.zip'  # 替换为你的文件名
        full_path = create_full_path(base_path, file_name)
        unzip_file(create_full_path(base_path, file_name), game_path)
        # 解压TSM.zip
        file_name = 'TSM.zip'  # 替换为你的文件名
        full_path = create_full_path(base_path, file_name)
        game_path_mod = game_path + '/mods'
        unzip_file(create_full_path(base_path, file_name), game_path_mod)
        print(Fore.BLUE + "INFO:解压完毕")
        print(Fore.GREEN+"默认没有中文，如有需要请重新运行脚本选择下载汉化。")
        input()
    else:
        # 下载TSM_font.zip
        fileurl = down_3
        save_path = os.path.join(filepath, "TSM_font.zip")
        download_file_with_progress(fileurl, save_path)
        # 下载TSMmap-ZH_CN.zip
        fileurl = down_4
        save_path = os.path.join(filepath, "TSMmap-ZH_CN.zip")
        download_file_with_progress(fileurl, save_path)
        print(Fore.BLUE + "INFO:文件下载完毕")
        print(Fore.BLUE + "INFO:开始校验文件信息")
        # 获取JSON数据
        url = downdata['check'][1]
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
                    print(Fore.RED+"ERROR:JSON数据中缺少文件名或MD5值，跳过该项。")
        print(Fore.BLUE + "INFO:文件信息校验完毕。")
        print(Fore.BLUE + "INFO:开始解压文件")
        # 解压TSM_font.zip
        file_name = 'TSM_font.zip'  # 替换为你的文件名
        full_path = create_full_path(base_path, file_name)
        unzip_file(create_full_path(base_path, file_name), game_path)
        # 解压TSMmap-ZH_CN.zip
        file_name = 'TSMmap-ZH_CN.zip'  # 替换为你的文件名
        full_path = create_full_path(base_path, file_name)
        unzip_file(create_full_path(base_path, file_name), game_path)
        print(Fore.BLUE + "INFO:解压完毕，请在steam中启动游戏，如果启动后崩溃请安装VC运行库")
        input()
elif choice == "6":

    print(Fore.YELLOW + "WARN:当前使用的是社区功能,请注意这些脚本以及信息来源于全球玩家贡献，无法确保安全和稳定性，请自行斟酌！")
    def fetch_data_from_url(url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # 确保请求成功
            return response.json()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch data from URL: {e}")
            return None


    def fetch_data_from_local(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Failed to fetch data from local file: {e}")
            return None


    def download_file_with_progress(url, save_path, progress_bar, root, install_button):
        try:
            response = requests.get(url, stream=True, allow_redirects=True)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type')
            if 'text/html' in content_type:
                messagebox.showerror("Error", "请求返回了HTML内容，可能URL无效或需要权限。")
                return

            total_size = int(response.headers.get('content-length', 0))
            progress_bar["maximum"] = total_size

            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    progress_bar["value"] += len(chunk)
                    root.update_idletasks()

            messagebox.showinfo("完成", f"文件已下载并安装,请重启游戏生效。")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"下载文件时出错: {e}")
        finally:
            install_button.config(state=tk.NORMAL, text="安装")


    def install_application(down, puth, progress_bar, root, install_button):
        progress_bar["value"] = 0
        decoded_filename = unquote(down.split('/')[-1])  # 解码文件名中的百分号
        save_path = os.path.join(puth, decoded_filename)

        install_button.config(state=tk.DISABLED, text="正在下载...")

        download_thread = threading.Thread(target=download_file_with_progress,
                                           args=(down, save_path, progress_bar, root, install_button))
        download_thread.start()


    def create_interface(data):
        root = tk.Tk()
        root.title("动态 JSON 数据界面")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        window_width = int(screen_width * 0.3)
        window_height = int(screen_height * 0.3)
        root.geometry(f"{window_width}x{window_height}")

        canvas = tk.Canvas(root)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        row_counter = 0

        for entry in data:
            name = entry.get("name", "No Name")
            txt = entry.get("txt", "No Description")
            down = entry.get("down", "")
            puth = entry.get("puth", "")
            puth = game_path + puth

            ttk.Label(scrollable_frame, text=f"名称: {name}").grid(row=row_counter, column=0, sticky=tk.W, pady=2)
            ttk.Label(scrollable_frame, text=f"描述: {txt}").grid(row=row_counter + 1, column=0, sticky=tk.W, pady=2)

            progress_bar = ttk.Progressbar(scrollable_frame, orient="horizontal", length=200, mode="determinate")
            progress_bar.grid(row=row_counter + 4, column=0, pady=5)

            install_button = ttk.Button(scrollable_frame, text="安装")
            install_button.config(
                command=lambda d=down, p=puth, pb=progress_bar, ib=install_button: install_application(d, p, pb, root,
                                                                                                       ib))
            install_button.grid(row=row_counter + 5, column=0, pady=10)

            row_counter += 6

        root.mainloop()


    def main():
        fetch_from_url = True

        if fetch_from_url:
            url = downdata['check'][2]
            print(Fore.BLUE + "INFO:加载窗体控件，如果没有正常显示，请查看通知栏。")
            print(Fore.BLUE + "INFO:正在从云端拉取数据,请确保网络通畅....")
            data = fetch_data_from_url(url)
        else:
            local_file = "datadc.json"
            data = fetch_data_from_local(local_file)

        if data:
            create_interface(data)


    if __name__ == "__main__":
        main()

elif choice == "7":
    print(Fore.BLUE + "INFO:加载窗体控件，如果没有正常显示，请查看通知栏。")
    messagebox.showinfo("温馨提示", "当前使用的是社区功能,请注意这些脚本以及信息来源于全球玩家贡献，无法确保安全和稳定性，请自行斟酌！")
    messagebox.showinfo("使用帮助", "此功能适用于TSM的代码运行功能，复制后请前往“TSM-自定义命令”进行执行")
    def fetch_data_from_url(url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # 确保请求成功
            return response.json()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch data from URL: {e}")
            return None


    def fetch_data_from_local(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Failed to fetch data from local file: {e}")
            return None


    def download_file_with_progress(url, save_path, progress_bar, root, install_button):
        try:
            response = requests.get(url, stream=True, allow_redirects=True)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type')
            if 'text/html' in content_type:
                messagebox.showerror("Error", "请求返回了HTML内容，可能URL无效或需要权限。")
                return

            total_size = int(response.headers.get('content-length', 0))
            progress_bar["maximum"] = total_size

            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    progress_bar["value"] += len(chunk)
                    root.update_idletasks()

            messagebox.showinfo("完成", f"文件已下载并安装")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"下载文件时出错: {e}")
        finally:
            install_button.config(state=tk.NORMAL, text="安装")


    def install_application(down, puth, progress_bar, root, install_button):
        progress_bar["value"] = 0
        save_path = os.path.join(puth, down.split('/')[-1])

        install_button.config(state=tk.DISABLED, text="正在下载...")

        download_thread = threading.Thread(target=download_file_with_progress,
                                           args=(down, save_path, progress_bar, root, install_button))
        download_thread.start()


    def copy_to_clipboard(code):
        pyperclip.copy(code)
        messagebox.showinfo("复制成功", "代码已复制到剪切板")


    def create_interface(data):
        root = tk.Tk()
        root.title("动态 JSON 数据界面")

        # 获取屏幕尺寸
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # 设置窗口大小为屏幕的30%
        window_width = int(screen_width * 0.3)
        window_height = int(screen_height * 0.3)
        root.geometry(f"{window_width}x{window_height}")

        # 创建Canvas和Scrollbar
        canvas = tk.Canvas(root)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        row_counter = 0  # 用于动态排列控件

        for entry in data:
            name = entry.get("name", "No Title")
            txt = entry.get("txt", "No Description")
            code = entry.get("code", "")

            ttk.Label(scrollable_frame, text=f"标题: {name}").grid(row=row_counter, column=0, sticky=tk.W, pady=2)
            ttk.Label(scrollable_frame, text=f"描述: {txt}").grid(row=row_counter + 1, column=0, sticky=tk.W,
                                                                  pady=2)

            # 添加“复制代码”按钮
            copy_button = ttk.Button(scrollable_frame, text="复制代码", command=lambda c=code: copy_to_clipboard(c))
            copy_button.grid(row=row_counter + 2, column=0, pady=5)

            row_counter += 3  # 每个条目占用3行

        root.mainloop()

    fetch_from_url = True

    if fetch_from_url:
        url = downdata['check'][3]
        print(Fore.BLUE + "INFO:正在从云端拉取数据,请确保网络通畅....")
        data = fetch_data_from_url(url)
    else:
        local_file = "datacode.json"
        data = fetch_data_from_local(local_file)

    if data:
        create_interface(data)

elif choice == "8":
    print('输入对应功能的前面序号')
    print('=====')
    print(Fore.GREEN+'1. 【文件】清除临时下载文件\n'
          '3. 【设置】查看当前设置项\n'
          '2. 【设置】更改目录相关\n'
          '4. 【下载】重新检测下载线路\n'
          '5. 【下载】手动设置下载源')
    print('=====')
    xuanze = input("请输入选项数字: ")
    if xuanze == '1':
        print(Back.YELLOW + Fore.RED+'WARN:请注意,删除会将此目录所有文件删除,请确保目录下没有重要文件')
        print(Fore.BLUE + 'INFO:当前临时目录位置',filepath)
        xuanze = input("请输入y表示确认,其他键表示取消: ")
        if xuanze == 'y':
            delete_all_files_in_directory(filepath)
            print(Fore.BLUE + 'INFO:删除完毕')
    elif xuanze == '3':
        print('游戏目录',config['game_path'],'\n 下载临时文件存储目录',config['data_path'],'\n 下载源',config['Downloadsource'])
        print('输入1打开“游戏目录”,输入2打开“下载临时文件存储目录”,输入3打开全部.输入其它键退出')
        xuanze = input("请输入选项数字: ")
        if xuanze == '1':
            open_directory_in_explorer(config['game_path'])
        elif xuanze == '2':
            open_directory_in_explorer(config['data_path'])
        elif xuanze == '3':
            open_directory_in_explorer(config['game_path'])
            open_directory_in_explorer(config['data_path'])
    elif xuanze == '2':
        print('=====')
        print(Fore.GREEN + '1.更改游戏目录\n'
                           '2.更改下载文件存放目录')
        print('=====')
        xuanze = input("请输入选项数字: ")
        if xuanze == '1':
            game_path = select_directory(Fore.BLUE + "INFO:请选择游戏根目录")
            update_config_value('game_path', game_path)
        else:
            base_path = select_directory(Fore.BLUE + "INFO:请选择文件存放目录")
            update_config_value('data_path', base_path)
    elif xuanze == '4':
        print(Fore.BLUE + "INFO:正在检测最优线路,预计20秒,请耐心等待..")
        fastest = download_files(urls)
        if fastest:
            if fastest == 'https://mirror.ghproxy.com/https://github.com/yxsj245/Filespeedmeasurement/releases/download/main/test.txt':
                print(Fore.BLUE + 'INFO:当前最优线路：github中国代理,与此同时汉化相关组件采用gitee网络')
                update_config_value('Downloadsource', 'Mirrorghproxy')
            elif fastest == 'https://github.com/yxsj245/Filespeedmeasurement/releases/download/main/test.txt':
                print(Fore.BLUE + 'INFO:当前最优线路：github,与此同时汉化相关组件采用cloudlfare网络')
                update_config_value('Downloadsource', 'github')
            elif fastest == 'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/%E6%B5%8B%E9%80%9F%E6%96%87%E4%BB%B6/test.txt':
                print(Fore.BLUE + 'INFO:当前最优线路：cloudflare')
                update_config_value('Downloadsource', 'cloudflare')
            elif fastest == 'https://gitee.com/xiao-zhu245/filespeedmeasurement/releases/download/main/test.txt':
                print(Fore.BLUE + 'INFO:当前最优线路：gitee')
                update_config_value('Downloadsource', 'gitee')
    elif xuanze == '5':
        print('=====')
        print(Fore.GREEN+'gitee\t'
              'cloudflare\t'
              'Mirrorghproxy\t'
              'github\t'
              'other')
        print('=====')
        xuanze = input('请输入上方下载源')
        if xuanze == 'gitee':
            update_config_value('Downloadsource', 'gitee')
        elif xuanze == 'cloudflare':
            update_config_value('Downloadsource', 'cloudflare')
        elif xuanze == 'Mirrorghproxy':
            update_config_value('Downloadsource', 'Mirrorghproxy')
        elif xuanze == 'github':
            update_config_value('Downloadsource', 'github')
        elif xuanze == 'other':
            update_config_value('Downloadsource', 'other')
elif choice == "9":
    fileurl = down_5
    save_path = os.path.join(filepath, "VC_redist.x64.exe")
    download_file_with_progress(fileurl, save_path)
    exe_path = os.path.join(filepath, "VC_redist.x64.exe")
    subprocess.run(exe_path)
elif choice == "10":
    print('=====')
    print(Fore.GREEN + "4. 运行故障排除"
                       "1. TSM使用从萌新到大佬课程\n"
                       "2. 远程技术支持与1v1问题咨询\n"
                       "3. GitHub开源代码")
    print('=====')
    xuanze = input("请输入选项数字: ")
    if xuanze == '1':
        print(Style.BRIGHT + Fore.CYAN + "全套课程需要对本项目进行赞助才可以查看")
        print('=====')
        print(Fore.GREEN + "1. 前往试看1分钟\n"
                           "2. 前往赞助购买获得全套课程\n")
        print('=====')
        xuanze = input("请输入选项数字: ")
        if xuanze == '1':
            webbrowser.open('https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/%E6%88%91%E7%9A%84%E8%AF%BE%E7%A8%8B/TSM%E7%B3%BB%E5%88%97%E8%AF%BE%E7%A8%8B%E8%AF%95%E7%9C%8B/%E5%8D%8A%E8%87%AA%E5%8A%A8%E8%B7%91%E5%9B%BE%E8%B7%91%E6%B3%95(%E8%AF%95%E7%9C%8B).mp4')
        else:
            webbrowser.open("https://m.tb.cn/h.guakVCA?tk=3qGZ3kVUM9U")
    elif xuanze == '2':
        webbrowser.open("https://m.tb.cn/h.guakVCA?tk=3qGZ3kVUM9U")
    elif xuanze == '4':
        Troubleshooting(game_path)
    else:
        webbrowser.open("https://github.com/yxsj245/TSMpackagemanager")
else:
    print(Fore.RED+"ERROR:输入有误")

print(Back.YELLOW + "WARN:程序运行结束,按任意按键退出...")
input()
