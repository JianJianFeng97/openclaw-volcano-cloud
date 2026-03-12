---
name: openclaw-volcano-cloud
description: 管理火山引擎（Volcano Engine）云资源与方舟（Ark）大模型用量的综合技能。通过接入火山引擎OpenAPI，实现云资源的真实创建、配置与操作，以及实例启停/重启、健康巡检、成本统计、声明式GitOps基础设施管理。
version: "2.2.0"
allowed-tools:
  - Bash(python:scripts/*.py)
  - Terraform
---

# OpenClaw 火山引擎云管理技能
本技能为OpenClaw提供统一管理火山引擎云资源与方舟Ark大模型服务的能力，基于火山引擎官方SDK实现，API兼容性100%，操作稳定可靠。

## 触发条件
当用户的意图涉及以下场景时触发本技能：
- 云资源查询/创建/修改/删除（ECS/VPC/子网/安全组/EIP/CLB等）
- 火山引擎账户余额/账单/成本查询
- 云资源健康巡检、配置漂移检查
- GitOps基础设施管理、资源状态同步到代码仓库
- 方舟大模型用量统计、成本分析
- 云资源相关故障排查

## 前置依赖
1. 已安装Terraform ≥ 1.6.0
2. 已配置火山引擎AK/SK，具备对应资源的操作权限
3. （可选）已配置GitHub仓库，用于GitOps状态存储

## 📋 前置准备
### 1. Python环境要求
- Python版本：3.8 ~ 3.12（推荐3.10+）
- 操作系统：Linux/macOS/Windows均可
### 2. 安装依赖
```bash
# 安装火山引擎官方Python SDK
pip install volcengine-python-sdk --upgrade
# 验证安装
python -c "import volcenginesdkcore; print('SDK安装成功，版本：', volcenginesdkcore.__version__)"
```

```
## 🎯 功能使用示例
所有命令均在`openclaw-volcano-cloud`目录下执行
---
### ✅ 1. 查询ECS实例列表
```bash
python scripts/vecloud_client.py --action list_assets
```
返回结果示例：
```json
{
  "ok": true,
  "assets": [
    {
      "resource_id": "i-xxxxxx",
      "resource_name": "test-ecs",
      "status": "RUNNING",
      "public_ip": "118.xx.xx.xx",
      "private_ip": "172.31.0.2",
      "os_name": "veLinux 2.0 CentOS Compatible 64 bit",
      "instance_type": "ecs.g4i.large"
    }
  ]
}
```
---
### ✅ 2. 查询账户余额
```bash
python scripts/vecloud_client.py --action query_balance
```
返回结果示例：
```json
{
  "ok": true,
  "balance": {
    "available_balance": "98.15",
    "cash_balance": "98.15",
    "freeze_amount": "0",
    "arrears_balance": "0",
    "currency": "CNY"
  }
}
```
---
### ✅ 3. 查询账单明细
```bash
# 查询2026年3月账单，默认返回10条记录
python scripts/vecloud_client.py --action query_bill --bill-period 2026-03
# 自定义返回条数
python scripts/vecloud_client.py --action query_bill --bill-period 2026-03 --limit 20
```
返回结果包含总消费金额、每条消费记录的时间、产品类型、费用等信息。
---
### ✅ 4. 查询Ark大模型成本
```bash
# 查询2026年3月Ark消费明细
python scripts/vecloud_client.py --action query_ark_cost --bill-period 2026-03
```
返回结果示例（无消费时总费用为0）：
```json
{
  "ok": true,
  "bill_period": "2026-03",
  "total_cost": 0,
  "total_calls": 0,
  "model_stats": {}
}
```
---
### ✅ 5. 停止ECS实例
```bash
# 先创建参数文件 stop_instance.json
echo '{"instance_id": "i-你的实例ID"}' > stop_instance.json
# 执行停止操作
python scripts/vecloud_client.py --action stop --payload-file stop_instance.json
# 模拟执行（不真实停止）
python scripts/vecloud_client.py --action stop --payload-file stop_instance.json --dry-run
```
---
### ✅ 6. 启动ECS实例
```bash
# 创建参数文件 start_instance.json
echo '{"instance_id": "i-你的实例ID"}' > start_instance.json
# 执行启动操作
python scripts/vecloud_client.py --action start --payload-file start_instance.json
```
---
### ✅ 7. 重启ECS实例
```bash
# 创建参数文件 reboot_instance.json
echo '{"instance_id": "i-你的实例ID"}' > reboot_instance.json
# 执行重启操作
python scripts/vecloud_client.py --action reboot --payload-file reboot_instance.json
```
---
### ✅ 8. 生成工单草稿（工单功能待SDK安装后可直接提交）
```bash
python scripts/vecloud_client.py --action create_ticket --title "ECS实例公网无法访问" --content "实例i-xxxxxx公网ping不通，SSH也无法连接" --severity high --product-type ecs
```
---

## 核心指令
### 资源查询类
| 指令示例 | 说明 |
|----------|------|
| `查询火山账户余额` | 查询账户可用余额、欠费状态 |
| `查询上海区ECS实例状态` | 查询指定区域的ECS实例列表与状态 |
| `查询当前区域所有资源` | 列出账户下所有云资源信息 |
| `查询本月账单明细` | 查询指定月份的消费账单明细 |

### 资源操作类
| 指令示例 | 说明 |
|----------|------|
| `创建一台2核8G的ECS实例` | 创建指定配置的ECS实例 |
| `启动实例i-xxxxxx` | 启动指定ID的ECS实例 |
| `停止实例i-xxxxxx` | 停止指定ID的ECS实例 |
| `重启实例i-xxxxxx` | 重启指定ID的ECS实例 |
| `删除实例i-xxxxxx` | 释放指定ID的ECS实例（高危操作，二次确认） |

### GitOps类
| 指令示例 | 说明 |
|----------|------|
| `将当前资源同步到GitHub仓库` | 导入现有资源到Terraform状态，生成配置提交到仓库 |
| `对比当前资源与仓库配置差异` | 执行terraform plan，返回变更预览 |
| `应用仓库配置到线上` | 执行terraform apply，将仓库配置生效到线上 |

### 成本巡检类
| 指令示例 | 说明 |
|----------|------|
| `检查本月Ark模型用量` | 统计方舟大模型的token消耗与成本 |
| `巡检闲置资源` | 识别低负载/闲置资源，推荐优化方案 |
| `生成云资源体检报告` | 输出资源健康状态、成本、安全配置的综合报告 |

## 安全规则
1. **高危操作二次确认**：删除/释放资源、修改安全组规则、调整公网带宽等高危操作必须向用户发起二次确认，明确告知风险
2. **密钥零泄露**：禁止任何场景下明文输出AK/SK等敏感信息，敏感信息用`***`脱敏展示
3. **DryRun优先**：所有资源变更类操作默认先执行DryRun校验，校验通过后再执行真实操作
4. **审计日志**：所有操作都会写入`logs/audit.log`，包含完整的请求与响应信息，便于追溯
5. **最小权限原则**：建议用户为AK配置最小必要权限，避免过度授权

## 目录结构
```
openclaw-volcano-cloud/
├── SKILL.md                # OpenClaw标准技能说明文档，包含触发条件、核心指令、安全规则
├── README.md               # 完整项目技术文档，就是你要的公众号文章的技术版
├── config.json.example     # 配置文件模板，已清空所有密钥，用户自行填入AK/SK即可使用
├── config_schema.json      # 配置文件校验规则
├── scripts/                # 核心功能脚本
│   ├── common.py           # 公共工具函数
│   ├── vecloud_client.py   # 云资源操作客户端
│   └── gitops_agent.py     # GitOps自动化脚本
├── references/             # 参考文档
│   ├── api_mapping.md
│   ├── desired-state-example.md
│   └── rag_templates.md
├── logs/                   # 审计日志目录（带.gitkeep占位）
└── reports/                # 巡检报告输出目录（带.gitkeep占位）
```
## Gitops仓库地址
仓库地址：https://github.com/JianJianFeng97/volc-infra