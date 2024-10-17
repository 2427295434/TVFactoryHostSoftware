import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import *
from tkinter.ttk import *
import serial
import threading
import time
from datetime import datetime
import serial.tools.list_ports
import configparser
import os

# 配置日志文件
log_dir = './log'
config_dir = './config'
def get_log_filename():
    """生成带有当前日期的日志文件名"""
    current_date = datetime.now().strftime("%Y%m%d")
    return f"{log_dir}/log_{current_date}.txt"

log_file = get_log_filename()

# 创建日志/配置目录
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
if not os.path.exists(config_dir):
    os.makedirs(config_dir)   

# 配置信息
testconfig_file = './config/Testconfig.ini'
#初始化配置
def init_test_config():
    if not os.path.exists(testconfig_file):
        open(testconfig_file, 'w')
    config = configparser.ConfigParser()
    config.read(testconfig_file)
    if 'DEFAULT' not in config:
        config['DEFAULT'] = {}
    # 检查每个配置项是否存在于 [DEFAULT] 部分，如果不存在则设置默认值
    check_config_items = {
        'workorder_entry':'',
        'IP_entry':'',
        'port_entry':'',
        'ULPKlimit_min_entry':'',
        'ULPKlimit_max_entry':'',
        'FWver_entry':'',
        'modelindex_entry':'',
        'check_key_to_mes_checkbutton':'True',
        'burnkey_module_button':'启用',

        'Burnkey_checkbutton':'True',
        'WB_checkbutton':'True',
        'HDMI1_checkbutton':'True',
        'HDMI2_checkbutton':'True',
        'HDMI3_checkbutton':'True',
        'DTV_checkbutton':'True',
        'USB_checkbutton':'True',
        'KEYPAD_checkbutton':'True',
        'IR_checkbutton':'True',
        'DEMO_checkbutton':'True',
        'check_module_button':'启用',
        
        'WIFI1_checkbutton':'True',
        'WIFI1_min_entry':'-70',
        'WIFI1_max_entry':'0',
        'WIFI2_checkbutton':'True',
        'WIFI2_min_entry':'-70',
        'WIFI2_max_entry':'0',
        'BT_checkbutton':'True',
        'BT_min_entry':'-80',
        'BT_max_entry':'0',
        'checkRSSI_module_button':'启用',

        'reset_checkbutton':'True',
        'reset_module_button':'启用',

        'reset_mes_checkbutton':'True',
        'reset_mes_module_button':'启用',

    }
    for item, status, in check_config_items.items():
        if item not in config['DEFAULT']:
            config.set('DEFAULT', item, status)
    with open(testconfig_file, 'w') as configfile:
        config.write(configfile)
def read_testconfig():
    config = configparser.ConfigParser()
    config.read(testconfig_file)
    return config

# 保存配置文件
def save_config():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {

        'workorder_entry':workorder_entry.get(),
        'IP_entry':IP_entry.get(),
        'port_entry':port_entry.get(),
        'ULPKlimit_min_entry':ULPKlimit_min_entry.get(),
        'ULPKlimit_max_entry':ULPKlimit_max_entry.get(),
        'FWver_entry':FWver_entry.get(),
        'modelindex_entry':modelindex_entry.get(),
        'check_key_to_mes_checkbutton':str(fulltest_check_key_to_mes.get()),
        'burnkey_module_button':burnkey_module_button_text.get(),

        'Burnkey_checkbutton':str(fulltest_Burnkey_check.get()),
        'WB_checkbutton':str(fulltest_WB.get()),
        'HDMI1_checkbutton':str(fulltest_HDMI1.get()),
        'HDMI2_checkbutton':str(fulltest_HDMI2.get()),
        'HDMI3_checkbutton':str(fulltest_HDMI3.get()),
        'DTV_checkbutton':str(fulltest_DTV.get()),
        'USB_checkbutton':str(fulltest_USB.get()),
        'KEYPAD_checkbutton':str(fulltest_KEYPAD.get()),
        'IR_checkbutton':str(fulltest_IR.get()),
        'DEMO_checkbutton':str(fulltest_DEMO.get()),
        'check_module_button':check_module_button_text.get(),

        'WIFI1_checkbutton':str(fulltest_WIFI1_check.get()),
        'WIFI1_min_entry':WIFI1_min_entry.get(),
        'WIFI1_max_entry':WIFI1_max_entry.get(),
        'WIFI2_checkbutton':str(fulltest_WIFI2_check.get()),
        'WIFI2_min_entry':WIFI2_min_entry.get(),
        'WIFI2_max_entry':WIFI2_max_entry.get(),
        'BT_checkbutton':str(fulltest_BT_check.get()),
        'BT_min_entry':BT_min_entry.get(),
        'BT_max_entry':BT_max_entry.get(),
        'checkRSSI_module_button':checkRSSI_module_button_text.get(),

        'reset_checkbutton':str(fulltest_reset_check.get()),
        'reset_module_button':reset_module_button_text.get(),

        'reset_mes_checkbutton':str(fulltest_reset_mes_check.get()),
        'reset_mes_module_button':reset_mes_module_button_text.get(),
    }
    with open(testconfig_file, 'w') as configfile:
        config.write(configfile)


# 串口配置
port_name = 'COM4'  # 根据实际情况修改
baud_rate = 115200
timeout = 0.1

