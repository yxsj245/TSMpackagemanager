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

#——————方法库——————
# 初始化变量
url = 'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/data.json'
base_path = None  # 文件路径
game_path = None # 游戏路径
fileurl = None  #云端链接
filepath = None #临时存储文件路径

# 打开Windows资源管理器
def open_directory_in_explorer(directory_path):
    try:
        os.startfile(directory_path)
        print('启动成功')
    except Exception as e:
        print(f"无法打开目录 {directory_path}: {e}")
#更新json方法
def update_config_value(key, value, file_path="config.json"):
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
# 加载json文件
def load_config(file_path="config.json"):
    """
    读取 JSON 配置文件的内容。如果文件不存在，则返回 None。
    """
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return None

# 创建json文件
def create_default_config(file_path="config.json", default_config=None):
    """
    创建一个默认的 JSON 配置文件，如果文件不存在。
    可以传递一个默认配置的字典，如果没有提供，则使用预定义的默认配置。
    """
    if default_config is None:
        default_config = {
            "first": True,
            "game_path": None,
            "data_path": None
        }

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
        print("ERROR:注册表项或数值名称不存在。")
    except Exception as e:
        print(f"ERROR:读取注册表时发生错误: {e}")
    return None


# 解压文件的方法
def unzip_file(zip_path, extract_to):
    # 检查文件是否为zip格式
    if zipfile.is_zipfile(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 解压缩所有文件到目标目录
            zip_ref.extractall(extract_to)
    else:
        print("ERROR:指定的文件不是有效的ZIP文件")

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
            print(f"WARN:文件信息校验码不匹配: {file_path}")
            print("提示：可能是您下载了错误的版本或者下载过程中文件出现损坏。请重新下载上行路径输出的末尾的文件替换到此目录。如果是新版本更新可能没有及时更新云端文件信息所致，您可以按任意键跳过，但是这将可能导致TSM不在预期内运行。")
            input()
            return True
    except FileNotFoundError:
        print(f"ERROR:文件缺失: {file_path}")
        print("提示：在最新版本中，此错误不应当出现，请联系作者排查。")
        input()
        sys.exit(1)  # 终止程序运行并返回状态码1

def fetch_json_from_url(url):
    try:
        response = requests.get(url, timeout=30)  # 设置超时时间为10秒
        response.raise_for_status()  # 如果请求失败则抛出HTTPError异常
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR:从云端拉取文件信息失败: {e}")
        print("WARN:跳过鉴权文件信息，无法保证文件完整，这可能会导致TSM不在预期内运行。")
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
        print("ERROR:没有选择目录")
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
        # 发送 HTTP GET 请求获取文件信息
        response = requests.get(url, stream=True, allow_redirects=True)
        response.raise_for_status()  # 检查请求是否成功

        # 检查内容类型，确保下载的是 ZIP 文件而不是 HTML 等其他内容
        content_type = response.headers.get('Content-Type')
        if 'text/html' in content_type:
            print("ERROR:请求返回了HTML内容，可能URL无效或需要权限。")
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

        print(f"INFO:文件已下载到临时存储目录")
    except requests.exceptions.RequestException as e:
        print(f"ERROR:下载文件时出错: {e}")

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
                print(f"INFO:已删除文件: {file_path}")
            else:
                print(f"ERROR:文件未找到: {file_path}")
        except Exception as e:
            print(f"ERROR:删除文件时出错: {file_path}, 错误: {e}")

    # 删除目录
    for dir_name in directories_to_delete:
        dir_path = os.path.join(target_directory, dir_name)
        try:
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)
                print(f"INFO:已删除目录: {dir_path}")
            else:
                print(f"ERROR:目录未找到: {dir_path}")
        except Exception as e:
            print(f"ERROR:删除目录时出错: {dir_path}, 错误: {e}")
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

#——————程序运行入口——————
# 环境初始化
config = load_config()
if config is None:
    create_default_config()
    config = load_config()
    print("INFO:首次运行创建配置文件")
