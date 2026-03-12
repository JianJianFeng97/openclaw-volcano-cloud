# OpenClaw 火山引擎云资源管理技能
基于OpenClaw构建的零门槛火山引擎GitOps云管平台，实现自然语言交互、全资源生命周期管理、开箱即用的IaC能力，是个人开发者与中小团队的轻量云资源管理解决方案。

---

## 核心能力
### 1. 全资源生命周期纳管
- 覆盖ECS/VPC/子网/安全组/EIP/CLB/云盘等90%+个人开发者常用资源
- 支持实例启停/配置变更/释放等全生命周期操作
- 内置参数合法性校验、配额/余额前置校验，避免半拉子创建导致的资源残留
- 支持批量操作，适合集群类场景

### 2. 开箱即用的GitOps能力
- 存量资源一键导入：自动拉取现有资源生成标准HCL配置并导入Terraform状态，零成本实现存量资源IaC化
- 变更全流程可追溯：所有变更通过PR提交，CI自动执行格式校验→类型校验→变更预览，合码自动生效
- 状态一致性自动校验：定期对比线上资源与仓库配置差异，出现配置漂移自动告警

### 3. 成本与安全左移
- 多维度成本监控：按资源/项目/时间维度统计消费，余额/消费基线超标自动告警
- 闲置资源自动识别：基于使用率指标推荐资源释放/降配，实测降低30%+云资源成本
- 高危操作强制二次确认，全链路审计日志存储≥180天

---

## 技术架构
```
┌─────────────────┐ 自然语言交互层
│  OpenClaw Agent │ LLM意图识别、参数补全、多渠道交互
├─────────────────┤ 云API适配层
│ Volcengine SDK  │ 官方SDK封装，自动处理签名/版本兼容/重试
├─────────────────┤ 状态管理层
│    Terraform    │ 云资源状态管理，变更预览/回滚/一致性校验
├─────────────────┤ CI流水线层
│ GitHub Actions  │ 自动配置校验/变更预览/发布审批
└─────────────────┘
```

### 技术优势
| 特性 | 本方案 | 纯Terraform | 手动控制台 |
|------|--------|-------------|------------|
| 学习成本 | 极低（自然语言操作） | 高（需要掌握HCL/CLI） | 低 |
| 配置漂移风险 | 极低（自动同步校验） | 低（手动维护） | 极高 |
| 变更审计 | 全流程可追溯 | 依赖Git | 无 |
| 落地成本 | 极低（所有组件免费） | 低（工具免费） | 高（人工+账单浪费） |

---

## 快速开始
### 1. 前置依赖
- OpenClaw ≥ 0.8.0
- Terraform ≥ 1.6.0
- 火山引擎账号，已创建具备`ECSFullAccess`/`VPCFullAccess`/`BillingReadOnlyAccess`权限的AK/SK
- 安装 火山引擎pythonSDK :pip install volcengine-python-sdk --upgrade

### 2. 配置
复制`config.json.example`为`config.json`，填入火山引擎AK/SK与默认区域：
```json
{
  "credentials": {
    "ve_ak": "<your-volcengine-access-key>",
    "ve_sk": "<your-volcengine-secret-key>",
    "ve_region": "cn-shanghai"
  },
  "api": {
    "mode": "gateway",
    "versions": {
      "RunInstances": "2020-04-01",
      "DescribeInstances": "2020-04-01"
    }
  },
  "defaults": {
    "default_instance_type": "ecs.g4i.large",
    "default_image_id": "image-yd7m6lyk64m05l01lxp1",
    "default_tags": {
      "created_by": "openclaw-volcano-skill"
    }
  },
  "approvals": {
    "default_dry_run": false
  }
}
```

### 3. 示例指令
```
- 帮我查下上海区所有ECS实例状态
- 删除实例i-yehgwxokqoqbxysd5v6a
- 创建一台2核8G的ECS，镜像用veLinux，带宽10M
- 将当前所有资源同步到GitHub仓库
```

---

## 安全设计
- 密钥零泄露：AK/SK仅存储在加密环境变量中，永远不会出现在代码/日志/配置文件
- 高危操作多因子校验：实例删除/安全组变更等操作强制二次确认
- DryRun前置校验：所有变更先执行DryRun校验，通过后才执行真实操作
- 全链路审计：所有API调用记录包含操作人/时间/参数/结果，可追溯可审计

---

## 项目地址
GitHub仓库：https://github.com/JianJianFeng97/volc-infra
欢迎Star/PR共建，问题反馈请提交Issue。
