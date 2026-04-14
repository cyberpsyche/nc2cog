# 投影参数功能设计文档

## 1. 概述

### 1.1 背景
nc2cog 是一个将 netCDF 文件转换为云优化 GeoTIFF（COG）格式的工具。当前版本缺少在转换过程中进行坐标系重投影的功能，这限制了其在不同地理信息系统间的互操作性。

### 1.2 目标
为 nc2cog 添加投影转换功能，使用户能够在 netCDF 到 COG 的转换过程中执行坐标系重投影。

### 1.3 需求
- 支持在转换时将数据从源投影重投影到目标投影
- 使用 EPSG 代码作为投影输入格式
- 提供完整的数据重投影功能（包括重采样和坐标变换）
- 与现有 CLI 系统兼容

## 2. 功能规格

### 2.1 CLI 参数扩展
添加以下新参数：

#### `--src-proj`（可选）
- 描述：源投影定义（如果未指定，则尝试从输入文件自动检测）
- 格式：EPSG 代码（例如 `EPSG:4326`）
- 示例：`--src-proj EPSG:4326`

#### `--dst-proj`（必需，当启用重投影时）
- 描述：目标投影定义
- 格式：EPSG 代码（例如 `EPSG:3857`）
- 示例：`--dst-proj EPSG:3857`

## 3. 架构设计

### 3.1 组件修改
#### 3.1.1 CLI (`src/nc2cog/cli.py`)
- 添加 `--src-proj` 和 `--dst-proj` 参数定义
- 在配置管理器中设置投影参数
- 验证投影参数的一致性

#### 3.1.2 处理引擎 (`src/nc2cog/processor.py`)
- 修改 `convert_file` 方法以支持重投影
- 实现 GDAL 的坐标变换逻辑
- 确保与现有压缩和分块选项的兼容性

### 3.2 数据流
1. 用户通过 CLI 提供投影参数
2. CLI 解析并验证投影参数
3. 处理引擎检测是否需要重投影
4. 如果需要重投影，则使用 GDAL 的 `Warp` 函数执行坐标变换
5. 之后按正常流程生成 COG 文件

## 4. 实现细节

### 4.1 GDAL 集成
使用 GDAL 的 `gdal.Warp()` 函数来执行投影转换：

```python
# 伪代码示例
if src_proj and dst_proj:
    warped_dataset = gdal.Warp(
        destNameOrDestDS=temp_output,
        srcDS=input_dataset,
        srcSRS=src_proj,
        dstSRS=dst_proj,
        resampleAlg=resampling_method,
        creationOptions=creation_options
    )
```

### 4.2 与现有流程集成
- 重投影作为转换流程中的第一个步骤
- 确保重投影后仍能应用现有的压缩、分块和概览图生成设置
- 保持与 `--overwrite`、`--dry-run` 等现有选项的兼容性

### 4.3 错误处理
- 投影定义无效时抛出 `ValidationError`
- 重投影失败时记录错误并根据 `skip_errors` 设置决定是否继续
- 保留现有的错误处理机制

## 5. 测试策略

### 5.1 单元测试
- 测试 CLI 参数解析
- 测试处理引擎的重投影功能

### 5.2 集成测试
- 端到端重投影转换测试
- 不同 EPSG 代码组合的测试
- 与现有功能的兼容性测试

## 6. 用户体验

### 6.1 命令行示例
```bash
# 基本重投影转换
nc2cog --dst-proj EPSG:3857 input.nc output/

# 完整的源和目标投影指定
nc2cog --src-proj EPSG:4326 --dst-proj EPSG:3857 input.nc output/

# 高级重投影带重采样
nc2cog --src-proj EPSG:4326 --dst-proj EPSG:3857 --resampling cubic input.nc output/
```

## 7. 向后兼容性
- 新参数是可选的，不会破坏现有功能
- 现有的转换流程保持不变
- 所有现有 CLI 选项继续工作

## 8. 性能考虑
- 重投影可能会显著增加处理时间，特别是在高分辨率数据上
- 应该提供适当的进度指示和性能优化选项
- 考虑内存使用情况，因为重投影可能需要额外的临时空间