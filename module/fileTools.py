from pathlib import Path
import sys
from module.logManager import setup_logger

logger = setup_logger()


def check_path(path: Path) -> str:

    if path.is_file():

        logger.info(f'传入path：{path},合法，属性:file，文件')
        return "isFile"
    elif path.is_dir():
        logger.info(f'传入path：{path},合法，属性:dir，文件夹')
        return "isDir"
    else:
        logger.warn(f'传入path：{path}路径无效！')
        print(f"❌ 路径无效{path}")
        sys.exit(1)  # 退出程序，返回状态码 1
