from pathlib import Path

from PIL import Image

from module.logManager import setup_logger

logger = setup_logger()


def extract_hidden_jpeg_from_file(filepath: Path, temp_dir: Path):
    """
    扫描 原始图片中隐藏的图片字节，找到最后一段JPEG 数据，
    根据传入的temp_dir目录
    保存到 temp_dir/hidden_raw.jpg，返回该 Path。
    """

    data = filepath.read_bytes()
    # 找到所有 FFD8 起始
    starts = [i for i in range(len(data) - 1) if data[i] == 0xFF and data[i + 1] == 0xD8]
    if not starts:
        logger.warn(f"{filepath}文件中未找到任何 JPEG 起始标志 FFD8")
        raise ValueError("❌ 未找到任何 JPEG 起始标志 FFD8")

    last_start = starts[-1]  # 找到最后一段被隐藏的jpg数据，即：补丁图。
    end = data.find(b'\xFF\xD9', last_start)
    if end == -1:
        logger.warn(f"{filepath}文件中未找到与最后一个 FFD8 对应的 FFD9,尝试使用第二个")
        raise ValueError("❌ 未找到与最后一个 FFD8 对应的 FFD9")

    # 如果原图是人像模式，则提取第二个隐藏的jpg
    # if is_depthmap:
    #     if len(starts) < 2:
    #         raise ValueError("❌ 人像模式要求至少存在两个 JPEG 起始段，但未满足。")
    #     second_start = starts[2]
    #     second_end = data.find(b'\xFF\xD9', second_start)
    #     if second_end == -1:
    #         logger.warn(f"{filepath}文件中未找到第二段 JPEG 的结束标志 FFD9")
    #         raise ValueError("❌ 未找到第二段 JPEG 的结束标志 FFD9")
    #     jpeg_bytes = data[second_start:second_end + 2]
    #     print('人像模式图片')
    # else:
    #     jpeg_bytes = data[last_start:end + 2]
    #     print("非人像图")
    jpeg_bytes = data[last_start:end + 2]
    temp_raw = temp_dir / f'{filepath.stem}_hidden.jpg'  # 提取到的jpg补丁文件保存到tmp_dir下
    logger.info(f'成功提取到补丁文件：{str(temp_raw)}')
    temp_raw.write_bytes(jpeg_bytes)
    # print(f"✅ 从原图提取到最后补丁JPEG：slice[{last_start}:{end + 2}] → {temp_raw}")
    return temp_raw


def is_image_valid(path: Path):
    try:
        with Image.open(path) as img:
            img.verify()
        with Image.open(path) as img:
            img.load()
        return True
    except Exception as e:
        # print(f"⚠️ 图片非法或损坏: {e}")
        logger.warn('f"⚠️ 图片非法或损坏: {e}"')
        return False


def extract_all_jpgs_from_bin_raw(filepath: Path, temp_dir: Path) -> list[Path]:
    """
    使用原生 Python 库从二进制文件中提取所有 JPEG 图像（以 0xFFD8 开始，0xFFD9 结束）并保存为 .jpg 文件。
    返回所有合法 JPEG 路径组成的列表。
    """
    data = filepath.read_bytes()
    jpg_paths = []
    jpg_count = 0
    pos = 0
    length = len(data)

    temp_dir.mkdir(parents=True, exist_ok=True)

    while pos < length - 1:
        if data[pos] == 0xFF and data[pos + 1] == 0xD8:
            start = pos
            end = data.find(b'\xFF\xD9', start)
            if end == -1:
                # print(f"⚠️ 找到起始但未找到结束标志（FFD9），跳过")
                pos += 2
                continue
            end += 2  # 包含 FFD9

            jpg_data = data[start:end]
            output_file = temp_dir / f"{filepath.stem}_raw_extracted_{jpg_count + 1}.jpg"

            try:
                with open(output_file, "wb") as f_out:
                    f_out.write(jpg_data)

                if is_image_valid(output_file):
                    # print(f"✅ 提取 JPEG #{jpg_count + 1}（偏移 {start} - {end}）: {output_file.name}")
                    jpg_paths.append(output_file)
                    jpg_count += 1
                else:
                    # print(f"⚠️ 跳过非法图像 {output_file.name}")
                    output_file.unlink(missing_ok=True)

            except Exception as e:
                # print(f"❌ 保存 JPEG 失败: {e}")
                logger.error(f'❌ 保存 JPEG 失败: {e}')

            pos = start + 2  # 改成从下一个起点继续扫描，而不是跳到 `end`
        else:
            pos += 1

    # print(f"🎉 提取完成，共 {jpg_count} 张合法 JPEG 图像")
    return jpg_paths
