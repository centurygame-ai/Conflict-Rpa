"""
1. 进行当前执行命令的判断，是否有错，是否有值得修改的文件
2. 在循环中
    * 返回新执行指令
    * 进行文档内修改
    * 重新执行
    * 重新评估
3. 在循环之后没有正确完成，则还原原本文档
"""
import asyncio
import json
import os
import platform
import subprocess

from conflict_rpa.file_operation import recover_file, get_lines_around, edit_file
from conflict_rpa.get_running_env import get_running_env
from conflict_rpa.utils import async_chat, LLMParams

debug = True
shell_name = 'bash'
shell = os.getenv('SHELL')
if shell:
    if 'bash' in shell:
        shell_name = 'bash'
    elif 'zsh' in shell:
        shell_name = 'zsh'
else:
    if platform.system() == 'Windows':
        comspec = os.getenv('ComSpec')
        if comspec:
            print(comspec)
            if 'cmd.exe' in comspec.lower():
                shell_name = 'cmd'


def DEBUG(*args, **kwargs):
    if debug:
        print(*args)


def operate_script(script):
    env = dict(os.environ)
    # 使用 subprocess.Popen 执行 Bash 命令并捕获输出
    try:
        process = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                   env=env,
                                   encoding='utf-8')
        outputs = ''
        # 实时地将输出同步到标准输出中
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                outputs += output.strip() + ' '
        # 捕获并打印任何错误输出
        stderr = process.communicate()[1]
        if stderr:
            print(stderr.strip())
            outputs += stderr.strip() + ' '
    except UnicodeDecodeError as e:
        print('尝试使用unicode编码')
        process = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                   env=env)
        outputs = ''
        # 实时地将输出同步到标准输出中
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                outputs += output.strip() + ' '
        # 捕获并打印任何错误输出
        stderr = process.communicate()[1]
        if stderr:
            print(stderr.strip())
            outputs += stderr.strip() + ' '

    return outputs


def generate(prompt: str, json_mode=False):
    messages = [
        {
            'role': 'user',
            'content': prompt}
    ]
    output = asyncio.run(async_chat(messages, LLMParams(json_mode=json_mode, model="gpt-4o", max_tokens=4096)))
    return output


def check_correctness(script):
    # PIPE OPEN 后的环境已经是conda 内的环境了,验证了一下确实如此
    # conda_env = os.getenv('CONDA_DEFAULT_ENV')
    # if conda_env:
    #     script = f'conda   conda activate {conda_env}; ' + script
    output = operate_script(script)
    if output == 'timeout':
        return output, None
    prompt = f'''在以下的{shell_name}执行环境下
```
{get_running_env()}
```

对于{shell_name}指令(script)
```
> {script}
```
执行后产生如下输出
```
> {output}
```
请对于该格式的运行结果进行如下判断，你的输出应该为JSON格式:''' + '''{
    "correctness": bool // 该指令的是否被正确执行，执行结果中是否有报错
    "error_in_script": bool // 如果该指令没有被正确执行，原因为使用了错误的指令，如拼写作物或者错误的使用方法等
    "error_in_file": bool // 如果该指令没有被正确执行，原因为**用户编写**的代码中存在明显错误
    "additional_operation_lack": bool // 如果该指令没有被正确执行，原因是需要执行额外的指令，如pip安装依赖，或者实现执行其他脚本
    'natural_language_description': //该指令是不是一个描述命令行命令的自然语言
    "file_path": str // 如果 error_in_file=True，那么需要被修改的文件的路径
    "error_line_number": int // 如果 error_in_file=True，需要被修改文件的对应行数
}'''
    DEBUG('prompt: ', prompt)
    check_res = json.loads(generate(prompt, json_mode=True))
    return check_res, output


def corrigenda_script(script, output):
    prompt = f'''在以下的{shell_name}执行环境下
```
{get_running_env()}
```
用户使用如下{shell_name} 指令(script)
```
{script}
```    
获得了以下的错误信息
```
{output}
```
现在你需要还原用户在指令中存在的错误，分析后返回我被更正的，满足用户意图的，正确被执行的指令。
为了方便你进行思考，你应该输出为以下JSON格式:''' + '''{
    "user_intent": str //还原用户想实现怎样的脚本功能，是什么地方的错误导致命令无法执行
    "new_script": str //被更正后的指令，需要完全满足用户意图，且可以被正确执行的指令：如果完全无从下手，给出查询有效信息的指令，以便对于对当前问题进行诊断
}'''
    DEBUG('prompt: ', prompt)
    corrigenda_res = json.loads(generate(prompt, json_mode=True))
    return corrigenda_res


