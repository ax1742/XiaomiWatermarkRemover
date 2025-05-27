from pathlib import Path
from PIL import Image
from module.getJpegImgQuantization import get_jpg_quantization
from module.logManager import setup_logger

logger = setup_logger()


def composite_Img_with_patchImg(orig_path: Path, patch_path: Path, xmp: dict, output_path: Path):
    """
    使用 原图的xmp中lenswatermark的padding信息 (左下角原点) → PIL 左上角原点 坐标转换后，覆盖去并保存图像。
    """
    orgImg2RGB = Image.open(orig_path).convert("RGB")
    patchImg2RGB = Image.open(patch_path).convert("RGB")

    W_orgImg2RGB, H_orgImg2RGB = orgImg2RGB.size  # 原图图片的宽高缩写，以下同理
    W_patchImg2RGB, H_patchImg2RGB = patchImg2RGB.size

    x = xmp['paddingx'] - 1  # 这里减去一个像素点。实现完美贴合。鬼知道为什么小米自己关闭水印也会偏移1像素点。
    y = H_orgImg2RGB - xmp['paddingy'] - H_patchImg2RGB  # 左下原点 -> 左上原点
    logger.info(f'源文件：{orig_path}，尺寸{W_orgImg2RGB}×{H_orgImg2RGB}')
    logger.info(f'源文件：{patch_path}，尺寸{W_patchImg2RGB}×{H_patchImg2RGB}')

    logger.info(f'📌 patchImg贴回 到坐标(PIL 坐标)：x={x}, y={y}')

    orgImg2RGB.paste(patchImg2RGB, (x, y))
    # output_path = Path(output_path).with_suffix(".png")  # 确保输出为 PNG
    # orgImg2RGB.save(output_path, format="PNG")

    #  默认以小米未去水印前的原图的量化表输出为jpg文件
    q_tables_list = get_jpg_quantization(orig_path)  # 拿到原图量化表

    if q_tables_list is not None:
        output_path = Path(output_path).with_suffix(".jpg")  # 确保输出为 jpg
        orgImg2RGB.save(
            output_path,
            format="JPEG",
            qtables=q_tables_list
        )
    else:
        output_path = Path(output_path).with_suffix(".png")  # 确保输出为 jpg
        orgImg2RGB.save(
            output_path,
            format="PNG",
            subsampling="keep",  # 保持原子采样
        )
        #  这里应该判断下
    # print(f"✅ 成功保存去水印图像：{output_path}")
    logger.info(f'✅ 成功保存去水印图像：{output_path}')
