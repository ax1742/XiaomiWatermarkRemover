import multiprocessing
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

from tqdm import tqdm

from module.logManager import setup_logger
# 单文件处理函数需支持被多进程调用（建议放在模块最顶层）
from module.singleJpegHandle import singleJpegFileHandle

logger = setup_logger()

cpu_threads = multiprocessing.cpu_count()  # 通常是逻辑线程数
max_cpu_workers = max(1, cpu_threads - 2)


def _process_one(filePath: Path, outDir: Optional[Path]) -> Optional[Path]:
    try:
        return singleJpegFileHandle(filePath, outDir)
    except Exception as e:
        logger.error(f"❌ 处理文件 {filePath} 时出错: {e}\n{traceback.format_exc()}")
        return None


def batchJpegFilesHandle(max_workers: int, fileList: List[Path], outDir: Optional[Path] = None) -> List[Path]:
    """
    批量处理多个 JPG 文件，支持多进程和进度条。

    Args:
        fileList (List[Path]): 要处理的文件列表。
        outDir (Optional[Path]): 输出目录。
        max_workers (int): 并发进程数量，默认 4。

    Returns:
        List[Path]: 成功处理的文件路径列表。
    """
    output_paths = []
    failed_files = []

    print(f"开始批量处理，共 {len(fileList)} 个文件，使用 {max_workers} 个进程")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_process_one, file, outDir): file
            for file in fileList
        }

        # tqdm 正确绑定 as_completed，并设置稳定宽度（避免滚屏）
        for future in tqdm(as_completed(futures), total=len(futures), desc="批量处理进度", ncols=100):
            file = futures[future]
            try:
                result = future.result()
                if result:
                    logger.info(f"✅ 文件处理成功: {file}")
                    output_paths.append(result)
                else:
                    logger.warning(f"⚠️ 文件处理失败（无结果）: {file}")
                    failed_files.append(file)
            except Exception as e:
                logger.error(f"❌ 文件处理异常: {file}，错误信息: {e}")
                failed_files.append(file)

    print(f"批量处理完成，成功处理 {len(output_paths)} 个文件，失败 {len(failed_files)} 个")
    if failed_files:
        print(f"失败文件列表：{failed_files}")

    return output_paths



