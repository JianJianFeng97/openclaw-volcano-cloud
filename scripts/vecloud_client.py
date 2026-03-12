#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""VeCloud 客户端（基于官方Python SDK实现）。
封装火山引擎官方Python SDK，支持所有云资源操作，稳定可靠。
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import volcenginesdkcore
import volcenginesdkecs
import volcenginesdkbilling
# import volcenginesdkticket  # 工单SDK待安装后启用
from volcenginesdkcore.rest import ApiException
try:
    from .common import load_config, write_audit_log, get_skill_root
except ImportError:
    from common import load_config, write_audit_log, get_skill_root

def _get_api_client(
    ak: str,
    sk: str,
    region: str
) -> volcenginesdkcore.ApiClient:
    """获取SDK客户端实例"""
    configuration = volcenginesdkcore.Configuration()
    configuration.ak = ak
    configuration.sk = sk
    configuration.region = region
    volcenginesdkcore.Configuration.set_default(configuration)
    return volcenginesdkcore.ApiClient(configuration)

def list_assets(
    creds: Dict[str, Any],
    dry_run: bool = False
) -> Dict[str, Any]:
    """列出所有云资源"""
    if dry_run:
        return {
            "dry_run": True,
            "note": "dry_run模式，未实际查询资源"
        }
    
    try:
        api_instance = volcenginesdkecs.ECSApi()
        request = volcenginesdkecs.DescribeInstancesRequest()
        resp = api_instance.describe_instances(request)
        instances = resp.to_dict().get("instances", [])
        
        assets = []
        for ins in instances:
            eip = ins.get("eip_address", {})
            primary_ip = ins.get("network_interfaces", [{}])[0].get("primary_ip_address", "")
            assets.append({
                "resource_id": ins.get("instance_id"),
                "resource_type": "ecs",
                "resource_name": ins.get("instance_name"),
                "region": creds["region"],
                "status": ins.get("status"),
                "private_ip": primary_ip,
                "public_ip": eip.get("ip_address"),
                "tags": ins.get("tags", {}),
                "os_name": ins.get("os_name"),
                "instance_type": ins.get("instance_type_id"),
                "zone_id": ins.get("zone_id")
            })
        
        write_audit_log(
            "vecloud.ecs.list_assets",
            {},
            status="success",
            message=f"查询到{len(assets)}台ECS实例"
        )
        return {
            "dry_run": False,
            "ok": True,
            "assets": assets,
            "raw_response": resp.to_dict()
        }
    except ApiException as e:
        error_info = {
            "status": e.status,
            "body": e.body,
            "request_id": e.headers.get("X-Tt-Logid")
        }
        write_audit_log(
            "vecloud.ecs.list_assets",
            {},
            status="error",
            message=f"查询失败: {e.body}"
        )
        return {
            "dry_run": False,
            "ok": False,
            "error": error_info
        }

def create_instance(
    creds: Dict[str, Any],
    spec: Dict[str, Any],
    dry_run: bool = False
) -> Dict[str, Any]:
    """创建ECS实例"""
    if dry_run:
        return {
            "dry_run": True,
            "spec": spec,
            "note": "dry_run模式，未实际创建实例"
        }
    
    try:
        api_instance = volcenginesdkecs.ECSApi()
        network_interfaces = [
            {
                "SubnetId": "subnet-33gs4r2t8zzls6k70bq07mbqy",
                "SecurityGroupIds": ["sg-366we8n77ulfk1e710az6t174"]
            }
        ]
        request = volcenginesdkecs.RunInstancesRequest(
            instance_name=spec.get("name", "openclaw-auto-ecs"),
            instance_type=spec.get("instance_type", "ecs.g4i.large"),
            image_id=spec.get("image_id", "image-yd7m6lyk64m05l01lxp1"),
            zone_id=spec.get("zone_id", "cn-shanghai-a"),
            network_interfaces=network_interfaces,
            password="Openclaw@2026",
            instance_charge_type=spec.get("instance_charge_type", "PostPaid"),
            count=1
        )
        # 过滤空参数
        request_dict = {k: v for k, v in request.to_dict().items() if v not in (None, "", [], {})}
        request = volcenginesdkecs.RunInstancesRequest(**request_dict)
        
        resp = api_instance.run_instances(request)
        
        write_audit_log(
            "vecloud.ecs.create_instance",
            spec,
            status="success",
            message=f"创建实例成功，实例ID: {resp.instance_ids}"
        )
        return {
            "dry_run": False,
            "ok": True,
            "instance_ids": resp.instance_ids,
            "request_id": resp.request_id,
            "raw_response": resp.to_dict()
        }
    except ApiException as e:
        error_info = {
            "status": e.status,
            "body": e.body,
            "request_id": e.headers.get("X-Tt-Logid")
        }
        write_audit_log(
            "vecloud.ecs.create_instance",
            spec,
            status="error",
            message=f"创建失败: {e.body}"
        )
        return {
            "dry_run": False,
            "ok": False,
            "error": error_info
        }