# 发送的数据
send_source_HDMI1 = bytes([0xF1, 0x01, 0x01, 0x07, 0x00, 0xF6, 0xF2])
send_get_portstate = bytes([0xF1, 0x01, 0x01, 0x07, 0x00, 0xF6, 0xF2])

# 初始化串口
ser = None

def log(message):
    """记录消息到日志文件并打印到控制台"""
    with open(log_file, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} - {message}\n")
    print(message)  # 打印到控制台，便于调试

def open_serial():
    """打开指定的串口"""
    global ser
    try:
        ser = serial.Serial(port=port_name, baudrate=baud_rate, timeout=timeout)
        log("串口已连接")
        update_setting_status("串口已连接", connected=True)
        return True
    except Exception as e:
        log(f"无法打开串口: {e}")
        update_setting_status("串口未连接", connected=False)
        return False

def close_serial():
    """关闭串口"""
    global ser
    if ser and ser.is_open:
        ser.close()
        log("串口已关闭")
        update_setting_status("串口未连接", connected=False)

def send_data(command, data):
    """通过串口发送数据并读取响应"""
    if ser and ser.is_open:
        ser.write(data)
        # 将数据转换为大写，并在每两个字符之间插入空格
        formatted_data = ' '.join([data.hex()[i:i+2].upper() for i in range(0, len(data.hex()), 2)])
        log(f"[Send] {formatted_data}")
        read_response(command)
    else:
        log("串口未连接，请先连接串口")
        tk.messagebox.showerror("Error", "串口未连接，请先连接串口")

def read_response(command):
    """从串口读取响应数据"""
    if ser and ser.is_open:
        response = ser.read(8)  # 假设响应长度为8字节
        formatted_response = ' '.join([response.hex()[i:i+2].upper() for i in range(0, len(response.hex()), 2)])
        log(f"[Recd] {formatted_response}")


def on_closing():
    """处理窗口关闭事件，关闭串口并退出程序"""
    close_serial()
    root.destroy()

def connect_serial():
    """连接串口"""
    global port_name, baud_rate, timeout
    port_name = port_var.get()
    baud_rate = int(baud_rate_entry.get())
    timeout = float(timeout_entry.get())
    if not open_serial():
        log("串口打开失败")
        update_setting_status("串口打开失败", connected=False)

def disconnect_serial():
    """断开串口连接"""
    close_serial()
    log("串口断开连接.")
    update_setting_status("串口未连接", connected=False)

def update_port_list():
    """更新串口列表"""
    ports = [port.device for port in serial.tools.list_ports.comports()]
    if ports:
        port_combobox['values'] = ports
        if port_combobox.current() == -1:
            port_combobox.current(0)
    else:
        port_combobox.set('')
        port_combobox['values'] = []

def update_setting_status(message, connected=False):
    """更新状态文本框的内容"""
    status_label.config(text=message, fg="white", font=("微软雅黑", 16 ,"bold"), anchor=tk.CENTER)
    
    # 根据连接状态设置背景颜色
    if connected:
        status_label.config(bg="green")
    else:
        status_label.config(bg="red")

################################################################################
# 整机测试
def enable_fulltest_Module(status_text):
    if status_text.get() == "启用":
        status_text.set("停用")
    else:
        status_text.set("启用")

def change_value_confirm_pasword():
    password = simpledialog.askstring("修改参数", "请输入密码:", show='*')
    if password == "hkc":
        fulltest_tab1_button_start.config(state=tk.DISABLED)
        fulltest_tab1_button_changevalue.config(state=tk.DISABLED)
        fulltest_tab1_button_confirmchange.config(state=tk.NORMAL)
        
        workorder_entry.config(state=tk.NORMAL)
        IP_entry.config(state=tk.NORMAL)
        port_entry.config(state=tk.NORMAL)
        ULPKlimit_min_entry.config(state=tk.NORMAL)
        ULPKlimit_max_entry.config(state=tk.NORMAL)
        FWver_entry.config(state=tk.NORMAL)
        modelindex_entry.config(state=tk.NORMAL)
        check_key_to_mes_checkbutton.config(state=tk.NORMAL)
        burnkey_module_button.config(state=tk.NORMAL)

        Burnkey_checkbutton.config(state=tk.NORMAL)
        WB_checkbutton.config(state=tk.NORMAL)
        HDMI1_checkbutton.config(state=tk.NORMAL)
        HDMI2_checkbutton.config(state=tk.NORMAL)
        HDMI3_checkbutton.config(state=tk.NORMAL)
        DTV_checkbutton.config(state=tk.NORMAL)
        USB_checkbutton.config(state=tk.NORMAL)
        KEYPAD_checkbutton.config(state=tk.NORMAL)
        IR_checkbutton.config(state=tk.NORMAL)
        DEMO_checkbutton.config(state=tk.NORMAL)
        check_module_button.config(state=tk.NORMAL)

        WIFI1_checkbutton.config(state=tk.NORMAL)
        WIFI1_min_entry.config(state=tk.NORMAL)
        WIFI1_max_entry.config(state=tk.NORMAL)
        WIFI2_checkbutton.config(state=tk.NORMAL)
        WIFI2_min_entry.config(state=tk.NORMAL)
        WIFI2_max_entry.config(state=tk.NORMAL)
        BT_checkbutton.config(state=tk.NORMAL)
        BT_min_entry.config(state=tk.NORMAL)
        BT_max_entry.config(state=tk.NORMAL)
        checkRSSI_module_button.config(state=tk.NORMAL)

        reset_checkbutton.config(state=tk.NORMAL)
        reset_module_button.config(state=tk.NORMAL)
        reset_mes_checkbutton.config(state=tk.NORMAL)
        reset_mes_module_button.config(state=tk.NORMAL)
        
    else:
        tk.messagebox.showerror("错误", "密码错误")

