# API 映射与返回字段约定

本文件定义了 OpenClaw 技能中关键动作与火山引擎（Volcano Engine）常见产品的术语映射，以及推荐的返回字段统一化约定。所有 API 细节需以火山引擎当前最新的官方公开文档为准进行校准。

## 一、术语与产品映射

| OpenClaw 动作/概念 | 火山引擎产品/服务 | 英文缩写/术语 | 备注 |
| :--- | :--- | :--- | :--- |
| **实例/云服务器** | 云服务器 | ECS (Elastic Compute Service) | 核心计算单元 |
| **公网 IP** | 弹性公网 IP | EIP (Elastic IP) | 提供公网访问能力 |
| **虚拟网络** | 私有网络 | VPC (Virtual Private Cloud) | 隔离的网络环境 |
| **子网** | 子网 | Subnet | VPC 内的 IP 地址块 |
| **安全策略/防火墙** | 安全组 | Security Group | 控制实例网络访问权限 |
| **NAT 网关** | NAT 网关 | NAT Gateway | 提供私网访问公网能力 |
| **路由表** | 路由表 | Route Table | VPC/子网的路由控制 |
| **负载均衡** | 负载均衡 | CLB (Cloud Load Balancer) | 分发流量到后端服务器 |
| **云监控** | 云监控 | Cloud Monitor | 监控资源指标与告警 |
| **日志服务** | 日志服务 | Log Service | 日志采集、查询与分析 |
| **容器平台** | 容器服务 | VKE (Volcano Engine Kubernetes Engine) | 托管的 Kubernetes 服务 |
| **块存储** | 云盘 | Disk / Volume | 挂载到 ECS 的持久化存储 |
| **快照** | 云盘快照 | Snapshot | 盘级别数据备份 |
| **私有域名** | 私有域名服务 | Private Zone | VPC 内解析的私有 DNS 区域 |
| **大模型服务** | 方舟大模型平台 | Ark | 提供多种大语言模型 API |
| **身份与访问** | 访问控制 | IAM (Identity and Access Management) | 管理用户、角色与权限 |
| **对象存储** | 对象存储 | TOS (Object Storage) | 海量文件存储 |

## 二、关键动作与 API 映射（占位示例）

以下映射仅为示例，实际实现时需参考火山引擎 Python SDK 或 OpenAPI 文档。

| 技能动作 (vecloud_client.py) | 火山引擎 OpenAPI Action（占位） | 主要参数（示例） | 备注 |
| :--- | :--- | :--- | :--- |
| `create_instance` | `RunInstances` | `InstanceName`, `InstanceType`, `ImageId`, `VpcId`, `SubnetId`, `SecurityGroupIds`, `AllocatePublicIp` | 创建 ECS 实例 |
| `start_instance` | `StartInstances` | `InstanceIds` | 启动一个或多个 ECS 实例 |
| `stop_instance` | `StopInstances` | `InstanceIds`, `Force` | 停止一个或多个 ECS 实例 |
| `reboot_instance` | `RebootInstances` | `InstanceIds` | 重启一个或多个 ECS 实例 |
| `create_vpc` | `CreateVpc` | `VpcName`, `CidrBlock`, `Description`, `Tags` | 创建 VPC |
| `create_subnet` | `CreateSubnet` | `VpcId`, `SubnetName`, `ZoneId`, `CidrBlock`, `Tags` | 在 VPC 内创建子网 |
| `create_security_group` | `CreateSecurityGroup` | `SecurityGroupName`, `VpcId`, `Description`, `Tags` | 创建安全组 |
| `add_sg_rule` | `AuthorizeSecurityGroupRule` | `SecurityGroupId`, `Direction`, `Protocol`, `PortRange`, `CidrIp` | 添加安全组规则 |
| `create_nat_gateway` | `CreateNatGateway` | `VpcId`, `SubnetId`, `BandwidthPackage`, `NatName` | 创建 NAT 网关 |
| `create_route_table` | `CreateRouteTable` | `VpcId`, `RouteTableName`, `Tags` | 创建路由表 |
| `add_route` | `CreateRouteEntry` | `RouteTableId`, `DestinationCidrBlock`, `NextHopType`, `NextHopId` | 在路由表中添加路由 |
| `create_eip` | `AllocateEipAddress` | `Bandwidth`, `ChargeType`, `ProjectName`, `Tags` | 申请弹性公网 IP |
| `bind_eip` | `AssociateEipAddress` | `AllocationId`, `InstanceId` / `LoadBalancerId` | 绑定 EIP 到 ECS 或 CLB |
| `create_clb` | `CreateLoadBalancer` | `LoadBalancerName`, `VpcId`, `SubnetId`, `LoadBalancerType`, `Tags` | 创建 CLB 实例 |
| `create_disk` | `CreateVolume` | `ZoneId`, `VolumeType`, `Size`, `ProjectName`, `Tags` | 创建云盘 |
| `attach_disk` | `AttachVolume` | `VolumeId`, `InstanceId`, `Device` | 将云盘挂载到实例 |
| `create_snapshot` | `CreateSnapshot` | `VolumeId`, `SnapshotName`, `Tags` | 创建云盘快照 |
| `create_vke_cluster` | `CreateCluster` | `ClusterName`, `KubernetesVersion`, `VpcId`, `Subnets`, `NodePools` | 创建 VKE 集群 |
| `create_private_zone` | `CreatePrivateZone` | `ZoneName`, `Remark`, `VpcBindings`, `Tags` | 创建私有 DNS Zone |
| `add_record` | `CreatePrivateZoneRecordSet` | `ZoneId`/`ZoneName`, `RecordName`, `Type`, `Value`, `TTL` | 在私有 Zone 中创建记录 |
| `list_assets` (ECS) | `DescribeInstances` | `InstanceIds`, `VpcId`, `ProjectName`, `Tags` | 查询 ECS 实例列表 |
| `list_assets` (EIP) | `DescribeEips` | `EipAddresses`, `AllocationIds`, `ProjectName` | 查询 EIP 列表 |
| `list_assets` (CLB) | `DescribeLoadBalancers` | `LoadBalancerIds`, `VpcId`, `ProjectName` | 查询 CLB 实例列表 |

