from pathlib import Path
from PIL import Image
from module.logManager import setup_logger

logger = setup_logger()


def rotate_img_with_pillow(input_patch_jpg: Path, rotation, temp_dir: Path):
    """
    使用 Pillow 实现旋转操作，并输出 PNG 图像。
    rotation: 应为 90, 180, 270，表示顺时针旋转角度。
    这里的rotation不应该由用户自定义，应该由源文件的xmp读取
    """
    # Pillow为逆时针旋转，转换角度适配Pillow
    angle_map = {
        '90': -90,
        '180': -180,
        '270': -270,
        '-1': 0
    }
    if str(rotation) not in angle_map:
        raise ValueError("图片旋转角度rotation 必须是 90, 180, 270 中的一个数，且默认不许自定义")

    angle = angle_map[str(rotation)]


    output_path = temp_dir / f'{input_patch_jpg.stem}_hidden_roted.png'

    # print(f"🌀 使用 Pillow 旋转 {angle}°：{input_path}")
    image = Image.open(input_patch_jpg).convert("RGB")
    rotated = image.rotate(angle, expand=True)
    rotated.save(output_path)
    logger.info(f'输出旋转后的补丁文件：{str(output_path)}')
    logger.info(f"✅ 旋转后文件：{output_path}")
    return output_path