def corrigenda_natural_language(script, output):
    prompt = f'''在以下的{shell_name}执行环境下
```
{get_running_env()}
```
用户输入以下自然语言，希望在{shell_name}中执行其描述的操作
```
script={script}
```
现在你需要还原用户的指令要求，分析后返回满足用户意图的，正确被执行的指令。
为了方便你进行思考，你应该输出为以下JSON格式:''' + '''{
    "user_intent": str //还原用户想实现怎样的脚本功能
    "new_script": str //被更正后的指令，需要完全满足用户意图，且可以被正确执行的指令.如果完全无从下手，给出查询有效信息的指令，以便对于对当前问题进行诊断
}'''
    DEBUG('prompt: ', prompt)
    corrigenda_res = json.loads(generate(prompt, json_mode=True))
    return corrigenda_res


def corrigenda_additional_operation(script, output):
    prompt = f'''在以下的{shell_name}执行环境下
```
{get_running_env()}
```
用户使用如下{shell_name} 指令(script)
```
{script}
```    
获得了以下的错误信息
```
{output}
```
你发现需要执行额外的{shell_name}命令后，该错误可以解决，现在请你输出需要提前执行什么脚本
为了方便你进行思考，你应该输出为以下JSON格式:''' + '''{
    "user_intent": str //还原用户想实现怎样的脚本功能，是缺少什么设置导致无法执行
    "new_script": str //需要额外执行的脚本.如果完全无从下手，给出查询有效信息的指令，以便对于对当前问题进行诊断
}'''
    DEBUG('prompt: ', prompt)
    corrigenda_res = json.loads(generate(prompt, json_mode=True))
    return corrigenda_res


def corrigenda_file(script, output, file_path, line_count, content):
    prompt = f'''在以下的{shell_name}执行环境下
```
{get_running_env()}
```
用户在运行以下{shell_name}指令(script)
```
{script}
```
获得了以下错误信息
```
{output}
```
你注意到这个错误与 `{file_path}` 中第{line_count}行的内容有关，该文件对应位置附近的文本如下所示:
``` content:
{content}
```
现在你需要按照要求对于content中出现的错误进行修正，在尽量不影响代码原本功能的前提下以解决报错。你需要集中解决{shell_name}报错中的问题，而不是其他可能性bug，对脚本中的原有信息尽量不去改动。
为了帮助你更好地思考，你的输出应该是以下JSON格式:''' + '''{
     "code_understanding": str //对于现有的代码进行分析和理解，分析其实现的功能，结合报错日志，分析代码附近是否有错误
     "editable": bool //报错是否来源于此段代码的错误
     "new_content": str //if editable=True 对于输入content进行的修改与替换，在解决问题的前提下尽量保证其他代码不受影响，包括变量名称，缩进与注释
}'''
    DEBUG('prompt: ', prompt)
    corrigenda_res = json.loads(generate(prompt, json_mode=True))
    return corrigenda_res


def main_loop(origin_script: str, MAX_LOOP=5, verbose=False):
    global debug
    debug = verbose
    script = origin_script
    correct_res, output = check_correctness(script)
    if correct_res == 'timeout':
        return
    if correct_res['correctness']:
        print('------------------------------')
        print('初始验证: 程序执行成功')
        print("执行结果:")
        print(output)
        return
    # 为了修正文件错误而修改的原文本
    changed_file_list = []
    for i in range(MAX_LOOP):
        DEBUG('output: ', output)
        print(f">>尝试 {i + 1}...")
        DEBUG(f'命令: {script}')
        # 进行三个方向的修正
        if correct_res['error_in_script']:
            res = corrigenda_script(script, output)
            script = res['new_script']
        elif correct_res['error_in_file']:
            file_path = correct_res['file_path']
            line_count = correct_res['error_line_number']
            if not os.path.exists(file_path) or not isinstance(line_count, int):
                DEBUG('no such a file to edit', file_path)
                break
            if file_path in changed_file_list:
                content, start_line, end_line = get_lines_around(file_path, line_count,
                                                                 save_copy=False)
            else:
                # 这个文件被第一次修改，所以去保存一下副本
                changed_file_list.append(file_path)
                content, start_line, end_line = get_lines_around(file_path, line_count,
                                                                 save_copy=True)
            res = corrigenda_file(script, output, file_path, line_count, content)
            if not res['editable']:
                DEBUG(f'no error found in {file_path}')
                break
            edit_file(file_path, start_line, end_line, res['new_content'])
        elif correct_res['additional_operation_lack']:
            res = corrigenda_additional_operation(script, output)
            new_script = res['new_script']
            script = f"{new_script}; {script}"
        elif correct_res['natural_language_description']:
            res = corrigenda_natural_language(script, output)
            script = res['new_script']
        else:
            # GPT说我干不了
            break
        print(f'''>重新尝试执行: 
{script}''')

        correct_res, output = check_correctness(script)
        if correct_res == 'timeout':
            return
        if correct_res['correctness']:
            print('程序执行成功')
            print(f"命令: {script}")
            print(f"被修改的文件: {changed_file_list}")
            print("执行结果:")
            print(output)
            return
    # 恢复被GPT弄到乱七八糟的文件
    for file_path in changed_file_list:
        recover_file(file_path)
    print('------------------------------')
    print('自动修正失败，请您另请高明')
    print('最后执行操作:')
    print(script)
    print(f'最终执行结果:')
    print(output)
    return