def change_value_confirm():

    save_config()

    fulltest_tab1_button_start.config(state=tk.NORMAL)
    fulltest_tab1_button_changevalue.config(state=tk.NORMAL)
    fulltest_tab1_button_confirmchange.config(state=tk.DISABLED)
    
    workorder_entry.config(state=tk.DISABLED)
    IP_entry.config(state=tk.DISABLED)
    port_entry.config(state=tk.DISABLED)
    ULPKlimit_min_entry.config(state=tk.DISABLED)
    ULPKlimit_max_entry.config(state=tk.DISABLED)
    FWver_entry.config(state=tk.DISABLED)
    modelindex_entry.config(state=tk.DISABLED)
    check_key_to_mes_checkbutton.config(state=tk.DISABLED)
    burnkey_module_button.config(state=tk.DISABLED)

    Burnkey_checkbutton.config(state=tk.DISABLED)
    WB_checkbutton.config(state=tk.DISABLED)
    HDMI1_checkbutton.config(state=tk.DISABLED)
    HDMI2_checkbutton.config(state=tk.DISABLED)
    HDMI3_checkbutton.config(state=tk.DISABLED)
    DTV_checkbutton.config(state=tk.DISABLED)
    USB_checkbutton.config(state=tk.DISABLED)
    KEYPAD_checkbutton.config(state=tk.DISABLED)
    IR_checkbutton.config(state=tk.DISABLED)
    DEMO_checkbutton.config(state=tk.DISABLED)
    check_module_button.config(state=tk.DISABLED)

    WIFI1_checkbutton.config(state=tk.DISABLED)
    WIFI1_min_entry.config(state=tk.DISABLED)
    WIFI1_max_entry.config(state=tk.DISABLED)
    WIFI2_checkbutton.config(state=tk.DISABLED)
    WIFI2_min_entry.config(state=tk.DISABLED)
    WIFI2_max_entry.config(state=tk.DISABLED)
    BT_checkbutton.config(state=tk.DISABLED)
    BT_min_entry.config(state=tk.DISABLED)
    BT_max_entry.config(state=tk.DISABLED)
    checkRSSI_module_button.config(state=tk.DISABLED)

    reset_checkbutton.config(state=tk.DISABLED)
    reset_module_button.config(state=tk.DISABLED)
    reset_mes_checkbutton.config(state=tk.DISABLED)
    reset_mes_module_button.config(state=tk.DISABLED)
    
################################################################################
# 创建主窗口
root = tk.Tk()
root.title("TV Factory Mode Utility")
root.geometry("1600x900")  # 设置窗口初始大小
root.protocol("WM_DELETE_WINDOW", on_closing)

# 创建 Notebook（选项卡容器）
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

################################################################################
# 创建 TEST 选项卡
test_frame = ttk.Frame(notebook)
notebook.add(test_frame, text="TEST")

# 定义更多命令和数据
commands = {
    "Send Source: HDMI 1": send_source_HDMI1,
    "Burn Key": send_get_portstate,
    "Send Command 3": bytes([0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10])
}

# 添加按钮到 TEST 选项卡
for command, data in commands.items():
    button = tk.Button(test_frame, text=command, command=lambda c=command, d=data: send_data(c, d))
    button.pack(pady=5)

################################################################################
################################################################################
#整机测试 选项卡
fulltest_frame = ttk.Frame(notebook)
notebook.add(fulltest_frame, text="整机测试")


#SN输入框——SN
fulltest_tab1_frame = ttk.Frame(fulltest_frame, padding=10, relief=tk.SOLID, borderwidth=2)
fulltest_tab1_frame.pack(fill=tk.BOTH, expand=False, pady=10)
ttk.Label(fulltest_tab1_frame, text="SN:", font=("宋体", 20 ,"bold")).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W+tk.S+tk.N)
#SN输入框——输入框
fulltest_SN = tk.StringVar()
SN_entry = ttk.Entry(fulltest_tab1_frame, textvariable=fulltest_SN, width=50, font=("宋体", 25 ,"bold"))
SN_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.S+tk.N)
#SN输入框——确认
fulltest_tab1_button_start = tk.Button(fulltest_tab1_frame, text="开始", width = 10, font=("宋体", 20 ,"bold"))
fulltest_tab1_button_start.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W+tk.E)
#SN输入框——修改参数
fulltest_tab1_button_changevalue = tk.Button(fulltest_tab1_frame, text="修改参数", width = 10, font=("宋体", 20 ,"bold"), command = lambda: change_value_confirm_pasword())
fulltest_tab1_button_changevalue.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W+tk.E)
#SN输入框——确认修改
fulltest_tab1_button_confirmchange = tk.Button(fulltest_tab1_frame, text="确认修改", width = 10, font=("宋体", 20 ,"bold"),command = lambda:change_value_confirm(),state = DISABLED)
fulltest_tab1_button_confirmchange.grid(row=0, column=4, sticky=tk.W+tk.E)

