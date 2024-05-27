# Conflict RPA

```shell
  ____ ____  ____   _
 / ___|  _ \|  _ \ / \
| |   | |_) | |_) / _ \
| |___|  _ <|  __/ ___ \
 \____|_| \_\_| /_/   \_\
```

* 一个应用在 `bash/zsh/powershell` 上的python包，利用[GPT](https://github.com/openai/openai-python)
  实现与[thefuck](https://github.com/nvbn/thefuck)略有不同的效果，尤其是解决一些类似于依赖冲突这样不费脑子但是很费时间的问题。
* 功能可以概括为两类
    * 通过修正bash 指令或者代码使其运行不出现报错
    * 将自然语言转化为bash指令直到正确执行
    * <span style="color:red; font-weight:bold;">Warning</span> 因为该工具确实会自动执行额外的操作，(虽然没有遇到过)
      目前难以排除他会执行一些恶性操作的风险。以此为免责声明。

## 安装

建议`python>=3.10`

```shell
pip install conflict_rpa
conflict_rpa
# 进行相关配置
# source ~/.bashrc 或重启bash
crpa
```

* 源码安装

```shell
pip install --upgrade pip setuptools 
pip install .
```

source ~/.bashrc或重启bash以生效

## 运行

```shell
crpa -h
```

* 第一次执行时需要用户填入 `OPENAI API`配置

## 功能

### 命令行纠错

```shell
➜  git coomot -am
git: 'coomot' is not a git command. See 'git --help'.

The most similar command is
        commit

➜  crpa
# after a sequence of analysis logs
程序执行成功
bash命令“ git config --global user.email "you@example.com"
git config --global user.name "Your Name"; git commit -am 'your commit message'
被修改的文件: []
执行结果:
[main 242105a] your commit message 11 files changed, 843 insertions(+), 863 deletions(-) rewrite README.md (100%)
```

### 代码纠错

* 在`test`文件夹下做了一些代码修复样例
* 纠错过程中会修改原始文件，但会保留所有被修改文件的备份`*.bak`

``` shell
➜  python test/test_for_multifile/main.py
Traceback (most recent call last):
  File "test/test_for_multifile/main.py", line 1, in <module>
    from test.test_for_multifile.count import count
ModuleNotFoundError: No module named 'test.test_for_multifile'

➜  crpa
# after a sequence of analysis logs
程序执行成功
bash命令“ export PYTHONPATH=$(pwd)/test; python test/test_for_multifile/main.py; export PYTHONPATH=$(pwd); python test/test_for_multifile/main.py
被修改的文件: ['test/test_for_multifile/main.py', 'test/test_for_multifile/count.py']
执行结果:
3 3
```

原始文件

```python
# count.py
def count(a: int, b: int):
    assert isinstance(a, str)
    return a + b


# main.py
from test.test_for_multifile.count import count

print(count(1, 2))
```

修改后文件

```python
# count.py
def count(a: int, b: int):
    assert isinstance(a, int)
    return a + b


# main.py
from count import count

print(count(1, 2))
```

### 自动执行教程

如果从 `stackoverflow`, `github`, `CSDN`上找到一些教程链接，可能是关于如何安装新项目或者修改配置的bash指令，那么就可以试试这个功能

```shell
➜  crpa -l https://github.com/danielmiessler/fabric
此网站的信息:  fabric: An open-source framework for augmenting humans using AI
环境需求: Ensure you have at least python3.10 installed on your operating system.
将执行以下指令:
* cd . 
* git clone https://github.com/danielmiessler/fabric.git
* cd fabric
* pipx install . # 因为有操作系统信息，所以这里会直接执行wsl命令
* fabric --help
Do you want to continue? (yes/no): # 你可以检验一下命令是否正确之后顺序执行
```

必须承认，现在LLM的能力还没有达到能够完美完成大量操作的地步。以下给出另一个调用方法。从教程中复制指令列，来缩小让`crpa`
自动执行的范围

```shell
➜  crpa -t <<EOF
{你想要贴入的教程，这样可以多行粘贴}
EOF
```

这里的自动化执行在很多时候都有一些小问题，比如你需要提前 `git clone` 文件，预先安装`docker`等等。祝你好运。

### 自然语言命令

在实现以上功能之后，这个工具可以实现进一步的功能——实现自然语言交互! 这确实是在设计之外的事情

#### Case 1

```shell
➜ crpa -i 查询当前端口占用
# after a sequence of analysis logs
程序执行成功
bash命令 sudo netstat -tuln
被修改的文件: []
执行结果:
Active Internet connections (only servers) Proto Recv-Q Send-Q Local Address           Foreign Address         State udp        0      0 127.0.0.1:323           0.0.0.0:* udp6       0      0 ::1:323                 :::*
```

其实也可以这样调用:

```shell
➜ 查询当前端口占用
# 一段报错
➜ crpa
# after a sequence of analysis logs
程序执行成功
bash命令 sudo netstat -tuln
被修改的文件: []
执行结果:
Active Internet connections (only servers) Proto Recv-Q Send-Q Local Address           Foreign Address         State udp        0      0 127.0.0.1:323           0.0.0.0:* udp6       0      0 ::1:323                 :::*
```

**这种是其实这样调用更好一些，毕竟你可以在里面加入空格**

#### Case 2

它实现的功能可以更加复杂(因为bash确实又很多很神奇的指令)

```shell
➜ crpa -i  抓取github trending 中的所有链接到log
# after a sequence of analysis logs
程序执行成功
bash命令 curl -s https://github.com/trending | grep -Eo '<a [^>]+>' | grep -Eo 'href="[^"]+"' | awk -F'"' '{print $2}' > log
被修改的文件: []
执行结果:
```

log 中的内容

```shell
#start-of-content
https://github.com/
https://github.com/features/actions
https://github.com/features/packages
https://github.com/features/security
https://github.com/features/codespaces
# 等等
```

#### Case 3

好像也可以产生一些可执行的文件?

```shell
➜  crpa -i 产生一个可以打印出 ASCII艺术字符格式的"CRPA" 的python脚本
bash命令 pip install pyfiglet; echo 'import pyfiglet'
print(pyfiglet.figlet_format("CRPA"))' > print_crpa.py && python3 print_crpa.py
被修改的文件: []
执行结果:
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple Requirement already satisfied: pyfiglet in python3.10/site-packages (1.0.2) ____ ____  ____   _ / ___|  _ \|  _ \ / \ | |   | |_) | |_) / _ \ | |___|  _ <|  __/ ___ \ \____|_| \_\_| /_/   \_\
```

产生了一个叫做`print_crpa.py`的脚本，帮你装好了库

```shell
import pyfiglet
print(pyfiglet.figlet_format("CRPA"))
```

于是它可以打印出最上方的艺术字

#### Case 4

Bash 中也是有与UI交互的指令，所以，它在执行一些操作时会有恍惚间有一种真正RPA的感觉
```shell
crpa -i 使用Edge打开百度主页
```
祝您玩得愉快，就在刚刚，它帮我解决了提交冲突，感谢这个工具，希望它也对你有用

## 额外说明
* 显然，这只是一个非常简陋的小项目，完全的桌面自动化是不可能只靠一下午时间摸鱼解决的，希望这个行为艺术可以为大家通向AGI打开一些思路。
* 目前不支持`cmd`，在`powershell`中的智能好像没有bash高，所以在windows上最好使用WSL
* 网页抓取使用了[jina-ai/reader](https://github.com/jina-ai/reader) 非常感谢
