import argparse
import os
import subprocess
from conflict_rpa.config import read_all_config, init_config
from conflict_rpa.environment_setting import environment_setting


def rpa():
    openai_config = read_all_config()
    if openai_config is None:
        environment_setting()
        print('环境设置完成')
        print('需要初始化OPENAI配置')
        init_config()
        print('配置完成，`source ~/.bashrc`或重启后可执行`crpa`操作')
        return
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--link', type=str, help="提供链接进行自动化操作", default=None)
    parser.add_argument('-t', '--tutorial', type=str, help="希望自动化操作的流程文本，不需要整理地很好", default=None)
    parser.add_argument('-i', '--instruct', type=str, help="想要RPA的指令或者自然语言", default=None)
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode (sets DEBUG to True)')
    parser.add_argument('command',
                        nargs='*',
                        help='上一条执行的指令，用户莫动')
    args = parser.parse_args()
    openai_config = read_all_config()
    if openai_config is None:
        print('需要初始化OPENAI配置')
        init_config()
        return
    else:
        OPENAI_API_KEY = openai_config["OPENAI_API_KEY"]
        OPENAI_API_BASE = openai_config["OPENAI_API_BASE"]
        os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
        if len(OPENAI_API_BASE):
            os.environ['OPENAI_API_BASE'] = OPENAI_API_BASE
    debug = args.verbose
    from conflict_rpa.content_rpa import content_rpa
    from conflict_rpa.correcting_framework import main_loop
    from conflict_rpa.link_rpa import link_rpa
    if args.link:
        print(f"正在处理链接: {args.link}")
        # 在这里添加处理链接的代码
        link_rpa(args.link,debug)
    elif args.tutorial:
        print(f"正在处理文本: {args.tutorial}")
        # 在这里添加处理链接的代码
        content_rpa(args.tutorial,debug)
    elif args.instruct:
        print(f"运行指令 {args.instruct}")
        script = ''.join(args.instruct).replace('\t', '')
        main_loop(script,verbose=debug)
    else:
        if len(args.command) == 1:
            history_cmd = args.command[0]
        elif len(args.command) > 1:
            history_cmd = ''.join(args.command[1:])
        else:
            print('没有可执行的指令')
            return
        print(f"运行指令 {history_cmd}")
        script = ''.join(history_cmd).replace('\t', '')
        main_loop(script,verbose=debug)