#烧key
fulltest_tab2_frame = ttk.Frame(fulltest_frame, padding=10, relief=tk.SOLID, borderwidth=2, width = 400, height = 450)
fulltest_tab2_frame.place(x=0, y=100)
ttk.Label(fulltest_tab2_frame, text="烧录KEY", font=("宋体", 10 ,"bold")).place(x=0, y=0)
#烧key——工单
ttk.Label(fulltest_tab2_frame, text="工单号", width = 10, font=("宋体", 13 ,"bold")).place(x=5, y=20)
fulltest_workorder = tk.StringVar() ##需要修改为读文件的值
workorder_entry = ttk.Entry(fulltest_tab2_frame, textvariable=fulltest_workorder, width=25, font=("宋体", 15 ,"bold"), state = DISABLED)
workorder_entry.place(x=85,y=20)
#烧key——IP
ttk.Label(fulltest_tab2_frame, text="MES IP", width = 10, font=("宋体", 13 ,"bold")).place(x=5, y=50)
fulltest_IP = tk.StringVar()        ##需要修改为读文件的值
IP_entry = ttk.Entry(fulltest_tab2_frame, textvariable=fulltest_IP, width=15, font=("宋体", 15 ,"bold"), state=DISABLED)
IP_entry.place(x=85,y=50)
ttk.Label(fulltest_tab2_frame, text="端口", width = 6, font=("宋体", 13 ,"bold")).place(x=255, y=50)
fulltest_port = tk.StringVar()      ##需要修改为读文件的值
port_entry = ttk.Entry(fulltest_tab2_frame, textvariable=fulltest_port, width = 5, font=("宋体", 15 ,"bold"), state=DISABLED)
port_entry.place(x=300,y=50)
#烧key——uid范围
ttk.Label(fulltest_tab2_frame, text="UID范围", width = 10, font=("宋体", 13 ,"bold")).place(x=5, y=80)
fulltest_ULPKlimit_min = tk.StringVar()   #下限，需要修改为读文件的值
ULPKlimit_min_entry = ttk.Entry(fulltest_tab2_frame, textvariable=fulltest_ULPKlimit_min, width=10, font=("宋体", 15 ,"bold"), state=DISABLED)
ULPKlimit_min_entry.place(x=85,y=80)
ttk.Label(fulltest_tab2_frame, text="-", font=("宋体", 13 ,"bold")).place(x=220, y=80)
fulltest_ULPKlimit_max = tk.StringVar()   #上限，需要修改为读文件的值
ULPKlimit_max_entry = ttk.Entry(fulltest_tab2_frame, textvariable=fulltest_ULPKlimit_max, width = 10, font=("宋体", 15 ,"bold"), state=DISABLED)
ULPKlimit_max_entry.place(x=250,y=80)
#烧key——软件版本
ttk.Label(fulltest_tab2_frame, text="软件版本", width = 10, font=("宋体", 13 ,"bold")).place(x=5, y=110)
fulltest_FWver = tk.StringVar()     ##需要修改为读文件的值
FWver_entry = ttk.Entry(fulltest_tab2_frame, textvariable=fulltest_FWver, width=25, font=("宋体", 15 ,"bold"), state=DISABLED)
FWver_entry.place(x=85,y=110)
#烧key——model index
ttk.Label(fulltest_tab2_frame, text="Index", width = 10, font=("宋体", 13 ,"bold")).place(x=5, y=140)
fulltest_modelindex = tk.StringVar()     ##需要修改为读文件的值
modelindex_entry = ttk.Entry(fulltest_tab2_frame, textvariable=fulltest_modelindex, width=25, font=("宋体", 15 ,"bold"), state=DISABLED)
modelindex_entry.place(x=85,y=140)
#烧key——check——SN
ttk.Label(fulltest_tab2_frame, text="SN", width = 10, font=("宋体", 20 ,"bold")).place(x=25, y=190)
default_check_color = ttk.Style()
default_check_color.configure('stylegray.TLabel', background='#BFBFBF')
Status_SN = ttk.Label(fulltest_tab2_frame, style='stylegray.TLabel',width = 10, font=("宋体", 20 ,"bold")).place(x=200,y=190)
#烧key——check——ULPK
ttk.Label(fulltest_tab2_frame, text="ULPK", width = 10, font=("宋体", 20 ,"bold")).place(x=25, y=240)
Status_ULPK = ttk.Label(fulltest_tab2_frame, style='stylegray.TLabel',width = 10, font=("宋体", 20 ,"bold")).place(x=200,y=240)
#烧key——check——POTK
ttk.Label(fulltest_tab2_frame, text="POTK", width = 10, font=("宋体", 20 ,"bold")).place(x=25, y=290)
Status_POTK = ttk.Label(fulltest_tab2_frame, style='stylegray.TLabel',width = 10, font=("宋体", 20 ,"bold")).place(x=200,y=290)
#烧key——check——MES
fulltest_check_key_to_mes = tk.BooleanVar(value=True)   ##需要修改为读文件的值
check_key_to_mes_checkbutton = ttk.Checkbutton(fulltest_tab2_frame, variable=fulltest_check_key_to_mes, state=DISABLED)
check_key_to_mes_checkbutton.place(x=0, y=345)
ttk.Label(fulltest_tab2_frame, text="上传MES", width = 10, font=("宋体", 20 ,"bold")).place(x=25, y=340)
Status_key_to_mes = ttk.Label(fulltest_tab2_frame, style='stylegray.TLabel',width = 10, font=("宋体", 20 ,"bold")).place(x=200,y=340)
#烧key——启用/停用
burnkey_module_button_text = tk.StringVar(value="启用")
burnkey_module_button = tk.Button(fulltest_tab2_frame, textvariable=burnkey_module_button_text, width = 6, font=("宋体", 15 ,"bold"), command = lambda: enable_fulltest_Module(burnkey_module_button_text), state=DISABLED)       #待补充command参数
burnkey_module_button.place(x=200, y=390)
#烧key——测试
burnkey_test_button = tk.Button(fulltest_tab2_frame, text="测试", width = 6, font=("宋体", 15 ,"bold"))       #待补充command参数
burnkey_test_button.place(x=280, y=390)

