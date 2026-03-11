---
name: openclaw-volcano-cloud
description: >-
  管理火山引擎（Volcano Engine）云资源与方舟（Ark）大模型用量的综合技能。通过接入火山引擎 OpenAPI，实现云资源的真实创建、配置与操作（VPC、子网、安全组、EIP、CLB、NAT、路由、ECS、VKE、云盘、快照等），以及实例启停/重启、健康巡检、初步故障问答、Ark 成本统计与协同工作流。
version: "2.0.0"
allowed-tools:
  - Bash(python:scripts/*.py)
---

# Volcano Engine 云管与 Ark 成本治理技能

本技能为 OpenClaw 提供了统一管理火山引擎云资源与方舟 Ark 大模型服务的能力，通过调用火山引擎官方CLI工具，覆盖从网络与基础资源创建、资源生命周期管理、日常巡检，到成本统计与协同的完整闭环。

**实现方式：** 基于火山引擎官方CLI工具实现，无需自行处理签名逻辑，API兼容性100%，操作稳定可靠。
**注意：** 此版本默认执行真实API调用，所有创建、修改或删除操作都会对您的火山引擎账户产生实际影响并可能产生费用，支持`--dry-run`预览模式。

## 何时触发此技能

当用户的意图涉及**火山引擎**、**云资源/网络**或**方舟大模型**时，应优先考虑触发此技能。常见中文问法包括：

- **网络与资源创建**：“帮我新建一个 VPC/子网”、“创建安全组并开放 80/443 端口”、“申请一个 EIP 并绑定到 web 实例”、“创建一个公网 CLB 做 HTTP 负载均衡”、“创建一块数据盘并挂载到指定实例”、“为内网服务新增一个私有域名解析”等。
- **实例/集群创建与操作**：“帮我创建一台云服务器”、“在北京区新建一台 ECS 实例”、“把那台测试服务器关机”、“重启一下 web 应用的实例”、“创建一个 VKE 集群用于测试环境”等。
- **云资源巡检**：“检查一下我账号下的资源健康状况”、“做一次安全基线扫描”、“输出一份云资源体检报告”。
- **初步故障问答 (RAG)**：“我的网站为什么访问不了？”、“ECS 实例无法 SSH 连接是什么原因？”、“为什么这个月的云费用突然增加了？”。
- **方舟 Ark 大模型用量与成本**：“统计一下上个月 Ark 模型的使用量”、“哪个项目 token 消耗最多？”、“估算一下 Ark Pro 模型的成本”、“生成一份 Ark 服务的报账单”。
- **协同操作**：“针对昨天的费用异常创建一个工单”、“把巡检报告发给技术负责人”、“根据这份蓝图一键规划一个测试环境”。

## 核心指令与场景

本技能通过调用 `scripts/` 下的 Python 脚本执行，所有操作均记录在 `logs/audit.log` 中。

**重要提示**：执行任何创建或修改操作前，必须在 `config.json` 的 `api.versions` 字段中为相应的 OpenAPI Action（如 `RunInstances`、`CreateVpc`）配置正确的 `Version`。

### 场景一：网络与资源创建（VPC/子网/安全组/EIP/CLB/NAT/路由/磁盘/私有域）

通过 `vecloud_client.py` 创建或配置网络与基础资源。

- **命令行示例：创建 VPC**：

  ```bash
  # 1. 准备 vpc.json 文件
  # { "CidrBlock": "10.0.0.0/16", "VpcName": "my-vpc" }

  # 2. 执行创建（真实调用）
  python scripts/vecloud_client.py --action create_vpc --payload-file vpc.json --config config.json
  ```

- **命令行示例：创建安全组并添加入方向规则**：

  ```bash
  # 1. 准备 sg.json 文件
  # { "VpcId": "vpc-xxxx", "SecurityGroupName": "web-sg" }
  python scripts/vecloud_client.py --action create_sg --payload-file sg.json --config config.json
  # (假设返回了安全组 ID：sg-yyyy)

  # 2. 准备 sg_rule.json 文件
  # { "SecurityGroupId": "sg-yyyy", "Direction": "ingress", "Protocol": "tcp", "PortEnd": 80, "PortStart": 80, "CidrIp": "0.0.0.0/0" }
  python scripts/vecloud_client.py --action add_sg_rule --payload-file sg_rule.json --config config.json
  ```

- **自然语言示例**：
  - “帮我创建一个 VPC，参数在 `vpc.json` 里。配置文件是 `config.json`。”
  - “新建一个安全组 `web-sg`，开放 80/443 端口给公网访问。”

### 场景二：云服务器创建

通过 `vecloud_client.py` 创建云服务器实例。

- **命令行示例**：
  ```bash
  # 1. 准备实例规格 JSON 文件 (e.g., spec.json)
  # { "InstanceName": "web-server-01", "InstanceType": "ecs.g1ie.large", ... }
  
  # 2. 执行创建（真实调用）
  python scripts/vecloud_client.py --action create_instance --payload-file spec.json --config config.json
  ```
- **自然语言示例**：
  “帮我在火山引擎北京区创建一个实例，规格文件是 `spec.json`。”

### 场景三：云资源操作（启停/重启）

通过 `vecloud_client.py` 对指定实例执行电源操作。

- **命令行示例**:
  ```bash
  # 准备操作参数 (e.g., payload.json)
  # { "instance_id": "i-xxxxx" }
  
  python scripts/vecloud_client.py --action stop --payload-file payload.json --config config.json
  ```
- **自然语言示例**:
  “停止实例 `i-xxxxx`。”

### 场景四：云资源巡检与报告

通过 `inspect_runner.py` 编排资产发现、规则检查与报告生成。此操作通常是只读的，但仍建议在生产环境谨慎执行。

- **命令行示例**:
  ```bash
  # 执行一次计划性巡检，输出报告到默认目录
  python scripts/inspect_runner.py --mode scheduled --output result.json --config config.json
  
  # 查看生成的报告
  cat reports/cloud_inspect_report.json
  ```
- **自然语言示例**:
  “对我的火山引擎账号做一次完整的健康巡检，并把报告路径告诉我。”

### 场景五：初步故障问答 (RAG)

本技能不直接处理 RAG 逻辑，但提供了答案框架与模板 `references/rag_templates.md`，供上层 Agent 参考。当用户提问时，Agent 应：

1. **识别问题场景**（如“网站不可用”、“费用异常”、“实例无法 SSH”）。
2. **结合巡检/成本/日志等结果**（如 `cloud_inspect_report.json`、Ark 成本报告）分析线索。
3. **参考 `rag_templates.md`** 组织答案，按“问题重述 → 原因线索 → 建议动作 → 风险提示 → 是否需要人工介入”的结构输出。

### 场景六：Ark 大模型用量与成本统计

通过 `ark_usage_cost.py` 统计用量、估算成本并检查预算。

- **命令行示例**:
  ```bash
  # 假设用量数据在 usage.csv 中
  python scripts/ark_usage_cost.py --usage-csv usage.csv --config config.json --output-csv cost_summary.csv
  ```
- **自然语言示例**:
  “基于 `usage.csv` 文件，帮我统计上个月的 Ark 模型费用，并检查是否超预算。”

### 场景七：协同（创建工单）

通过 `workorder_create.py` 生成标准化工单 JSON。

- **命令行示例**:
  ```bash
  # 准备异常信息 (e.g., anomaly.json)
  python scripts/workorder_create.py --input-json anomaly.json --output workorder.json
  ```
- **自然语言示例**:
  “根据 `anomaly.json` 的内容，帮我创建一个 P2 级别的费用异常工单。”

## 输入输出约定

- **输入**：主要通过 JSON 文件传递复杂参数（如实例规格、网络蓝图、事件内容），简单参数（如实例 ID）可直接在命令行或自然语言中提供。所有脚本均需通过 `--config` 参数指定统一配置文件。
- **输出**：
  - 成功时，默认向 `stdout` 输出 JSON 结构的结果，包含 `request_id` 与核心响应字段，便于 Agent 解析。
  - 失败时，返回的 JSON 中 `ok` 为 `false`，并包含 `error_code` 和 `error_message`。
  - 所有操作均会追加一条 JSON Line 记录到 `logs/audit.log`，包含完整的请求与响应信息。

## 错误处理

- 脚本在 API 调用失败时会返回非零退出码，并将包含错误信息的 JSON 输出到 `stdout`。
- `logs/audit.log` 中会记录 `status: "error"` 的审计条目，包含完整的请求与响应，便于排查。
- 常见的错误类型包括 `InvalidActionOrVersion`（Action 或 Version 不正确）、`SignatureDoesNotMatch`（签名失败）、`AccessDenied`（权限不足）。Agent 在捕获到错误时，应向用户报告问题，并可引导用户检查配置或查看日志。

## 危险操作：二次确认与 `dry-run`

- **默认真实调用**: 本技能默认执行**真实** API 调用。任何创建、修改、删除操作都会立即生效。
- **二次确认**: 对于删除/释放资源等高危操作（在 `config_schema.json` 的 `approvals.require_approval_actions` 中定义），Agent **必须**在调用脚本前向用户发起二次确认，并明确告知风险。
- **`--dry-run` 预览模式**:
  - 所有资源变更类脚本均支持 `--dry-run` 标志。
  - 使用 `--dry-run` 时，脚本**仅生成请求蓝图**并写入审计日志，**不会**发出真实的 API 调用。
  - 在执行任何不确定的操作前，强烈建议先使用 `--dry-run` 预览将要执行的动作。

  - **`--dry-run` 示例**：
    ```bash
    python scripts/vecloud_client.py --action create_instance --payload-file spec.json --config config.json --dry-run
    ```
- **安全提示**: 在执行任何可能产生费用或变更资源状态的操作前，Agent 都应向用户明确说明潜在风险，并鼓励先使用 `--dry-run` 查看计划。