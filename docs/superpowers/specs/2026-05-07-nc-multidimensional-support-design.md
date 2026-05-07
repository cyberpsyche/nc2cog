# NC 多维文件支持设计

## 背景

当前 nc2cog 只能处理 2D 栅格 NC 文件（单个变量 `var(lat, lon)`）。对于包含时间维度和多个变量的 NC 文件（如 `PRE(time, lat, lon)`），GDAL 以子数据集方式存储，当前代码 `validate_input()` 中 `RasterCount == 0` 会直接报错。

## 目标输出

对于包含 10 时间步和 2 变量（PRE、REF）的 NC 文件：
```
input.nc → output/PRE.tif (10 bands, time 展平为波段)
         → output/REF.tif  (10 bands)
```

## 架构变更

- **新增** `src/nc2cog/analyzer.py` — 分析 NC 文件结构，提取变量、维度、子数据集信息
- **修改** `src/nc2cog/processor.py` — 增加子数据集处理路径，将时间步写入多波段
- **修改** `src/nc2cog/cli.py` — 添加 `--variables` CLI 参数，集成 analyzer

## analyzer.py 职责

1. `get_subdatasets()` — 返回子数据集路径列表，空列表表示 2D 模式
2. `analyze_subdataset(path)` — 返回维度名、形状、数据类型、变量名
3. `get_time_info(subdataset_path)` — 从 NC 属性读取时间坐标
4. 自动识别坐标变量（`lat`, `lon`, `time`, `crs`）并排除

## processor.py 变更

1. 新增 `convert_multiband()` 方法：处理单变量多维数据
2. 遍历时间维度，逐时间步读取为 numpy 数组
3. 写入临时多波段 GeoTIFF（`Create()` + `WriteRaster()`）
4. 设置波段描述为时间元数据
5. 保持现有的 COG 转换 + 金字塔构建流程不变

## CLI 变更

1. 新增 `--variables TEXT` 参数：指定要转换的变量名（逗号分隔）
2. 不指定时自动发现所有数据变量
3. 单文件输入模式下，输出路径判断规则不变（`single_file_mode` 逻辑兼容）

## 兼容性

| NC 结构 | 行为 |
|---------|------|
| 2D 单变量 | 原有流程不变 |
| 3D 单变量 | 子数据集 → 多波段 COG |
| 3D 多变量 | 每变量一个多波段 COG |
| 2D 多变量 | 每变量一个单波段 COG |