#防呆复位模块1
fulltest_tab3_frame = ttk.Frame(fulltest_frame, padding=10, relief=tk.SOLID, borderwidth=2, width = 650, height = 450)
fulltest_tab3_frame.place(x=420, y=100)
ttk.Label(fulltest_tab3_frame, text="防呆复位", font=("宋体", 10 ,"bold")).place(x=0, y=0)


#防呆复位——BurnKey
fulltest_Burnkey_check = tk.BooleanVar(value=True)   ##需要修改为读文件的值
Burnkey_checkbutton = ttk.Checkbutton(fulltest_tab3_frame, variable=fulltest_Burnkey_check, state=DISABLED)
Burnkey_checkbutton.place(x=0, y=55)
ttk.Label(fulltest_tab3_frame, text="KEY烧录", width = 10, font=("宋体", 20 ,"bold")).place(x=25, y=50)
Status_Burnkey = ttk.Label(fulltest_tab3_frame, style='stylegray.TLabel',width = 10, font=("宋体", 20 ,"bold")).place(x=150,y=50)

#防呆复位——WB
fulltest_WB = tk.BooleanVar(value=True)   ##需要修改为读文件的值
WB_checkbutton = ttk.Checkbutton(fulltest_tab3_frame, variable=fulltest_WB, state=DISABLED)
WB_checkbutton.place(x=0, y=105)
ttk.Label(fulltest_tab3_frame, text="白平衡", width = 10, font=("宋体", 20 ,"bold")).place(x=25, y=100)
Status_WB = ttk.Label(fulltest_tab3_frame, style='stylegray.TLabel',width = 10, font=("宋体", 20 ,"bold")).place(x=150,y=100)

#防呆复位——HDMI1
fulltest_HDMI1 = tk.BooleanVar(value=True)  ##需要修改为读文件的值
HDMI1_checkbutton = ttk.Checkbutton(fulltest_tab3_frame, variable=fulltest_HDMI1, state=DISABLED)
HDMI1_checkbutton.place(x=0, y=155)
ttk.Label(fulltest_tab3_frame, text="HDMI1", width = 10, font=("宋体", 20 ,"bold")).place(x=25, y=150)
Status_HDMI1 = ttk.Label(fulltest_tab3_frame, style='stylegray.TLabel',width = 10, font=("宋体", 20 ,"bold")).place(x=150,y=150)

#防呆复位——HDMI2
fulltest_HDMI2 = tk.BooleanVar(value=True)  ##需要修改为读文件的值
HDMI2_checkbutton = ttk.Checkbutton(fulltest_tab3_frame, variable=fulltest_HDMI2, state=DISABLED)
HDMI2_checkbutton.place(x=0, y=205)
ttk.Label(fulltest_tab3_frame, text="HDMI2", width = 10, font=("宋体", 20 ,"bold")).place(x=25, y=200)
Status_HDMI2 = ttk.Label(fulltest_tab3_frame, style='stylegray.TLabel',width = 10, font=("宋体", 20 ,"bold")).place(x=150,y=200)

#防呆复位——HDMI3
fulltest_HDMI3 = tk.BooleanVar(value=True)  ##需要修改为读文件的值
HDMI3_checkbutton = ttk.Checkbutton(fulltest_tab3_frame, variable=fulltest_HDMI3, state=DISABLED)
HDMI3_checkbutton.place(x=0, y=255)
ttk.Label(fulltest_tab3_frame, text="HDMI3", width = 10, font=("宋体", 20 ,"bold")).place(x=25, y=250)
Status_HDMI3 = ttk.Label(fulltest_tab3_frame, style='stylegray.TLabel',width = 10, font=("宋体", 20 ,"bold")).place(x=150,y=250)

#防呆复位——DTV
fulltest_DTV = tk.BooleanVar(value=True)  ##需要修改为读文件的值
DTV_checkbutton = ttk.Checkbutton(fulltest_tab3_frame, variable=fulltest_DTV, state=DISABLED)
DTV_checkbutton.place(x=0, y=305)
ttk.Label(fulltest_tab3_frame, text="DTV", width = 10, font=("宋体", 20 ,"bold")).place(x=25, y=300)
Status_DTV = ttk.Label(fulltest_tab3_frame, style='stylegray.TLabel',width = 10, font=("宋体", 20 ,"bold")).place(x=150,y=300)

#防呆复位——USB
fulltest_USB= tk.BooleanVar(value=True)  ##需要修改为读文件的值
USB_checkbutton = ttk.Checkbutton(fulltest_tab3_frame, variable=fulltest_USB, state=DISABLED)
USB_checkbutton.place(x=0, y=355)
ttk.Label(fulltest_tab3_frame, text="USB", width = 10, font=("宋体", 20 ,"bold")).place(x=25, y=350)
Status_USB = ttk.Label(fulltest_tab3_frame, style='stylegray.TLabel',width = 10, font=("宋体", 20 ,"bold")).place(x=150,y=350)

