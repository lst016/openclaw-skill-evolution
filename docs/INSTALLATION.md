# Installation Guide / 安装指南

## English

### Prerequisites / 系统要求

- Python 3.12+
- Docker
- Git
- Qdrant (local Docker container)

### Quick Install / 快速安装

#### 1. Clone Repository / 克隆仓库
```bash
git clone https://github.com/lst016/openclaw-skill-evolution.git
cd openclaw-skill-evolution
```

#### 2. Setup Virtual Environment / 设置虚拟环境
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Start Qdrant / 启动 Qdrant
```bash
# Start Qdrant container with a specific name
docker run -d --name openclaw-skill-evolution-qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  qdrant/qdrant:latest

# Verify Qdrant is running
curl http://localhost:6333
```

#### 4. Initialize Collections / 初始化集合
```bash
# Create Qdrant collections
python scripts/qdrant_setup.py
```

#### 5. Run Integration Tests / 运行集成测试
```bash
# Test v3 integration (current version)
python scripts/v3_integration_test.py
```

### Requirements / 依赖包

#### Python Dependencies
- `qdrant-client` >= 1.7.0
- `pyyaml` >= 6.0
- `httpx` >= 0.24.0

#### System Dependencies  
- Docker >= 20.10
- Python >= 3.12
- Git >= 2.30

---

## 中文 / 中文说明

### 系统要求 / 系统依赖

- Python 3.12+ 版本
- Docker 容器环境
- Git 版本控制
- Qdrant 向量数据库（本地 Docker 容器）

### 安装步骤

#### 1. 克隆仓库
```bash
git clone https://github.com/lst016/openclaw-skill-evolution.git
cd openclaw-skill-evolution
```

#### 2. 设置 Python 虚拟环境
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. 启动 Qdrant
```bash
# 启动 Qdrant 容器（指定名称）
docker run -d --name openclaw-skill-evolution-qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  qdrant/qdrant:latest

# 验证 Qdrant 是否正常运行
curl http://localhost:6333
```

#### 4. 初始化 Qdrant 集合
```bash
# 创建 Qdrant 所需的集合
python scripts/qdrant_setup.py
```

#### 5. 运行集成测试
```bash
# 测试 v3 集成（当前版本）
python scripts/v3_integration_test.py
```

### Python 依赖包

#### 核心依赖
- `qdrant-client` >= 1.7.0 - Qdrant Python 客户端
- `pyyaml` >= 6.0 - YAML 文件解析
- `httpx` >= 0.24.0 - 异步 HTTP 客户端

#### 系统依赖
- Docker >= 20.10 - 容器运行环境
- Python >= 3.12 - Python 运行时
- Git >= 2.30 - 版本控制管理

---

## Configuration / 配置

### Environment Variables / 环境变量
```bash
# Qdrant connection
export QDRANT_HOST=localhost
export QDRANT_PORT=6333

# Workspace path
export OPENCLAW_WORKSPACE=/Users/用户名/.openclaw/workspace

# Evolution settings
export EVOLUTION_ENABLED=true
export DAILY_EVOLUTION_TIME="01:00"
```

### Config Files / 配置文件
- `config/qdrant.json`: Qdrant 连接配置
- `config/thresholds.json`: 评分和阈值配置
- `config/evolution.json`: 进化系统配置
- `config/models.json`: 模型配置

---

## Troubleshooting / 故障排除

### Common Issues / 常见问题

#### Qdrant Connection Failed / Qdrant 连接失败
```bash
# Check if Qdrant container is running
docker ps | grep qdrant

# Restart Qdrant container
docker restart openclaw-skill-evolution-qdrant
```

#### Module Import Errors / 模块导入错误
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Collection Creation Failed / 集合创建失败
```bash
# Check Qdrant API
curl http://localhost:6333

# Re-run setup script
python scripts/qdrant_setup.py
```

---

## Development Setup / 开发环境设置

### Development Mode / 开发模式
```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest tests/

# Format code
black agents/ scripts/ docs/
```

### Docker Development / Docker 开发
```bash
# Build development container
docker build -t openclaw-skill-evolution:dev .

# Run in container
docker run -it openclaw-skill-evolution:dev bash
```