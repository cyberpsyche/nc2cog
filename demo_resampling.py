#!/usr/bin/env python3
"""
演示nc2cog中概览重采样方法控制功能
"""

from src.nc2cog.cli import main
import click

def test_resampling_param():
    """测试重采样参数功能"""
    print("=== nc2cog 概览重采样方法控制功能 ===\n")

    print("当前参数名称：")
    print("  --resampling: 控制概览生成的重采样方法（默认: nearest）")
    print()

    print("可用的重采样方法：")
    methods = ['nearest', 'bilinear', 'cubic', 'average', 'mode', 'gauss', 'rms']
    descriptions = {
        'nearest': '最邻近法 - 速度快，适合分类数据',
        'bilinear': '双线性插值 - 平衡质量和速度',
        'cubic': '三次卷积 - 高质量，适合连续数据',
        'average': '平均法 - 适合降采样统计',
        'mode': '众数法 - 适合分类数据',
        'gauss': '高斯重采样 - 平滑效果好',
        'rms': '均方根重采样 - 适合特殊分析'
    }

    for method in methods:
        print(f"  {method:10s} - {descriptions[method]}")
    print()

    print("使用示例：")
    print("# 使用默认重采样方法 (nearest)")
    print("nc2cog input.nc output/")
    print()

    print("# 高质量重采样（适合连续数据）")
    print("nc2cog input.nc output/ --resampling cubic")
    print()

    print("# 平衡质量和速度")
    print("nc2cog input.nc output/ --resampling bilinear")
    print()

    print("# 快速处理（适合分类数据）")
    print("nc2cog input.nc output/ --resampling nearest")
    print()

    print("# 统计降采样")
    print("nc2cog input.nc output/ --resampling average")
    print()

    print("# 结合概览层级参数使用")
    print("nc2cog input.nc output/ --resampling cubic --overview-levels 2,4,8,16,32")
    print()

    print("# 高级使用示例")
    print("nc2cog input.nc output/ --compression deflate --zlevel 9 --tile-size 1024 --resampling cubic --overview-levels 2,4,8,16,32,64")
    print()

    print("功能说明：")
    print("- 重采样方法影响概览（金字塔层级）的质量")
    print("- 对于连续数据（如温度、高度）推荐使用 cubic 或 bilinear")
    print("- 对于分类数据（如土地利用类型）推荐使用 nearest 或 mode")
    print("- average 适合需要统计意义的降采样")
    print()

    print("推荐搭配：")
    print("- 连续数据：--resampling cubic --overview-levels 2,4,8,16,32")
    print("- 分类数据：--resampling nearest --overview-levels 2,4,8,16")
    print("- 通用场景：--resampling bilinear --overview-levels 2,4,8,16")

if __name__ == "__main__":
    test_resampling_param()
    print("\n注意：要生成具有特定重采样方法的概览金字塔，")
    print("只需在命令中加入 --resampling 参数指定所需的方法即可。")
    print("例如: nc2cog input.nc output/ --resampling cubic --overview-levels 2,4,8,16,32")