import shutil


def get_lines_around(file_path, line_number, window=500, save_copy=True):
    """
    获取指定行号上下指定行数（默认500行）的文本内容，
    如果文件总行数不足以覆盖这么多行，则返回尽可能多的行。

    Args:
    - file_path: 文件的路径字符串
    - line_number: 要查看的中心行号（以1开始计数）
    - window: 上下探索的行数，默认500行
    - save_copy: 保留原始数据至少别别把人家的源文件覆盖了

    Returns:
    - 指定行号上下指定行数内的文本内容
    - 对应原始文件上，最开始的行数
    - 对应原始文件上，结束的行数
    """
    try:
        # 复制文件备份
        if save_copy:
            # 保证 .bak中的内容必须是要
            shutil.copy(file_path, file_path + ".bak")

        # 初始化文本列表
        lines = []
        stat = -1
        end = 0
        # 打开文件并提取内容
        with open(file_path, 'r', encoding='utf-8') as file:
            for i, line in enumerate(file, 1):

                if (line_number - window) <= i <= (line_number + window):
                    lines.append(line)
                    if stat < 0:
                        stat = i
                    end = i
        # 将列表中的文本合并为一个字符串返回
        return "".join(lines), stat, end

    except FileNotFoundError:
        return "Error: The file does not exist"
    except Exception as e:
        return f"Error: {str(e)}"


def recover_file(file_path):
    """
    在执行完全失败之后把文件恢复过去
    :param file_path:
    :return:
    """
    shutil.copy(file_path + ".bak", file_path)


def edit_file(file_path, start_line, end_line, new_content):
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as file:
        all_lines = file.readlines()

    # 替换指定行的内容
    all_lines[start_line - 1:end_line] = [new_content]

    # 将修改后的内容写会源文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(all_lines)


# 示例用法
if __name__ == "__main__":
    file_path = './rpa.py'
    # line = 3
    # text_around, stat_line, end_line = get_lines_around(file_path, line)
    # print(text_around, stat_line, end_line)
    recover_file(file_path)