#防呆复位——按键
fulltest_KEYPAD = tk.BooleanVar(value=True)  ##需要修改为读文件的值
KEYPAD_checkbutton = ttk.Checkbutton(fulltest_tab3_frame, variable=fulltest_KEYPAD, state=DISABLED)
KEYPAD_checkbutton.place(x=320, y=55)
ttk.Label(fulltest_tab3_frame, text="按键", width = 10, font=("宋体", 20 ,"bold")).place(x=345, y=50)
Status_KEYPAD = ttk.Label(fulltest_tab3_frame, style='stylegray.TLabel',width = 10, font=("宋体", 20 ,"bold")).place(x=470,y=50)

#防呆复位——遥控IR
fulltest_IR = tk.BooleanVar(value=True)  ##需要修改为读文件的值
IR_checkbutton = ttk.Checkbutton(fulltest_tab3_frame, variable=fulltest_IR, state=DISABLED)
IR_checkbutton.place(x=320, y=105)
ttk.Label(fulltest_tab3_frame, text="遥控IR", width = 10, font=("宋体", 20 ,"bold")).place(x=345, y=100)
Status_IR = ttk.Label(fulltest_tab3_frame, style='stylegray.TLabel',width = 10, font=("宋体", 20 ,"bold")).place(x=470,y=100)

#防呆复位——DEMO
fulltest_DEMO = tk.BooleanVar(value=True)  ##需要修改为读文件的值
DEMO_checkbutton = ttk.Checkbutton(fulltest_tab3_frame, variable=fulltest_DEMO, state=DISABLED)
DEMO_checkbutton.place(x=320, y=155)
ttk.Label(fulltest_tab3_frame, text="DEMO", width = 10, font=("宋体", 20 ,"bold")).place(x=345, y=150)
Status_DEMO = ttk.Label(fulltest_tab3_frame, style='stylegray.TLabel',width = 10, font=("宋体", 20 ,"bold")).place(x=470,y=150)

#防呆复位——启用/停用
check_module_button_text = tk.StringVar(value="启用")
check_module_button = tk.Button(fulltest_tab3_frame, textvariable=check_module_button_text, width = 6, font=("宋体", 15 ,"bold"), command = lambda: enable_fulltest_Module(check_module_button_text), state=DISABLED)       #待补充command参数
check_module_button.place(x=470, y=390)
#防呆复位——测试
check_test_button = tk.Button(fulltest_tab3_frame, text="测试", width = 6, font=("宋体", 15 ,"bold"))       #待补充command参数
check_test_button.place(x=550, y=390)

#防呆复位模块2
fulltest_tab4_frame = ttk.Frame(fulltest_frame, padding=10, relief=tk.SOLID, borderwidth=2, width = 500, height = 250)
fulltest_tab4_frame.place(x=1090, y=100)
ttk.Label(fulltest_tab4_frame, text="WIFI/BT", font=("宋体", 10 ,"bold")).place(x=0, y=0)
ttk.Label(fulltest_tab4_frame, text="最小值", font=("宋体", 12 ,"bold")).place(x=280, y=0)
ttk.Label(fulltest_tab4_frame, text="最大值", font=("宋体", 12 ,"bold")).place(x=380, y=0)
#防呆复位——WIFI1
fulltest_WIFI1_check = tk.BooleanVar(value=True)   ##需要修改为读文件的值
WIFI1_checkbutton = ttk.Checkbutton(fulltest_tab4_frame, variable=fulltest_WIFI1_check, state=DISABLED)
WIFI1_checkbutton.place(x=0, y=35)
ttk.Label(fulltest_tab4_frame, text="WIFI1", width = 6, font=("宋体", 20 ,"bold")).place(x=25, y=30)
Status_WIFI1 = ttk.Label(fulltest_tab4_frame, style='stylegray.TLabel',width = 8, font=("宋体", 20 ,"bold")).place(x=110,y=30)
fulltest_WIFI1_min = tk.StringVar(value = -70)   #上限，需要修改为读文件的值
WIFI1_min_entry = ttk.Entry(fulltest_tab4_frame, textvariable=fulltest_WIFI1_min, width = 6, font=("宋体", 20 ,"bold"), state=DISABLED)
WIFI1_min_entry.place(x=280,y=30)
fulltest_WIFI1_max = tk.StringVar(value = 0)   #下限，需要修改为读文件的值
WIFI1_max_entry = ttk.Entry(fulltest_tab4_frame, textvariable=fulltest_WIFI1_max, width = 6, font=("宋体", 20 ,"bold"), state=DISABLED)
WIFI1_max_entry.place(x=380,y=30)
#防呆复位——WIFI2
fulltest_WIFI2_check = tk.BooleanVar(value=True)   ##需要修改为读文件的值
WIFI2_checkbutton = ttk.Checkbutton(fulltest_tab4_frame, variable=fulltest_WIFI2_check, state=DISABLED)
WIFI2_checkbutton.place(x=0, y=85)
ttk.Label(fulltest_tab4_frame, text="WIFI2", width = 6, font=("宋体", 20 ,"bold")).place(x=25, y=80)
Status_WIFI2 = ttk.Label(fulltest_tab4_frame, style='stylegray.TLabel',width = 8, font=("宋体", 20 ,"bold")).place(x=110,y=80)
fulltest_WIFI2_min = tk.StringVar(value = -70)   #上限，需要修改为读文件的值
WIFI2_min_entry = ttk.Entry(fulltest_tab4_frame, textvariable=fulltest_WIFI2_min, width = 6, font=("宋体", 20 ,"bold"), state=DISABLED)
WIFI2_min_entry.place(x=280,y=80)
fulltest_WIFI2_max = tk.StringVar(value = 0)   #下限，需要修改为读文件的值
WIFI2_max_entry = ttk.Entry(fulltest_tab4_frame, textvariable=fulltest_WIFI2_max, width = 6, font=("宋体", 20 ,"bold"), state=DISABLED)
WIFI2_max_entry.place(x=380,y=80)
#防呆复位——BT
fulltest_BT_check = tk.BooleanVar(value=True)   ##需要修改为读文件的值
BT_checkbutton = ttk.Checkbutton(fulltest_tab4_frame, variable=fulltest_BT_check, state=DISABLED)
BT_checkbutton.place(x=0, y=135)
ttk.Label(fulltest_tab4_frame, text="BT", width = 6, font=("宋体", 20 ,"bold")).place(x=25, y=130)
Status_BT = ttk.Label(fulltest_tab4_frame, style='stylegray.TLabel',width = 8, font=("宋体", 20 ,"bold")).place(x=110,y=130)
fulltest_BT_min = tk.StringVar(value = -80)   #上限，需要修改为读文件的值
BT_min_entry = ttk.Entry(fulltest_tab4_frame, textvariable=fulltest_BT_min, width = 6, font=("宋体", 20 ,"bold"), state=DISABLED)
BT_min_entry.place(x=280,y=130)
fulltest_BT_max = tk.StringVar(value = 0)   #下限，需要修改为读文件的值
BT_max_entry = ttk.Entry(fulltest_tab4_frame, textvariable=fulltest_BT_max, width = 6, font=("宋体", 20 ,"bold"), state=DISABLED)
BT_max_entry.place(x=380,y=130)
#防呆复位——WIFI/BT——启用/停用
checkRSSI_module_button_text = tk.StringVar(value="启用")
checkRSSI_module_button = tk.Button(fulltest_tab4_frame, textvariable=checkRSSI_module_button_text, width = 6, font=("宋体", 15 ,"bold"), command = lambda: enable_fulltest_Module(checkRSSI_module_button_text), state=DISABLED)       #待补充command参数
checkRSSI_module_button.place(x=320, y=190)
#防呆复位——WIFI/BT——测试
checkRSSI_test_button = tk.Button(fulltest_tab4_frame, text="测试", width = 6, font=("宋体", 15 ,"bold"))       #待补充command参数
checkRSSI_test_button.place(x=400, y=190)

