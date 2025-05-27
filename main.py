import argparse
import multiprocessing
from pathlib import Path
from module.logManager import setup_logger
from module.singleJpegHandle import singleJpegFileHandle
from module.jpg_finder import get_jpg_files_list
from module.multiJpegHandle import batchJpegFilesHandle


def main():
    parser = argparse.ArgumentParser(
        description='v1.0 去除小米相机机型水印 ——by大美格里尔斯 '
    )
    parser.add_argument(
        '-p', '--path', required=True,
        help='带水印的原始 JPG 单文件文件路径,如果传入文件夹就自动扫描文件夹内所有jpg文件并处理'
    )
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='启用调试模式（打印日志到控制台）')  # 默认 False，加了 -d 就变 True

    parser.add_argument('-t', "--threads",
                        help='处理文件时的线程数，默认线程数为cpu支持的最大线程数-2，可以手动指定数')
    args = parser.parse_args()

    logger = setup_logger(to_console=args.debug)
    logger.info("启动程序，初始化logger...........")
    cpu_threads = int(multiprocessing.cpu_count())  # 通常是逻辑线程数

    logger.info(f'该机器支持最大逻辑线程数：{cpu_threads},默认将使用{cpu_threads - 2}数线程')

    max_cpu_workers = max(1, cpu_threads - 2)

    args = parser.parse_args()

    orig = Path(args.path)  # 接受参数中的path参数 str->path对象
    """
        判断路径是文件夹还是文件。
        文件进入单文件处理流
        文件夹进入文件夹循环处理

        """
    if orig.is_dir():
        jpgFilesList = get_jpg_files_list(orig)
        if jpgFilesList:
            logger.info(f"找到{len(jpgFilesList)}个文件。")
            # print(len(jpgFilesList))
            # print(jpgFilesList)
            logger.info(f"开始多处理任务....")
            batchJpegFilesHandle(max_cpu_workers, jpgFilesList)  # 处理多个jpg文件

            #  这里传入一个包含所有jpg文件的list，然后处理
    elif orig.is_file() and orig.suffix.lower() in {'.jpg', '.jpeg'}:
        singleJpegFileHandle(orig)


if __name__ == "__main__":
    main()
