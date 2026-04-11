# nc2cog 项目结构说明

## 目录结构

```
nc2cog/
├── .gitignore                 # Git忽略文件配置
├── README.md                  # 项目主文档
├── CHANGELOG.md              # 项目变更日志
├── INSTALLATION.md           # 安装说明
├── USAGE_EXAMPLE.md          # 使用示例
├── requirements.txt          # Python依赖
├── setup.py                  # 包配置
├── .claude/                  # Claude Code配置
├── config/                   # 配置文件目录
│   └── default_config.yaml   # 默认配置文件
├── docs/                     # 文档目录
│   ├── user_guide.md         # 用户指南
│   ├── gdal_optimization.md  # GDAL优化说明
│   ├── examples.md          # 使用示例
│   ├── configuration_guide.md # 配置指南 (原)
│   ├── troubleshooting.md     # 故障排除 (原)
│   └── user_manual.md        # 用户手册 (原)
├── src/                      # 源代码目录
│   └── nc2cog/               # 主要组件
│       ├── __init__.py       # 包初始化
│       ├── __version__.py    # 版本信息
│       ├── cli.py            # 命令行接口
│       ├── processor.py      # 核心处理引擎
│       ├── config.py         # 配置管理
│       ├── discovery.py      # 文件发现
│       ├── logger.py         # 日志系统
│       └── errors.py         # 错误处理
├── tests/                    # 测试目录
│   ├── test_config.py        # 配置测试
│   ├── test_discovery.py     # 发现功能测试
│   ├── test_cli_params.py    # CLI参数测试
│   ├── test_extended_cli.py  # 扩展CLI测试
│   └── ...                   # 其他测试文件
└── test_gdal_handling.py     # GDAL处理测试
```

## 功能模块说明

### 主要组件

1. **CLI接口** (`src/nc2cog/cli.py`)
   - 命令行参数处理
   - 参数验证和默认值设置
   - 配置参数覆盖逻辑

2. **处理引擎** (`src/nc2cog/processor.py`)
   - netCDF到COG转换核心逻辑
   - GDAL参数优化
   - 概览（金字塔）生成
   - 错误处理和日志记录

3. **配置管理** (`src/nc2cog/config.py`)
   - YAML配置文件处理
   - 参数验证和合并
   - 默认值管理

### 文档说明

1. **主要文档**:
   - `README.md`: 项目概览和快速入门
   - `docs/user_guide.md`: 详细用户指南
   - `docs/gdal_optimization.md`: GDAL优化技术细节
   - `docs/examples.md`: 使用示例集合

2. **辅助文档**:
   - `USAGE_EXAMPLE.md`: 原始使用示例
   - `docs/configuration_guide.md`: 原始配置指南
   - `docs/user_manual.md`: 原始用户手册
   - `docs/troubleshooting.md`: 原始故障排除

## 特色功能

### 1. GDAL优化
- 为不同驱动使用兼容参数（GTiff vs COG）
- 消除GDAL警告信息
- 优化概览生成流程

### 2. 参数控制
- `--zlevel`: 压缩级别控制
- `--overview-levels`: 概览层级自定义
- `--resampling`: 重采样方法选择
- 性能相关参数（tile-size, block-size等）

### 3. 批量处理
- 目录递归处理
- 多线程支持
- 断点续传功能

## 开发说明

### 主要改进
1. GDAL参数优化消除警告
2. 新增概览层级控制参数
3. 改进的错误处理机制
4. 更好的配置管理

### 代码规范
- 使用Python类型提示
- 遵循PEP 8编码规范
- 完整的文档字符串
- 单元测试覆盖

## 使用建议

参见 `docs/examples.md` 获取不同场景的最佳实践。