# 火山引擎基础设施期望状态模板
> 地域：cn-beijing
> 最后更新：2026-03-11

## VPC 网络
- VPC 名称：prod-vpc
- CIDR：172.16.0.0/16
- 子网：
  - 公有子网：172.16.1.0/24（可用区 cn-beijing-a）
  - 私有子网：172.16.2.0/24（可用区 cn-beijing-b）
- 安全组：
  - prod-sg：允许 80/443 入站，全部出站

## ECS 云服务器
- 集群名：prod-cluster
- 实例列表：
  - 名称：web-server-01
    镜像：centos-7.9
    规格：ecs.g1ie.large（2核4G）
    子网：公有子网
    公网IP：自动分配
    安全组：prod-sg
    端口：80、443

## RDS 数据库
- 实例名：prod-mysql
- 引擎：MySQL 8.0
- 规格：rds.mysql.2c4g
- 存储：100GB SSD
- 只读副本：1 个
- 备份：每天 02:00，保留 7 天
- 白名单：允许 VPC 内网访问

## CLB 负载均衡
- 名称：prod-clb
- 类型：应用型（ALB）
- 公网IP：是
- 监听规则：
  - HTTPS 443 → web-server-01:443（证书：cert-xxx）
  - HTTP 80 → 重定向到 HTTPS

## TOS 对象存储
- Bucket：myapp-assets-prod
- 权限：公共读
- 生命周期：30 天后转低频存储，180 天后删除
- 跨域配置：允许前端域名访问

## IAM/RAM 权限
- 角色：cicd-deploy-role
  信任策略：允许GitHub Actions OIDC访问
  权限：ECS 读写、TOS 读写、RDS 只读