if load_config()['first']:
    print("INFO:执行初始化设置向导")
    print("INFO:设置游戏目录(1/2)")
    game_path=get_game_install_location()
    print("INFO:您的游戏安装目录为：",game_path,'\n 是否正确,如果不正确输入n进行手动选择游戏目录,反则按任意键继续...')
    xuanze = input()
    if xuanze == 'n':
        game_path=None
    if game_path == None:
        print("WARN:获取游戏路径失败，需要手动选择")
        game_path= select_directory("INFO:请选择游戏根目录")
    update_config_value('game_path', game_path)
    print("INFO:设置下载的临时文件存储位置(2/2)")
    filepath=os.getcwd()
    print("提示：默认为运行目录,当前目录为:",filepath,"\n 如果需要进行更改请输入n,反则输入任意键继续...")
    if input() == 'n':
        filepath = select_directory("INFO:请选择临时文件存储目录")
    update_config_value('data_path', filepath)
    print('INFO:设置向导完毕。如有设置错误可以在菜单种重新设置')
    update_config_value('first', False)
# 设置变量值
print('INFO:程序初始化')
jsondata = load_config()
filepath = jsondata['data_path']
game_path = jsondata['game_path']
base_path = filepath
print("请选择功能(输入序号)")
print("1.【一键】一键安装TSM")
print("2.【一键】从本地文件安装TSM")
print("4.【手动】从github下载安装最新版TSM核心组件/更新TSM")
print("5.【手动】安装汉化组件/更新")
print("3.【一键】一键卸载TSM")
print("6.【社区】安装社区插件功能")
print("7.【社区】复制社区提供的运行代码")
print("8.【程序】设置")
choice = input("请输入选项数字: ")
if choice == "1":
    print("INFO:开始下载文件")
    # 下载TSM.zip
    fileurl = "https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/TSM.zip"
    save_path = os.path.join(filepath, "TSM.zip")
    download_file_with_progress(fileurl, save_path)
    # 下载sml-pc.zip
    fileurl = "https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/sml-pc.zip"
    save_path = os.path.join(filepath, "sml-pc.zip")
    download_file_with_progress(fileurl, save_path)
    # 下载TSM_font.zip
    fileurl = "https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/TSM_font.zip"
    save_path = os.path.join(filepath, "TSM_font.zip")
    download_file_with_progress(fileurl, save_path)
    # 下载TSMmap-ZH_CN.zip
    fileurl = "https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/TSMmap-ZH_CN.zip"
    save_path = os.path.join(filepath, "TSMmap-ZH_CN.zip")
    download_file_with_progress(fileurl, save_path)
    print("INFO:开始校验文件信息")
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
                print("ERROR:JSON数据中缺少文件名或MD5值，跳过该项。")
    print("INFO:文件信息校验完毕。")

    print("INFO:开始解压文件")
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
    print("INFO:解压完毕，请在steam中启动游戏，如果启动后崩溃请双击运行外挂目录下VC进行安装运行环境")
    input()
elif choice == "2":
    print('WARN:本地安装将不在进行文件校验，无法保证文件完好无损以及是否为官方版本，请自行斟酌！')
    print("INFO:请选择外挂文件下载的目录")
    base_path=select_directory("请选择外挂文件下载的目录")
    print("INFO:开始解压文件")
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
    print("INFO:解压完毕，请在steam中启动游戏，如果启动后崩溃请双击运行外挂目录下VC进行安装运行环境")
    input()
elif choice == "3":
    delete_files_and_directories(game_path)
    print("INFO:卸载完毕")
elif choice == "4":
    print("INFO:将通过代理地址加速访问github，您的下载速度会得到很大提升，但可能存在失效和下载失败概率")
    print("WARN:由于官方不提供校验码。下载后的文件不会进行文件鉴权，可能存在下载后文件损坏风险。")
    # 下载TSM.zip
    fileurl = "https://mirror.ghproxy.com/https://github.com/XeTrinityz/ThatSkyMod/releases/latest/download/TSM.zip"
    save_path = os.path.join(filepath, "TSM.zip")
    download_file_with_progress(fileurl, save_path)
    # 下载sml-pc.zip
    fileurl = "https://mirror.ghproxy.com/https://github.com/lukas0x1/sml-pc/releases/latest/download/sml-pc.zip"
    save_path = os.path.join(filepath, "sml-pc.zip")
    download_file_with_progress(fileurl, save_path)
    print("INFO:文件下载完毕")
    print("INFO:开始解压文件")
    # 解压sml-pc.zip
    file_name = 'sml-pc.zip'  # 替换为你的文件名
    full_path = create_full_path(base_path, file_name)
    unzip_file(create_full_path(base_path, file_name), game_path)
    # 解压TSM.zip
    file_name = 'TSM.zip'  # 替换为你的文件名
    full_path = create_full_path(base_path, file_name)
    game_path_mod = game_path + '/mods'
    unzip_file(create_full_path(base_path, file_name), game_path_mod)
    print("INFO:解压完毕")
    print("默认没有中文，如有需要请重新运行脚本选择下载汉化。")
    input()
