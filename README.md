# OpenClaw Volcano Engine Cloud Skill

这是一个为 OpenClaw 设计的技能，用于管理火山引擎（Volcano Engine）的云资源和方舟（Ark）大模型服务。它通过接入真实的火山引擎 OpenAPI，提供了一套完整的云管与 AIOps 能力，包括网络与基础资源创建、实例操作、巡检、成本统计与协同工作流。

**注意：此版本默认执行真实 API 调用，所有创建、修改或删除操作都会对您的火山引擎账户产生实际影响并可能产生费用。**

## 功能特性

- **云资源与网络管理**: 通过真实 OpenAPI 创建/配置 VPC、子网、安全组、NAT 网关、路由表/路由、弹性公网 IP（EIP）、负载均衡（CLB）、云盘与快照等，以及云服务器（ECS）与 VKE 集群。
- **实例操作**: 启动、停止、重启云服务器实例。
- **健康巡检**: 自动发现资产，进行安全基线和健康度检查，并生成报告。
- **初步故障问答**: 提供常见故障（如网站不可用、费用异常、实例无法 SSH）的排查框架和答案模板。
- **方舟 Ark 成本治理**: 统计 Token 用量，估算成本，设置预算阈值，并支持生成报账材料。
- **协同工作流**: 一键生成结构化的工单 JSON，便于对接到内部支持系统或飞书。
- **安全与审计**:
  - 所有真实 API 调用均记录在 `logs/audit.log` 中，包含 `request_id` 与完整响应。
  - 支持 `--dry-run` 模式进行操作预览。
  - 高危操作建议通过 `approvals` 配置二次确认。

## 文件结构

```
openclaw-volcano-cloud/
├── scripts/                # 核心代码目录
│   └── vecloud_client.py   # 主程序入口
├── config.json             # 配置文件（可选）
├── SKILL.md                # 技能说明文档
└── 试用指南.md              # 本文件
```

## 集成方式

1.  **放置技能目录**:
    将 `openclaw-volcano-cloud` 整个文件夹放置到您的 OpenClaw 工作区的 `skills/` 目录下。

2.  **配置环境变量 (推荐)**:
    为了安全地管理凭据，建议通过环境变量提供火山引擎的 AK/SK 和默认区域。
    ```bash
    export VE_AK="YOUR_VOLCANO_ENGINE_ACCESS_KEY"
    export VE_SK="YOUR_VOLCANO_ENGINE_SECRET_KEY"
    export VE_REGION="cn-shanghai"
    ```

3.  **创建并配置 `config.json`**:
    这是**必须**步骤，因为所有 API 调用都需要从此文件获取 `versions` 和其他配置。在技能根目录（`skills/openclaw-volcano-cloud/`）或您选择的任何位置创建一个 `config.json` 文件。

    **`config.json` 示例**:
    ```json
    {
      "credentials": {
        "ve_ak": "YOUR_AK_OR_USE_ENV_VAR",
        "ve_sk": "YOUR_SK_OR_USE_ENV_VAR",
        "ve_region": "cn-shanghai"
      },
      "api": {
        "mode": "service_host",
        "versions": {
          "CreateVpc": "2020-04-01",
          "RunInstances": "2020-04-01",
          "StartInstances": "2020-04-01",
          "StopInstances": "2020-04-01",
          "RebootInstances": "2020-04-01",
          "DescribeInstances": "2020-04-01",
          "CreateSubnet": "2020-04-01",
          "CreateSecurityGroup": "2020-04-01",
          "AuthorizeSecurityGroupRule": "2020-04-01",
          "CreateNatGateway": "2021-11-01",
          "CreateRouteTable": "2020-04-01",
          "CreateRouteEntry": "2020-04-01",
          "AllocateEipAddress": "2020-04-01",
          "AssociateEipAddress": "2020-04-01",
          "CreateLoadBalancer": "2020-04-01",
          "CreateVolume": "2020-04-01",
          "AttachVolume": "2020-04-01",
          "CreateSnapshot": "2020-04-01",
          "CreateCluster": "2021-05-12",
          "CreatePrivateZone": "2021-01-01",
          "CreatePrivateZoneRecordSet": "2021-01-01"
        }
      },
      "approvals": {
        "default_dry_run": false
      }
    }
    ```
    **注意**: `api.versions` 中的版本号需以火山引擎官方文档为准。
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
## ⚠️ 注意事项
1. **密钥安全**：请勿将AK/SK硬编码到代码或配置文件中提交到公共仓库，推荐使用环境变量方式配置
2. **Dry-Run模式**：所有变更类操作（启动/停止/创建实例）都可以加上`--dry-run`参数模拟执行，确认无误后再真实操作
3. **地域选择**：VE_REGION需要填写你资源所在的正确地域，否则会查询不到资源
4. **权限要求**：使用的AK需要对应开通相关云产品的访问权限，否则会返回权限不足错误
## ❓ 常见问题
### Q1：执行命令返回`Missing authentication token`
A：AK/SK配置错误，请检查密钥是否正确，环境变量是否生效
### Q2：查询不到ECS实例
A：检查VE_REGION是否和实例所在地域一致
### Q3：创建实例返回`Insufficient.Balance`
A：账户余额不足，请充值后再操作
### Q4：工单功能无法使用
A：需要额外安装火山引擎工单SDK`volcenginesdkticket`，安装后即可完整使用
## 📞 技术支持
使用过程中遇到任何问题，或者需要扩展其他功能，随时联系开发者哦😉
