import html
import re
from pathlib import Path
from xml.etree import ElementTree as Et
from module.logManager import setup_logger

logger = setup_logger()


def get_xmp_info(filepath):
    """
    解析 JPEG 中的 MiCamera:XMPMeta，返回 subimage / lenswatermark / timewatermark 属性字典。
    同时打印子标签列表以便调试。
    """
    logger.info(f"🔍 读取文件：{filepath}")
    data = Path(filepath).read_bytes()

    # 抽出 XMPMeta 属性值
    m = re.search(rb'MiCamera:XMPMeta="(.*?)"', data, flags=re.DOTALL)
    if not m:
        raise ValueError("❌ 未找到 MiCamera:XMPMeta 属性")
    raw = m.group(1)

    # 解码 HTML 实体 & 移除 XML 声明
    decoded = html.unescape(raw.decode('utf-8', errors='ignore'))
    decoded = re.sub(r'<\?xml.*?\?>', '', decoded, flags=re.DOTALL).strip()

    # 包一层 <root> 解析
    wrapped = f"<root>\n{decoded}\n</root>"

    root = Et.fromstring(wrapped)

    # 打印所有直接子标签，帮助调试
    tags = [child.tag for child in root]
    # print(f"ℹ️ XMP 子标签: {tags}")

    info = {}
    for tag in ('depthmap', 'subimage', 'lenswatermark', 'timewatermark'):
        el = root.find(tag)
        if el is None:
            # print(f"⚠️ 未找到 `{tag}` 标签")
            continue

        parsed = {}
        for k, v in el.attrib.items():
            vl = v.lower()
            if v.isdigit():
                parsed[k] = int(v)
            elif vl in ('true', 'false'):
                parsed[k] = (vl == 'true')
            else:
                parsed[k] = v
        info[tag] = parsed
    # print(f"✅ `{tag}` 属性：{parsed}")

    return info
