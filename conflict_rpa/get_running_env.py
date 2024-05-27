import subprocess
import platform
import os
import json


def get_bash_version():
    try:
        bash_version = subprocess.run(['bash', '--version'], capture_output=True, text=True).stdout.split('\n')[0]
        return bash_version
    except Exception as e:
        return str(e)


def get_cpu_info():
    try:
        if platform.system() == "Linux":
            cpu_info = subprocess.run(['lscpu'], capture_output=True, text=True).stdout
        elif platform.system() == "Darwin":
            cpu_info = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], capture_output=True,
                                      text=True).stdout.strip()
        elif platform.system() == "Windows":
            cpu_info = \
                subprocess.run(['wmic', 'cpu', 'get', 'name'], capture_output=True, text=True).stdout.split('\n')[
                    1].strip()
        return cpu_info
    except Exception as e:
        return str(e)


def get_gpu_info():
    try:
        gpu_info = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], capture_output=True,
                                  text=True).stdout.strip()
        return gpu_info if gpu_info else "No GPU found"
    except Exception as e:
        return str(e)


def check_docker():
    try:
        docker_version = subprocess.run(['docker', '--version'], capture_output=True, text=True).stdout.strip()
        return docker_version if docker_version else "Docker not found"
    except Exception as e:
        return "Docker not installed"


def get_python_version():
    try:
        python_version = subprocess.run(['python', '--version'], capture_output=True, text=True).stdout.strip()
        return python_version
    except Exception as e:
        return str(e)


def get_npm_version():
    try:
        npm_version = subprocess.run(['npm', '--version'], capture_output=True, text=True).stdout.strip()
        return npm_version
    except Exception as e:
        return str(e)


def get_shell_type():
    try:
        shell = os.environ.get('SHELL')
        if shell:
            return shell
        elif platform.system() == "Windows":
            if 'COMSPEC' in os.environ:
                return os.environ['COMSPEC']
            else:
                return "Command Prompt (cmd.exe)"
        return "Unknown"
    except Exception as e:
        return str(e)



def get_running_env():
    config = {
        "bash_version": get_bash_version(),
        # "cpu_info": get_cpu_info(),
        "gpu_info": get_gpu_info(),
        "docker_version": check_docker(),
        "python_version": get_python_version(),
        "npm_version": get_npm_version(),
        "shell_type": get_shell_type(),
        "conda_env_now": os.getenv('CONDA_DEFAULT_ENV')
    }

    config_string = json.dumps(config, indent=4)
    return config_string


if __name__ == "__main__":
    get_running_env()