elif choice == "5":
    print("INFO:开始下载")
    # 下载TSM_font.zip
    fileurl = "https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/TSM_font.zip"
    save_path = os.path.join(filepath, "TSM_font.zip")
    download_file_with_progress(fileurl, save_path)
    # 下载TSMmap-ZH_CN.zip
    fileurl = "https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/TSMmap-ZH_CN.zip"
    save_path = os.path.join(filepath, "TSMmap-ZH_CN.zip")
    download_file_with_progress(fileurl, save_path)
    print("INFO:文件下载完毕")
    print("INFO:开始校验文件信息")
    # 获取JSON数据
    url ='https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/data_hanhua.json'
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
                print("ERROR:JSON数据中缺少文件名或MD5值，跳过该项。")
    print("INFO:文件信息校验完毕。")
    print("INFO:开始解压文件")
    # 解压TSM_font.zip
    file_name = 'TSM_font.zip'  # 替换为你的文件名
    full_path = create_full_path(base_path, file_name)
    unzip_file(create_full_path(base_path, file_name),game_path)
    # 解压TSMmap-ZH_CN.zip
    file_name = 'TSMmap-ZH_CN.zip'  # 替换为你的文件名
    full_path = create_full_path(base_path, file_name)
    unzip_file(create_full_path(base_path, file_name),game_path)
    print("INFO:解压完毕，请在steam中启动游戏，如果启动后崩溃请双击运行外挂目录下VC进行安装运行环境")
    input()

elif choice == "6":

    print("WARN:当前使用的是社区功能,请注意这些脚本以及信息来源于全球玩家贡献，无法确保安全和稳定性，请自行斟酌！")
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
            url = "https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/%E7%A4%BE%E5%8C%BA%E8%B5%84%E6%BA%90/datadc.json"
            print("INFO:加载窗体控件，如果没有正常显示，请查看通知栏。")
            print("INFO:正在从云端拉取数据,请确保网络通畅....")
            data = fetch_data_from_url(url)
        else:
            local_file = "datadc.json"
            data = fetch_data_from_local(local_file)

        if data:
            create_interface(data)


    if __name__ == "__main__":
        main()

elif choice == "7":
    print("INFO:加载窗体控件，如果没有正常显示，请查看通知栏。")
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
        url = "https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/%E7%A4%BE%E5%8C%BA%E8%B5%84%E6%BA%90/datacode.json"
        print("INFO:正在从云端拉取数据,请确保网络通畅....")
        data = fetch_data_from_url(url)
    else:
        local_file = "datacode.json"
        data = fetch_data_from_local(local_file)

    if data:
        create_interface(data)

elif choice == "8":
    print('输入对应功能的前面序号')
    print('1. 清除临时下载文件')
    print('3. 查看当前设置项')
    print('2. 重新设置目录相关')
    xuanze = input()
    if xuanze == '1':
        delete_all_files_in_directory(filepath)
        print('删除完毕')
    elif xuanze == '3':
        print('游戏目录',config['game_path'],'\n 下载临时文件存储目录',config['data_path'])
        print('输入1打开“游戏目录”,输入2打开“下载临时文件存储目录”,输入3打开全部.输入其它键退出')
        xuanze = input()
        if xuanze == '1':
            open_directory_in_explorer(config['game_path'])
        elif xuanze == '2':
            open_directory_in_explorer(config['data_path'])
        elif xuanze == '3':
            open_directory_in_explorer(config['game_path'])
            open_directory_in_explorer(config['data_path'])
    elif xuanze == '2':
        update_config_value('first', True)
        print('重启程序进入设置向导')
else:
    print("ERROR:输入有误")

print("WARN:程序运行结束,按任意按键退出...")
input()
