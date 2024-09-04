import zipfile
import os
import hashlib
import requests
import sys
import tkinter as tk
from tkinter import filedialog
import winreg
from tqdm import tqdm
import shutil

# 初始化变量
url = 'https://pub-46d21cac9c7d44b79d73abfeb727999f.r2.dev/TSM%E5%AE%89%E8%A3%85%E5%99%A8/data.json'
base_path = "./"  # 文件路径
game_path = None # 游戏路径
fileurl = None

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


# ------解压文件的方法------
def unzip_file(zip_path, extract_to):
    # 检查文件是否为zip格式
    if zipfile.is_zipfile(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 解压缩所有文件到目标目录
            zip_ref.extractall(extract_to)
    else:
        print("ERROR:指定的文件不是有效的ZIP文件")

#------校验MD5方法------
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
            print(f"WARN:文件信息鉴权失败: {file_path}")
            print("INFO:可能是您下载了错误的版本或者下载过程中文件出现损坏。请重新下载上行路径输出的末尾的文件替换到此目录。如果是新版本更新可能没有及时更新云端文件信息所致，您可以按任意键跳过，但是这将可能导致TSM不在预期内运行。")
            input()
            return True
    except FileNotFoundError:
        print(f"WARN:文件缺失: {file_path}")
        print("INFO:请下载上行路径输出的末尾的文件到此目录")
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

        print(f"INFO:文件已下载并保存到: {save_path}")
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


game_path=get_game_install_location()
if game_path == None:
    print("WARN:获取游戏路径失败，需要手动选择")
    game_path= select_directory("INFO:请选择游戏根目录")
print("请选择功能(输入序号)")
print("1.【一键】一键安装TSM")
print("2.【一键】从本地文件安装TSM")
print("4.【手动】从github下载安装最新版TSM核心组件/更新TSM")
print("5.【手动】安装汉化组件/更新")
print("3.【一键】一键卸载TSM")
choice = input("请输入选项数字: ")
if choice == "1":
    print("INFO:开始下载文件")
    # 下载TSM.zip
    fileurl = "https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/TSM.zip"
    save_path = os.path.join(os.getcwd(), "TSM.zip")
    download_file_with_progress(fileurl, save_path)
    # 下载sml-pc.zip
    fileurl = "https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/sml-pc.zip"
    save_path = os.path.join(os.getcwd(), "sml-pc.zip")
    download_file_with_progress(fileurl, save_path)
    # 下载TSM_font.zip
    fileurl = "https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/TSM_font.zip"
    save_path = os.path.join(os.getcwd(), "TSM_font.zip")
    download_file_with_progress(fileurl, save_path)
    # 下载TSMmap-ZH_CN.zip
    fileurl = "https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/TSMmap-ZH_CN.zip"
    save_path = os.path.join(os.getcwd(), "TSMmap-ZH_CN.zip")
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
    # 其他后续代码（如果文件缺失或MD5不匹配，此处代码不会执行）
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
    print("INFO:请选择外挂文件下载的目录")
    base_path=select_directory("请选择外挂文件下载的目录")
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
    # 其他后续代码（如果文件缺失或MD5不匹配，此处代码不会执行）
    print("INFO:文件信息校验完毕。")

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
    save_path = os.path.join(os.getcwd(), "TSM.zip")
    download_file_with_progress(fileurl, save_path)
    # 下载sml-pc.zip
    fileurl = "https://mirror.ghproxy.com/https://github.com/lukas0x1/sml-pc/releases/latest/download/sml-pc.zip"
    save_path = os.path.join(os.getcwd(), "sml-pc.zip")
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
    save_path = os.path.join(os.getcwd(), "TSM_font.zip")
    download_file_with_progress(fileurl, save_path)
    # 下载TSMmap-ZH_CN.zip
    fileurl = "https://gitee.com/xiao-zhu245/TSMinstall/releases/download/TSM/TSMmap-ZH_CN.zip"
    save_path = os.path.join(os.getcwd(), "TSMmap-ZH_CN.zip")
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
    # 其他后续代码（如果文件缺失或MD5不匹配，此处代码不会执行）
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
else:
    print("ERROR:输入有误")

print("INFO:按任意按键退出...")
input()
