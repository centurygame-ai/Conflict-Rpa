import json
import os


def read_all_config():
    """读取所有配置"""
    home_dir = os.path.expanduser("~")
    config_dict_path = os.path.join(home_dir, '.crpa')
    os.makedirs(config_dict_path, exist_ok=True)
    config_path = os.path.join(config_dict_path, 'openai.json')
    try:
        if not os.path.exists(config_path):
            return None

        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except Exception as e:
        print(f"读取配置文件时发生异常: {e}")
        return None


def save_config(config_data):
    """保存配置到文件，并验证保存是否成功"""
    home_dir = os.path.expanduser("~")
    config_dict_path = os.path.join(home_dir, '.crpa')
    os.makedirs(config_dict_path, exist_ok=True)
    config_path = os.path.join(config_dict_path, 'openai.json')
    try:
        with open(config_path, 'w') as config_file:
            json.dump(config_data, config_file, indent=4)
        # 验证保存的数据和传入的数据是否一致
        saved_data = read_all_config()
        if saved_data == config_data:
            print("配置保存成功")
            return True
        else:
            print("配置保存失败")
            return False
    except Exception as e:
        print(f"保存配置文件时发生异常: {e}")
        return False


def init_config():
    OPENAI_API_KEY = input("输入-OPENAI API KEY: ")
    OPENAI_API_BASE = input("输入-OPENAI API BASE(空为默认): ")
    print("OPENAI API KEY:", OPENAI_API_KEY)
    if len(OPENAI_API_BASE) > 0:
        print("OPENAI API BASE:", OPENAI_API_BASE)
    print(OPENAI_API_BASE)
    save_config({
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "OPENAI_API_BASE": OPENAI_API_BASE
    })
    print('完成')
