import json

from conflict_rpa.correcting_framework import generate, main_loop
from conflict_rpa.get_running_env import get_running_env


def analyse_tutorial(content):
    prompt = '''
从以下文本中抽取有效信息，你的输出应该是JSON格式，包含以下内容:
{   
    'topic': str // 文本是关于什么主题，包含了哪些有价值的信息
    'operation_include': bool // 文本信息中是否有包含一系列可执行的命令，这些命令在顺序执行后可以完成 应用安装/执行/初始化等操作
    'script_requirement': str //网页中的指令执行依赖的系统要求，包括系统，硬件配置，其他软件依赖等
    'additional_commands': List[str] //是否需要执行额外的操作，如执行github url指南时，没有git clone 或没有进入项目目录。将这里得到的额外指令也加入到`scripts`中
    'scripts': List[str] //if operation_include=True，那么请按顺序，严格抽取命令（尤其是关于installation，getting start等内容）(不包括其他任何语言的代码块！要在命令行中执行)并组织为列表，这样的列表在顺序执行后可以完成网站中项目的基础功能。如果文本中包含多种执行方法，则选择其中最匹配当前执行环境的方法.果命令中包含类似`/where/you/keep/code`的路径，将这些自定义路径修改为当前目录即可
}''' + f'''
当前程序运行的环境信息为
```
{get_running_env()}
```
以下是完整的文本内容
```
{content}
```'''
    res = generate(prompt, json_mode=True)
    return json.loads(res)


def content_rpa(content, verbose=False):
    analysis = analyse_tutorial(content)
    if analysis['operation_include']:
        print('输入文本: ', analysis['topic'])
        print('环境需求:', analysis['script_requirement'])
        print('将执行以下指令:')
        for script in analysis['scripts']:
            print('*', script)
        while True:
            user_input = input("Do you want to continue? (yes/no): ")
            if user_input.lower() == 'yes':
                # 用户确认继续
                print("开始执行命令")
                dir_cmds = []
                for script in analysis['scripts']:
                    if script[0] == '#':
                        continue
                    elif 'cd ' == script[:3]:
                        dir_cmds.append(script)
                    elif 'conda activate' in script:
                        dir_cmds.append(script)
                    elif 'source ' in script:
                        dir_cmds.append(script)
                    else:
                        res = ''
                        for cmd in dir_cmds:
                            res += f'{cmd}; '
                        res += script
                        print('尝试执行: ', res)
                        main_loop(res, verbose=verbose)
                return
                # 这里放置你接下来要执行的命令
            elif user_input.lower() == 'no':
                # 用户选择不继续
                print("Operation cancelled by the user.")
                break
            else:
                # 处理无效的输入
                print("Invalid input. Please enter 'yes' or 'no'.")
    else:
        print('此文本的信息: ', analysis['topic'])
        print('此文本不存在可执行指令')
