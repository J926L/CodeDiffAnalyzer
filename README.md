# 运行指南

本项目包含 Python 分析引擎（gRPC）和 Go Web 服务，请按以下步骤启动。

## 1. 启动 Python 分析引擎 (gRPC)

打开终端，进入 `python-engine` 目录：

```powershell
cd python-engine
```

运行 Python 服务（首次运行建议先执行 `uv sync` 同步依赖）：

```powershell
uv run python server/grpc_server.py
```

_如果已手动激活虚拟环境，可直接运行：`python server/grpc_server.py`_

_默认监听端口：`50051`_

---

## 2. 启动 Go Web 服务

打开另一个终端，先进入 `go-server` 目录：

```powershell
cd go-server
```

您可以选择以下任意一种方式运行：

### 方式一：运行二进制文件

在 PowerShell 中直接运行 `server.exe`：

```powershell
./server.exe
```

_注意：如果本地缺失 `server.exe`，可先执行以下命令进行编译：_

```powershell
go build -o server.exe cmd/server/main.go
```

### 方式二：通过源码运行

直接通过 Go 工具链拉起：

```powershell
go run cmd/server/main.go
```

_默认服务地址：[http://localhost:8080](http://localhost:8080)_
