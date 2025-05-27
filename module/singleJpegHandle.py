from pathlib import Path

from module.compositeNewImg import composite_Img_with_patchImg
from module.getHidePatchImg import extract_hidden_jpeg_from_file,extract_all_jpgs_from_bin_raw
from module.getJpgXmpInfo import get_xmp_info
from module.rotate_img import rotate_img_with_pillow
from module.logManager import setup_logger

logger = setup_logger()


def singleJpegFileHandle(filePath: Path, outDir: Path = None, outFileName: str = None) -> Path:
    """
处理单个 JPG 文件的水印，返回处理后生成的新图像文件路径。

Args:
    filePath (Path): 要处理的 JPG 文件路径。
    outDir (Path, optional): 输出目录，用于保存处理后的文件。
    outFilePath (Path, optional): 自定义输出文件路径（包括文件名）。
Returns:
    Path: 处理后图像文件的完整路径。
    :param filePath:
    :param outDir:
    :param outFileName:
"""

    tempDir = filePath.parent / f"temp"
    tempDir.mkdir(exist_ok=True)

    if outDir is None:
        outDir = filePath.parent / f"outDir"
        outDir.mkdir(exist_ok=True)

    if outFileName is None:
        outFileName = f'{filePath.stem}_fixed.jpg'

    # 1. 解析 XMP
    info = get_xmp_info(filePath)

    # 2. 拿 lenswatermark 信息
    lm = info.get('lenswatermark')
    if lm is None:
        logger.error(f"图片{filePath}未找到 lenswatermark 信息，无法贴回")
        raise RuntimeError(f"❌ 图片{filePath}未找到 lenswatermark 信息，无法贴回")

    # 3. 提取 subimage（这里依然用 subimage 区块存储的 JPEG）
    sub = info.get('subimage')
    if sub is None:
        logger.error(f"图片{filePath}未找到 subimage信息，无法贴回")
        raise RuntimeError("❌ 未找到 subimage 信息")
    depthmap = info.get('depthmap')
    print(f'depthmap_list:{depthmap}')
    #  是否是人像模式的照片，默认不是

    '''
    if depthmap is None:
        print(f'is_depthmap:{depthmap}')
        is_depthmap = False
    else:
        print(f'is_depthmap:{depthmap}')
        is_depthmap = True
        '''

    # raw = extract_hidden_jpeg_from_file(filePath, tempDir, is_depthmap)

    raw = extract_all_jpgs_from_bin_raw(filePath, tempDir)
    raw = raw[1]

    # 4. 根据xmp旋转角旋转补丁
    rot = rotate_img_with_pillow(raw, sub.get('rotation', 0), tempDir)

    # 5. 合成fixed的img
    composite_Img_with_patchImg(filePath, rot, lm, outDir / outFileName)

    # print(f"🎉 {filePath}fix执行完毕，临时文件保存在", tempDir)
    return outDir / outFileName