#防呆复位——模块3
fulltest_tab5_frame = ttk.Frame(fulltest_frame, padding=10, relief=tk.SOLID, borderwidth=2, width = 500, height = 80)
fulltest_tab5_frame.place(x=1090, y=370)
ttk.Label(fulltest_tab5_frame, text="复位", font=("宋体", 10 ,"bold")).place(x=0, y=0)
#防呆复位——复位
fulltest_reset_check = tk.BooleanVar(value=True)   ##需要修改为读文件的值
reset_checkbutton = ttk.Checkbutton(fulltest_tab5_frame, variable=fulltest_reset_check, state=DISABLED)
reset_checkbutton.place(x=0, y=35)
ttk.Label(fulltest_tab5_frame, text="复位", width = 6, font=("宋体", 20 ,"bold")).place(x=25, y=30)
Status_reset = ttk.Label(fulltest_tab5_frame, style='stylegray.TLabel',width = 8, font=("宋体", 20 ,"bold")).place(x=110,y=30)
#防呆复位——复位——启用/停用
reset_module_button_text = tk.StringVar(value = "启用")
reset_module_button = tk.Button(fulltest_tab5_frame, textvariable=reset_module_button_text, width = 6, font=("宋体", 15 ,"bold"), command = lambda: enable_fulltest_Module(reset_module_button_text), state=DISABLED)       #待补充command参数
reset_module_button.place(x=320, y=30)
#防呆复位——复位——测试
reset_test_button = tk.Button(fulltest_tab5_frame, text="测试", width = 6, font=("宋体", 15 ,"bold"))       #待补充command参数
reset_test_button.place(x=400, y=30)

#防呆复位——模块4
fulltest_tab6_frame = ttk.Frame(fulltest_frame, padding=10, relief=tk.SOLID, borderwidth=2, width = 500, height = 80)
fulltest_tab6_frame.place(x=1090, y=470)
ttk.Label(fulltest_tab6_frame, text="上传mes（IP同烧key mes）", font=("宋体", 10 ,"bold")).place(x=0, y=0)
#防呆复位——上传mes
fulltest_reset_mes_check = tk.BooleanVar(value=True)   ##需要修改为读文件的值
reset_mes_checkbutton = ttk.Checkbutton(fulltest_tab6_frame, variable=fulltest_reset_mes_check, state=DISABLED)
reset_mes_checkbutton.place(x=0, y=35)
ttk.Label(fulltest_tab6_frame, text="上传", width = 6, font=("宋体", 20 ,"bold")).place(x=25, y=30)
Status_reset_mes = ttk.Label(fulltest_tab6_frame, style='stylegray.TLabel',width = 8, font=("宋体", 20 ,"bold")).place(x=110,y=30)
#防呆复位——复位——启用/停用
reset_mes_module_button_text = tk.StringVar(value="启用")
reset_mes_module_button = tk.Button(fulltest_tab6_frame, textvariable=reset_mes_module_button_text, width = 6, font=("宋体", 15 ,"bold"), command = lambda: enable_fulltest_Module(reset_mes_module_button_text), state=DISABLED)       #待补充command参数
reset_mes_module_button.place(x=320, y=30)
#防呆复位——复位——测试
reset_mes_test_button = tk.Button(fulltest_tab6_frame, text="测试", width = 6, font=("宋体", 15 ,"bold"))       #待补充command参数
reset_mes_test_button.place(x=400, y=30)