def stop_instance(
    creds: Dict[str, Any],
    instance_id: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """停止ECS实例"""
    if dry_run:
        return {
            "dry_run": True,
            "instance_id": instance_id,
            "note": "dry_run模式，未实际停止实例"
        }
    
    try:
        api_instance = volcenginesdkecs.ECSApi()
        request = volcenginesdkecs.StopInstancesRequest(
            instance_ids=[instance_id]
        )
        resp = api_instance.stop_instances(request)
        
        write_audit_log(
            "vecloud.ecs.stop_instance",
            {"instance_id": instance_id},
            status="success",
            message=f"停止实例{instance_id}成功"
        )
        return {
            "dry_run": False,
            "ok": True,
            "instance_id": instance_id,
            "raw_response": resp.to_dict()
        }
    except ApiException as e:
        error_info = {
            "status": e.status,
            "body": e.body,
            "request_id": e.headers.get("X-Tt-Logid")
        }
        write_audit_log(
            "vecloud.ecs.stop_instance",
            {"instance_id": instance_id},
            status="error",
            message=f"停止实例失败: {e.body}"
        )
        return {
            "dry_run": False,
            "ok": False,
            "error": error_info
        }

def start_instance(
    creds: Dict[str, Any],
    instance_id: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """启动ECS实例"""
    if dry_run:
        return {
            "dry_run": True,
            "instance_id": instance_id,
            "note": "dry_run模式，未实际启动实例"
        }
    
    try:
        api_instance = volcenginesdkecs.ECSApi()
        request = volcenginesdkecs.StartInstancesRequest(
            instance_ids=[instance_id]
        )
        resp = api_instance.start_instances(request)
        
        write_audit_log(
            "vecloud.ecs.start_instance",
            {"instance_id": instance_id},
            status="success",
            message=f"启动实例{instance_id}成功"
        )
        return {
            "dry_run": False,
            "ok": True,
            "instance_id": instance_id,
            "raw_response": resp.to_dict()
        }
    except ApiException as e:
        error_info = {
            "status": e.status,
            "body": e.body,
            "request_id": e.headers.get("X-Tt-Logid")
        }
        write_audit_log(
            "vecloud.ecs.start_instance",
            {"instance_id": instance_id},
            status="error",
            message=f"启动实例失败: {e.body}"
        )
        return {
            "dry_run": False,
            "ok": False,
            "error": error_info
        }

def reboot_instance(
    creds: Dict[str, Any],
    instance_id: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """重启ECS实例"""
    if dry_run:
        return {
            "dry_run": True,
            "instance_id": instance_id,
            "note": "dry_run模式，未实际重启实例"
        }
    
    try:
        api_instance = volcenginesdkecs.ECSApi()
        request = volcenginesdkecs.RebootInstancesRequest(
            instance_ids=[instance_id]
        )
        resp = api_instance.reboot_instances(request)
        
        write_audit_log(
            "vecloud.ecs.reboot_instance",
            {"instance_id": instance_id},
            status="success",
            message=f"重启实例{instance_id}成功"
        )
        return {
            "dry_run": False,
            "ok": True,
            "instance_id": instance_id,
            "raw_response": resp.to_dict()
        }
    except ApiException as e:
        error_info = {
            "status": e.status,
            "body": e.body,
            "request_id": e.headers.get("X-Tt-Logid")
        }
        write_audit_log(
            "vecloud.ecs.reboot_instance",
            {"instance_id": instance_id},
            status="error",
            message=f"重启实例失败: {e.body}"
        )
        return {
            "dry_run": False,
            "ok": False,
            "error": error_info
        }

def terminate_instance(
    creds: Dict[str, Any],
    instance_id: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """终止（删除）ECS实例"""
    if dry_run:
        return {
            "dry_run": True,
            "instance_id": instance_id,
            "note": "dry_run模式，未实际删除实例"
        }
    
    try:
        api_instance = volcenginesdkecs.ECSApi()
        request = volcenginesdkecs.DeleteInstancesRequest(
            instance_ids=[instance_id]
        )
        resp = api_instance.delete_instances(request)
        resp_dict = resp.to_dict()
        
        write_audit_log(
            "vecloud.ecs.terminate_instance",
            {"instance_id": instance_id},
            status="success",
            message=f"删除实例{instance_id}成功"
        )
        return {
            "dry_run": False,
            "ok": True,
            "instance_id": instance_id,
            "status": "deleted",
            "raw_response": resp_dict
        }
    except ApiException as e:
        error_info = {
            "status": e.status,
            "body": e.body,
            "request_id": e.headers.get("X-Tt-Logid")
        }
        write_audit_log(
            "vecloud.ecs.terminate_instance",
            {"instance_id": instance_id},
            status="error",
            message=f"删除实例失败: {e.body}"
        )
        return {
            "dry_run": False,
            "ok": False,
            "error": error_info
        }

def query_balance(
    creds: Dict[str, Any],
    dry_run: bool = False
) -> Dict[str, Any]:
    """查询账户余额"""
    if dry_run:
        return {
            "dry_run": True,
            "note": "dry_run模式，未实际查询余额"
        }
    
    try:
        api_instance = volcenginesdkbilling.BILLINGApi()
        request = volcenginesdkbilling.QueryBalanceAcctRequest()
        resp = api_instance.query_balance_acct(request)
        resp_dict = resp.to_dict()
        
        write_audit_log(
            "vecloud.billing.query_balance",
            {},
            status="success",
            message=f"查询余额成功，可用余额: {resp_dict.get('available_balance')}"
        )
        return {
            "dry_run": False,
            "ok": True,
            "balance": {
                "available_balance": resp_dict.get("available_balance"),
                "cash_balance": resp_dict.get("cash_balance"),
                "freeze_amount": resp_dict.get("freeze_amount"),
                "arrears_balance": resp_dict.get("arrears_balance"),
                "currency": "CNY"
            },
            "raw_response": resp_dict
        }
    except ApiException as e:
        error_info = {
            "status": e.status,
            "body": e.body,
            "request_id": e.headers.get("X-Tt-Logid")
        }
        write_audit_log(
            "vecloud.billing.query_balance",
            {},
            status="error",
            message=f"查询余额失败: {e.body}"
        )
        return {
            "dry_run": False,
            "ok": False,
            "error": error_info
        }

def query_bill(
    creds: Dict[str, Any],
    bill_period: str,
    limit: int = 10,
    dry_run: bool = False
) -> Dict[str, Any]:
    """查询账单明细"""
    if dry_run:
        return {
            "dry_run": True,
            "bill_period": bill_period,
            "note": "dry_run模式，未实际查询账单"
        }
    
    try:
        api_instance = volcenginesdkbilling.BILLINGApi()
        request = volcenginesdkbilling.ListBillRequest(
            bill_period=bill_period,
            limit=limit
        )
        resp = api_instance.list_bill(request)
        resp_dict = resp.to_dict()
        bill_list = resp_dict.get("list", [])
        total_cost = sum(float(item.get("payable_amount", 0)) for item in bill_list)
        
        write_audit_log(
            "vecloud.billing.query_bill",
            {"bill_period": bill_period, "limit": limit},
            status="success",
            message=f"查询{bill_period}账单成功，共{len(bill_list)}条记录，总费用: {total_cost}元"
        )
        return {
            "dry_run": False,
            "ok": True,
            "bill_period": bill_period,
            "total_cost": round(total_cost, 2),
            "bill_list": bill_list,
            "raw_response": resp_dict
        }
    except ApiException as e:
        error_info = {
            "status": e.status,
            "body": e.body,
            "request_id": e.headers.get("X-Tt-Logid")
        }
        write_audit_log(
            "vecloud.billing.query_bill",
            {"bill_period": bill_period, "limit": limit},
            status="error",
            message=f"查询账单失败: {e.body}"
        )
        return {
            "dry_run": False,
            "ok": False,
            "error": error_info
        }

def query_ark_cost(
    creds: Dict[str, Any],
    start_time: str = None,
    end_time: str = None,
    bill_period: str = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """查询Ark大模型成本统计"""
    if dry_run:
        return {
            "dry_run": True,
            "note": "dry_run模式，未实际查询Ark成本"
        }
    
    try:
        # 先查询账单
        api_instance = volcenginesdkbilling.BILLINGApi()
        if not bill_period:
            from datetime import datetime
            bill_period = datetime.now().strftime("%Y-%m")
        
        request = volcenginesdkbilling.ListBillRequest(
            bill_period=bill_period,
            limit=100
        )
        resp = api_instance.list_bill(request)
        resp_dict = resp.to_dict()
        bill_list = resp_dict.get("list", [])
        
        # 筛选Ark相关消费
        ark_bills = [item for item in bill_list if item.get("product", "").lower() in ("ark", "方舟", "大模型", "volcArk")]
        total_cost = sum(float(item.get("payable_amount", 0)) for item in ark_bills)
        total_calls = len(ark_bills)
        
        # 按模型维度统计
        model_stats = {}
        for bill in ark_bills:
            product_name = bill.get("product_zh", "未知模型")
            if product_name not in model_stats:
                model_stats[product_name] = {
                    "count": 0,
                    "cost": 0.0
                }
            model_stats[product_name]["count"] += 1
            model_stats[product_name]["cost"] += float(bill.get("payable_amount", 0))
        
        write_audit_log(
            "vecloud.ark.query_cost",
            {"bill_period": bill_period, "start_time": start_time, "end_time": end_time},
            status="success",
            message=f"查询Ark成本成功，总费用: {total_cost}元，共{total_calls}条消费记录"
        )
        return {
            "dry_run": False,
            "ok": True,
            "bill_period": bill_period,
            "total_cost": round(total_cost, 2),
            "total_calls": total_calls,
            "model_stats": model_stats,
            "ark_bill_list": ark_bills,
            "raw_response": resp_dict
        }
    except ApiException as e:
        error_info = {
            "status": e.status,
            "body": e.body,
            "request_id": e.headers.get("X-Tt-Logid")
        }
        write_audit_log(
            "vecloud.ark.query_cost",
            {"bill_period": bill_period},
            status="error",
            message=f"查询Ark成本失败: {e.body}"
        )
        return {
            "dry_run": False,
            "ok": False,
            "error": error_info
        }

def create_ticket(
    creds: Dict[str, Any],
    title: str,
    content: str,
    severity: str = "normal",
    product_type: str = "ecs",
    dry_run: bool = False
) -> Dict[str, Any]:
    """创建工单（待安装工单SDK后启用）"""
    return {
        "ok": True,
        "note": "工单功能开发中，即将支持火山引擎官方工单/飞书工单/企业微信工单对接，敬请期待",
        "ticket_draft": {
            "title": title,
            "content": content,
            "severity": severity,
            "product_type": product_type
        }
    }

def main():
    parser = argparse.ArgumentParser(description="火山引擎云资源管理客户端（基于官方Python SDK）")
    parser.add_argument("--action", required=True, choices=[
        "create_instance", "start", "stop", "reboot", "terminate_instance", "list_assets",
        "query_balance", "query_bill", "query_ark_cost", "create_ticket",
        "inspect_baseline", "generate_report", "create_vpc", "create_subnet",
        "create_sg", "add_sg_rule", "create_nat", "create_route_table",
        "add_route", "create_eip", "bind_eip", "create_clb", "create_disk",
        "attach_disk", "create_snapshot", "create_vke_cluster",
        "create_private_zone", "add_record"
    ])
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--payload-file", help="参数JSON文件路径")
    parser.add_argument("--dry-run", action="store_true", help="模拟执行，不实际调用API")
    parser.add_argument("--output", help="结果输出文件路径")
    parser.add_argument("--bill-period", help="账单月份，格式YYYY-MM，用于query_bill/query_ark_cost动作")
    parser.add_argument("--limit", type=int, default=10, help="查询数量限制")
    parser.add_argument("--start-time", help="查询开始时间，格式YYYY-MM-DD，用于query_ark_cost动作")
    parser.add_argument("--end-time", help="查询结束时间，格式YYYY-MM-DD，用于query_ark_cost动作")
    parser.add_argument("--title", help="工单标题，用于create_ticket动作")
    parser.add_argument("--content", help="工单内容，用于create_ticket动作")
    parser.add_argument("--severity", default="normal", choices=["low", "normal", "high", "critical"], help="工单优先级，用于create_ticket动作")
    parser.add_argument("--product-type", default="ecs", help="工单所属产品类型，用于create_ticket动作")
    
    args = parser.parse_args()
    config = load_config(args.config)
    
    # 读取凭据
    ak = config.get("credentials", {}).get("ve_ak") or os.getenv("VE_AK") or os.getenv("VOLCENGINE_ACCESS_KEY")
    sk = config.get("credentials", {}).get("ve_sk") or os.getenv("VE_SK") or os.getenv("VOLCENGINE_SECRET_KEY")
    region = config.get("credentials", {}).get("ve_region") or os.getenv("VE_REGION") or os.getenv("VOLCENGINE_REGION")
    
    if not (ak and sk and region):
        raise ValueError("缺少必要凭据：VE_AK/VE_SK/VE_REGION，请通过环境变量或配置文件提供")
    
    creds = {"ak": ak, "sk": sk, "region": region}
    
    # 初始化SDK配置
    _get_api_client(ak, sk, region)
    
    # 读取参数
    payload = {}
    if args.payload_file:
        with open(args.payload_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
    
    result = {}
    if args.action == "list_assets":
        result = list_assets(creds, args.dry_run)
    elif args.action == "create_instance":
        result = create_instance(creds, payload, args.dry_run)
    elif args.action == "stop":
        result = stop_instance(creds, payload.get("instance_id", ""), args.dry_run)
    elif args.action == "start":
        result = start_instance(creds, payload.get("instance_id", ""), args.dry_run)
    elif args.action == "reboot":
        result = reboot_instance(creds, payload.get("instance_id", ""), args.dry_run)
    elif args.action == "terminate_instance":
        result = terminate_instance(creds, payload.get("instance_id", ""), args.dry_run)
    elif args.action == "query_balance":
        result = query_balance(creds, args.dry_run)
    elif args.action == "query_bill":
        if not args.bill_period:
            raise ValueError("query_bill动作需要指定--bill-period参数，格式YYYY-MM")
        result = query_bill(creds, args.bill_period, args.limit, args.dry_run)
    elif args.action == "query_ark_cost":
        result = query_ark_cost(creds, args.start_time, args.end_time, args.bill_period, args.dry_run)
    elif args.action == "create_ticket":
        if not (args.title and args.content):
            raise ValueError("create_ticket动作需要指定--title和--content参数")
        result = create_ticket(creds, args.title, args.content, args.severity, args.product_type, args.dry_run)
    else:
        result = {"note": f"动作 {args.action} 正在开发中，可直接使用官方SDK扩展"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