> 以上 Action 名和参数名仅为典型命名示意，实际实现时必须以官方文档为准校准。

## 三、统一返回字段约定

为便于上层 Agent 解析，所有脚本返回的资源信息应尽量遵循以下统一结构。

### 3.1 基础资源对象 (BaseResource)

所有资源对象都应包含以下基础字段：

```json
{
  "resource_id": "i-xxxxxxxxxx",         // 资源唯一标识
  "resource_type": "ecs",                // 资源类型（小写，如 ecs, eip, clb, vpc, disk, snapshot, vke_cluster, private_zone）
  "resource_name": "my-instance-name",   // 资源名称
  "region": "cn-beijing",                // 所在地域
  "project": "default-project",          // 所属项目
  "status": "Running",                   // 资源状态
  "created_at": "2026-01-01T12:00:00Z", // 创建时间 (UTC)
  "tags": {                               // 标签
    "env": "production",
    "owner": "fengjian.97"
  }
}
```

### 3.2 网络与关系字段

在网络与拓扑相关的资源上，推荐显式补充以下关系字段，便于跨资源聚合：

```json
{
  "vpc_id": "vpc-xxxxxxxx",
  "subnet_id": "subnet-xxxxxxxx",
  "sg_id": "sg-xxxxxxxx",
  "eip_id": "eip-xxxxxxxx",
  "instance_id": "i-xxxxxxxxxx",
  "clb_id": "lb-xxxxxxxx",
  "zone": "cn-beijing-a",
  "region": "cn-beijing"
}
```

### 3.3 云服务器实例 (ECS)

继承 `BaseResource`，并增加以下字段：

```json
{
  // ... BaseResource fields
  "instance_type": "ecs.g1ie.large",
  "image_id": "image-xxxxxxxx",
  "private_ip": ["192.168.1.10"],
  "public_ip": ["180.184.xx.xx"],
  "vpc_id": "vpc-xxxxxxxx",
  "subnet_id": "subnet-xxxxxxxx",
  "security_group_ids": ["sg-xxxxxxxx"]
}
```

### 3.4 弹性公网 IP (EIP)

继承 `BaseResource`，并增加以下字段：

```json
{
  // ... BaseResource fields
  "ip_address": "180.184.xx.xx",
  "bandwidth_mbps": 10,
  "charge_type": "PostPaidByBandwidth", // 计费类型
  "associated_resource_id": "i-xxxxxxxxxx",
  "associated_resource_type": "ecs"      // 也可能为 clb
}
```

### 3.5 云盘 (Disk) 与快照 (Snapshot)

云盘：

```json
{
  // ... BaseResource fields
  "disk_type": "ssd",
  "size_gib": 100,
  "zone": "cn-beijing-a",
  "attached_instance_id": "i-xxxxxxxxxx"
}
```

快照：

```json
{
  // ... BaseResource fields
  "source_disk_id": "disk-xxxxxxxx",
  "policy": "daily" // 例如 daily/weekly/policy-id 等
}
```

### 3.6 私有域名 (Private Zone) 与记录

私有域：

```json
{
  // ... BaseResource fields
  "zone_name": "internal.example.com",
  "associated_vpc_ids": ["vpc-xxxxxxxx"]
}
```

记录：

```json
{
  "zone_id": "pz-xxxxxxxx",
  "zone_name": "internal.example.com",
  "record_name": "www",
  "type": "A",
  "value": "10.0.1.10",
  "ttl": 60
}
```

### 3.7 巡检发现 (Finding)

巡检报告中的异常条目结构：

```json
{
  "resource_id": "i-xxxxxxxxxx",
  "rule": "public_ip_without_explicit_flag", // 规则 ID
  "severity": "high",                         // 严重性 (high, medium, low)
  "message": "资源存在公网 IP 但未显式标记...", // 问题描述
  "recommendation": "请为资源添加 'internet_exposed=true' 标签，或评估是否需要回收公网 IP。" // 修复建议
}
```

---

**声明**：本文档中的所有 API 映射与返回结构均为建议性约定。最终实现**必须**以当前火山引擎官方公开的 API 文档为准进行校准和调整，尤其是 Action 名、请求参数和字段命名。