################################################################################
################################################################################
# 创建 参数设置 选项卡
settings_frame = ttk.Frame(notebook)
notebook.add(settings_frame, text="参数设置")


# 参数设置控件
tk.Label(settings_frame, text="Port:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
port_var = tk.StringVar()
port_combobox = ttk.Combobox(settings_frame, textvariable=port_var, state="readonly")
port_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
update_port_list()

tk.Label(settings_frame, text="Baud Rate:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
baud_rate_entry = tk.Entry(settings_frame)
baud_rate_entry.insert(0, "115200")
baud_rate_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)

tk.Label(settings_frame, text="Timeout (s):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
timeout_entry = tk.Entry(settings_frame)
timeout_entry.insert(0, "0.1")
timeout_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W+tk.E)

connect_button = tk.Button(settings_frame, text="Connect", command=connect_serial)
connect_button.grid(row=3, column=0, padx=5, pady=10, sticky=tk.W+tk.E)

disconnect_button = tk.Button(settings_frame, text="Disconnect", command=disconnect_serial)
disconnect_button.grid(row=3, column=1, padx=5, pady=10, sticky=tk.W+tk.E)

# 添加参数设置的状态标签
status_label = tk.Label(settings_frame, height=2, width=20, wraplength=300, justify=tk.CENTER)
status_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)

################################################################################


# 尝试打开串口
if not open_serial():
    log("打开串口失败，请在参数设置中尝试连接。")
    update_setting_status("串口未连接", connected=False)
    close_serial()
#################################################################################

#配置初始化
init_test_config()
config = read_testconfig()

fulltest_workorder.set(config.get('DEFAULT','workorder_entry'))
# fulltest_workorder.set(config.get('DEFAULT','workorder_entry').fallback='') fallback用于设默认值
fulltest_IP.set(config.get('DEFAULT','IP_entry'))
fulltest_port.set(config.get('DEFAULT','port_entry'))
fulltest_ULPKlimit_min.set(config.get('DEFAULT','ULPKlimit_min_entry'))
fulltest_ULPKlimit_max.set(config.get('DEFAULT','ULPKlimit_max_entry'))
fulltest_FWver.set(config.get('DEFAULT','FWver_entry'))
fulltest_modelindex.set(config.get('DEFAULT','modelindex_entry'))
fulltest_check_key_to_mes.set(config.getboolean('DEFAULT','check_key_to_mes_checkbutton'))
burnkey_module_button_text.set(config.get('DEFAULT','burnkey_module_button'))

fulltest_Burnkey_check.set(config.getboolean('DEFAULT','Burnkey_checkbutton'))
fulltest_WB.set(config.getboolean('DEFAULT','WB_checkbutton'))
fulltest_HDMI1.set(config.getboolean('DEFAULT','HDMI1_checkbutton'))
fulltest_HDMI2.set(config.getboolean('DEFAULT','HDMI2_checkbutton'))
fulltest_HDMI3.set(config.getboolean('DEFAULT','HDMI3_checkbutton'))
fulltest_DTV.set(config.getboolean('DEFAULT','DTV_checkbutton'))
fulltest_USB.set(config.getboolean('DEFAULT','USB_checkbutton'))
fulltest_KEYPAD.set(config.getboolean('DEFAULT','KEYPAD_checkbutton'))
fulltest_IR.set(config.getboolean('DEFAULT','IR_checkbutton'))
fulltest_DEMO.set(config.getboolean('DEFAULT','DEMO_checkbutton'))
check_module_button_text.set(config.get('DEFAULT','check_module_button'))

fulltest_WIFI1_check.set(config.getboolean('DEFAULT','WIFI1_checkbutton'))
fulltest_WIFI1_min.set(config.get('DEFAULT','WIFI1_min_entry'))
fulltest_WIFI1_max.set(config.get('DEFAULT','WIFI1_max_entry'))
fulltest_WIFI2_check.set(config.getboolean('DEFAULT','WIFI2_checkbutton'))
fulltest_WIFI2_min.set(config.get('DEFAULT','WIFI2_min_entry'))
fulltest_WIFI2_max.set(config.get('DEFAULT','WIFI2_max_entry'))
fulltest_BT_check.set(config.getboolean('DEFAULT','BT_checkbutton'))
fulltest_BT_min.set(config.get('DEFAULT','BT_min_entry'))
fulltest_BT_max.set(config.get('DEFAULT','BT_max_entry'))
checkRSSI_module_button_text.set(config.get('DEFAULT','checkRSSI_module_button'))

fulltest_reset_check.set(config.getboolean('DEFAULT','reset_checkbutton'))
reset_module_button_text.set(config.get('DEFAULT','reset_module_button'))

fulltest_reset_mes_check.set(config.getboolean('DEFAULT','reset_mes_checkbutton'))
reset_mes_module_button_text.set(config.get('DEFAULT','reset_mes_module_button'))

# 启动Tkinter主循环
log("Starting main loop...")
root.mainloop()