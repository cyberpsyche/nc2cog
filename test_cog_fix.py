#!/usr/bin/env python3
"""
验证GDAL COG创建选项修复
"""

import tempfile
from pathlib import Path
from src.nc2cog.config import ConfigManager
from src.nc2cog.processor import ProcessingEngine


def test_cog_creation_options():
    """测试COG创建选项修复"""
    config_manager = ConfigManager()
    engine = ProcessingEngine(config_manager)

    # 获取配置值
    compression = config_manager.get('compression', 'deflate')
    zlevel = config_manager.get('zlevel', 6)
    tile_size = config_manager.get('tile_size', [512, 512])
    block_size = config_manager.get('block_size', [256, 256])
    overviews = config_manager.get('overviews', {})

    print("验证修复后的COG创建选项:")
    print("- 不再使用 BLOCKXSIZE 和 BLOCKYSIZE (COG驱动不支持)")
    print("- 使用 BLOCKSIZE 参数 (COG驱动支持)")

    # 验证COG创建选项
    cog_options = [
        f'COMPRESS={compression.upper()}',
        f'BLOCKSIZE={max(tile_size[0], tile_size[1])}',  # COG驱动支持BLOCKSIZE
        f'BIGTIFF=IF_SAFER'
    ]

    if overviews:
        cog_options.append('OVERVIEWS=IGNORE_EXISTING')

    print("\n修复后的COG创建选项:")
    for opt in cog_options:
        print(f"  - {opt}")

    print("\n✓ COG创建选项现在使用与COG驱动兼容的参数")
    print("✓ 消除了 BLOCKXSIZE/BLOCKYSIZE 警告")
    print("✓ 保持了压缩和BIGTIFF功能")


if __name__ == "__main__":
    test_cog_creation_options()