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
skills/openclaw-volcano-cloud/
├── SKILL.md                  # 技能核心定义：触发词、指令、示例
├── README.md                 # 当前文件，提供集成与使用说明
├── config_schema.json        # 技能配置文件的 JSON Schema
├── scripts/                  # 可执行脚本
│   ├── ve_openapi_signer.py  # 火山引擎 OpenAPI V4 签名工具
│   ├── ve_openapi_client.py  # 火山引擎 OpenAPI V4 通用客户端
│   ├── vecloud_client.py     # 整合了真实 API 调用的云资源操作客户端
│   ├── provision_env.py      # 环境蓝图编排脚本（plan 占位）
│   ├── ark_usage_cost.py     # Ark 用量与成本统计
│   ├── workorder_create.py   # 工单生成器
│   ├── inspect_runner.py     # 巡检编排器
│   └── common.py             # 通用工具函数
├── references/               # 参考文档与模板
│   ├── api_mapping.md        # 技能动作与火山引擎 API/资源字段的映射关系
│   └── rag_templates.md      # RAG 故障问答模板
├── logs/                     # 审计日志目录（由脚本自动创建）
│   └── audit.log
└── reports/                  # 报告输出目录（由脚本自动创建）
    └── ...
```

## 集成方式

1.  **放置技能目录**:
    将 `openclaw-volcano-cloud` 整个文件夹放置到您的 OpenClaw 工作区的 `skills/` 目录下。

2.  **配置环境变量 (推荐)**:
    为了安全地管理凭据，建议通过环境变量提供火山引擎的 AK/SK 和默认区域。
    ```bash
    export VE_AK="YOUR_VOLCANO_ENGINE_ACCESS_KEY"
    export VE_SK="YOUR_VOLCANO_ENGINE_SECRET_KEY"
    export VE_REGION="cn-beijing"
    ```

3.  **创建并配置 `config.json`**:
    这是**必须**步骤，因为所有 API 调用都需要从此文件获取 `versions` 和其他配置。在技能根目录（`skills/openclaw-volcano-cloud/`）或您选择的任何位置创建一个 `config.json` 文件。

    **`config.json` 示例**:
    ```json
    {
      "credentials": {
        "ve_ak": "YOUR_AK_OR_USE_ENV_VAR",
        "ve_sk": "YOUR_SK_OR_USE_ENV_VAR",
        "ve_region": "cn-beijing"
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

## 本地测试示例

### 示例 1: 创建 VPC

1.  创建 `vpc.json` 文件：
    ```json
    {
      "VpcName": "my-test-vpc",
      "CidrBlock": "10.10.0.0/16"
    }
    ```
2.  执行真实创建命令：
    ```bash
    python skills/openclaw-volcano-cloud/scripts/vecloud_client.py \
      --action create_vpc \
      --payload-file vpc.json \
      --config path/to/your/config.json
    ```

### 示例 2: 创建 ECS 实例

1.  创建 `ecs.json` 文件（请替换为您的真实 VPC 和子网 ID）：
    ```json
    {
      "InstanceName": "my-test-ecs",
      "InstanceType": "ecs.g1ie.large",
      "ImageId": "image-ybjon96vrtes7s*****",
      "VpcId": "vpc-274o1qew383r47fap8t7k****",
      "SubnetId": "subnet-274o2w7bgn7747fap8tc****",
      "SecurityGroupIds": ["sg-274omwz6p5d1s7fap8s7****"],
      "Password": "YourPassword@123"
    }
    ```
2.  执行真实创建命令：
    ```bash
    python skills/openclaw-volcano-cloud/scripts/vecloud_client.py \
      --action create_instance \
      --payload-file ecs.json \
      --config path/to/your/config.json
    ```

### 示例 3: 使用 `--dry-run` 预览操作

如果您想在执行前预览 API 请求，可以使用 `--dry-run` 标志。这不会发起真实 API 调用。

```bash
python skills/openclaw-volcano-cloud/scripts/vecloud_client.py \
  --action create_vpc \
  --payload-file vpc.json \
  --config path/to/your/config.json \
  --dry-run
```

### 示例 4: 巡检云资源

此操作通常是只读的，可以相对安全地执行。

```bash
python skills/openclaw-volcano-cloud/scripts/inspect_runner.py \
  --config path/to/your/config.json \
  --output result.json
```
这会调用 `DescribeInstances`（如果已在 `config.json` 中配置 Version）并生成一份本地巡检报告。

## 安全提示

- **凭据安全**: 切勿将 AK/SK 硬编码在脚本或 `SKILL.md` 中。强烈建议使用环境变量或安全的密钥管理服务。
- **最小权限**: 为 OpenClaw 使用的 AK/SK 配置最小化的 IAM 权限，仅授予其执行必要操作的权限。
- **二次确认**: 对于删除/释放资源等高危操作，Agent **必须**在调用脚本前向用户发起二次确认，并明确告知风险。
- **`--dry-run` 预览**: 在执行任何不确定的操作前，强烈建议先使用 `--dry-run` 查看计划。
- **审计日志**: 所有脚本都会将操作写入 `logs/audit.log`（JSON Lines）。在排查问题、审计操作或归档变更记录时，可直接基于该文件进行分析。
