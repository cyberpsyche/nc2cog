# 投影转换功能使用说明

## 概述

nc2cog 现在支持在 netCDF 到 COG 转换过程中进行坐标系重投影。您可以使用 `--src-proj` 和 `--dst-proj` 参数指定源投影和目标投影。

## 参数说明

### `--src-proj`
- **类型**: 字符串
- **格式**: EPSG 代码（例如 `EPSG:4326`）
- **说明**: 源投影定义（可选）。如果未指定，系统将尝试从输入文件中自动检测投影信息。

### `--dst-proj`
- **类型**: 字符串
- **格式**: EPSG 代码（例如 `EPSG:3857`）
- **说明**: 目标投影定义（必需，当需要重投影时）。

## 使用示例

### 基本重投影转换
```bash
# 将数据从原始投影转换到 Web Mercator 投影
nc2cog --dst-proj EPSG:3857 input.nc output/
```

### 指定源和目标投影
```bash
# 明确指定源投影和目标投影
nc2cog --src-proj EPSG:4326 --dst-proj EPSG:3857 input.nc output/
```

### 结合其他参数使用
```bash
# 在重投影的同时使用其他转换选项
nc2cog --src-proj EPSG:4326 --dst-proj EPSG:3857 \
       --compression deflate --zlevel 9 \
       --tile-size 1024 input.nc output/
```

### 干运行测试
```bash
# 测试重投影转换但不实际执行
nc2cog --dst-proj EPSG:3857 --dry-run input.nc output/
```

## 注意事项

1. **EPSG 代码**: 目前仅支持 EPSG 代码格式的投影定义。
2. **自动检测**: 如果未指定 `--src-proj`，系统会尝试从输入 netCDF 文件中自动检测源投影。
3. **重采样**: 重投影过程使用 nearest neighbor 重采样方法，这可以通过配置系统进一步定制。
4. **性能**: 重投影操作可能显著增加处理时间，特别是对于高分辨率数据。