from pathlib import Path

from module.logManager import setup_logger

logger = setup_logger()


def get_jpg_files_list(path: Path, recursive=False) -> list:
    """查找指定路径下的 .jpg 文件"""

    logger.info(f"开始查找路径：{path} | 递归查找？：{recursive}")

    if not path.exists():
        logger.error(f"路径不存在：{path}")
        return []  # 空列表

    if recursive:
        files = list(path.rglob("*.jpg"))
    else:
        files = list(path.glob("*.jpg"))

    files = [p for p in files if p.suffix.lower() == ".jpg"]

    if files:
        logger.info(f'{path}里共找到{len(files)}个JPEG文件')
    else:
        logger.error(f'{path}里不存在JPEG文件！')

    return files

    # logging.info(f"查找完成，共找到 {len(result)} 个 .jpg 文件")
