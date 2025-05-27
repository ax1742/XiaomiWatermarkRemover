from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile
from pathlib import Path
from module.logManager import setup_logger

logger = setup_logger()


def get_jpg_quantization(orgJpgPath: Path):
    orig2 = Image.open(orgJpgPath)
    orig2.load()  # 确保插件初始化

    # 方案 A：检查实例类型
    if isinstance(orig2, JpegImageFile) and hasattr(orig2, 'quantization'):
        q_tables = orig2.quantization
        logger.info(f'ℹ️ 源图片{orgJpgPath}:quantization信息:{q_tables}，方案1拿到。')
    else:
        # 方案 B：从 encoderinfo / info 字典中找
        q_tables = orig2.encoderinfo.get('qtables') or orig2.info.get('quantization')
        logger.info(f'ℹ️ 源图片{orgJpgPath}:quantization信息:{q_tables}，方案1拿到。')

    if not q_tables:
        logger.error("无法获取量化表；请确认这是 JPEG 文件，图片最后会以png未压缩格式保存。")
        raise RuntimeError("无法获取量化表；请确认这是 JPEG 文件，图片最后会以png未压缩格式保存。")

    #  print("ℹ️ 量化表 ID 列表：", list(q_tables.keys()))

    orig2.close()  # 关闭读取
    #  dict -> list
    q_tables_list = [q_tables[i] for i in sorted(q_tables.keys())]
    return q_tables_list
