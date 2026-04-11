#!/usr/bin/env python3
"""
演示nc2cog中概览层级（金字塔结构）控制功能
"""

from src.nc2cog.cli import main
import click
import tempfile
import os

def test_overview_levels_param():
    """测试新的概览层级参数功能"""
    print("=== nc2cog 概览层级（金字塔结构）控制功能 ===\n")

    print("新添加的参数：")
    print("  --overview-levels: 控制金字塔层级结构，逗号分隔（默认: 2,4,8,16）")
    print()

    print("使用示例：")
    print("# 使用默认概览层级 (2,4,8,16)")
    print("nc2cog input.nc output/")
    print()

    print("# 自定义概览层级")
    print("nc2cog input.nc output/ --overview-levels 2,4,8,16,32")
    print()

    print("# 结合其他参数使用")
    print("nc2cog input.nc output/ --resampling cubic --overview-levels 2,4,8")
    print()

    print("# 高级使用示例")
    print("nc2cog input.nc output/ --compression deflate --zlevel 9 --tile-size 1024 --overview-levels 2,4,8,16,32,64")
    print()

    print("功能说明：")
    print("- 概览层级控制COG文件中金字塔结构的分辨率层级")
    print("- 层级数值表示缩小倍数 (例如: 2表示分辨率减半，4表示缩小至1/4)")
    print("- 更多层级 = 更好的多尺度浏览体验，但文件稍大")
    print("- 较少层级 = 更小的文件，但多尺度浏览体验有限")
    print()

    print("推荐设置：")
    print("- 科学数据 (高精度)：--overview-levels 2,4,8,16,32,64")
    print("- 一般用途：--overview-levels 2,4,8,16 (默认)")
    print("- 快速浏览：--overview-levels 2,4,8")
    print()

def show_available_params():
    """显示所有可用参数"""
    ctx = click.Context(main)
    params = [param.name for param in ctx.command.params if hasattr(param, 'name')]

    print("当前所有可用参数：")
    for param in sorted(params):
        print(f"  --{param.replace('_', '-')}")
    print()

if __name__ == "__main__":
    test_overview_levels_param()
    show_available_params()
    print("注意：要生成带有金字塔结构的COG文件，")
    print("只需在命令中加入 --overview-levels 参数指定所需的层级即可。")
    print("例如: nc2cog input.nc output/ --overview-levels 2,4,8,16,32")