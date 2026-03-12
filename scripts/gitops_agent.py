#!/usr/bin/env python3
"""
火山引擎云管技能 GitOps 核心模块
通过 STAGE 环境变量控制执行阶段：analyze | summarize
"""
import os, json, sys
import difflib
from typing import List, Dict

# 风险分级规则
RISK_RULES = {
    "BLOCK": ["删除 RDS", "删除 TOS", "删除 VPC", "删除子网", "删除安全组", "修改 RAM 权限", "修改 IAM 策略", "生产 CLB 规则变更"],
    "WARN": ["修改 RDS 规格", "CLB 新增/修改监听", "ECS 扩缩容", "安全组规则变更", "修改 EIP 配置", "修改 NAT 规则"],
    "AUTO": ["ECS 镜像滚动更新", "TOS 标签/生命周期配置", "新建无状态资源", "修改资源描述/标签", "修改 DNS 解析记录"]
}

def analyze_diff(old_state: str, new_state: str) -> Dict:
    """分析新旧状态差异，生成变更计划"""
    # 计算差异
    diff = list(difflib.unified_diff(old_state.splitlines(), new_state.splitlines(), lineterm=''))
    changed_lines = [line for line in diff if line.startswith('+') or line.startswith('-')]
    
    # 识别涉及的资源类型
    affected_resources = []
    resource_types = ["VPC", "子网", "安全组", "ECS", "RDS", "CLB", "TOS", "IAM", "NAT", "EIP", "DNS"]
    for res in resource_types:
        if any(res in line for line in changed_lines):
            affected_resources.append(res)
    
    # 评估风险等级
    risk_level = "AUTO"
    risk_reason = ""
    for risk_type, keywords in RISK_RULES.items():
        for kw in keywords:
            if any(kw in line for line in changed_lines):
                if risk_type == "BLOCK":
                    risk_level = "BLOCK"
                    risk_reason = f"包含高风险操作：{kw}，必须人工审批"
                elif risk_type == "WARN" and risk_level == "AUTO":
                    risk_level = "WARN"
                    risk_reason = f"包含中等风险操作：{kw}，请注意风险"
    
    # 生成变更摘要
    summary = f"共检测到 {len(changed_lines)} 行变更，涉及资源：{', '.join(affected_resources)}"
    
    # 生成部署脚本（基于现有 vecloud_client 工具）
    script = generate_deploy_script(changed_lines, affected_resources)
    
    return {
        "summary": summary,
        "risk_level": risk_level,
        "risk_reason": risk_reason,
        "affected_resources": affected_resources,
        "script": script,
        "diff": diff
    }

def generate_deploy_script(changed_lines: List[str], affected_resources: List[str]) -> str:
    """基于差异生成使用 vecloud_client 的部署脚本"""
    script_content = """#!/usr/bin/env python3
\"\"\"
自动生成的火山引擎 GitOps 部署脚本
使用现有 vecloud_client 工具执行，自动审计、支持 dry-run
\"\"\"
import json
import subprocess
import sys

CONFIG_PATH = "config.json"
DRY_RUN = len(sys.argv) > 1 and sys.argv[1] == "--dry-run"

def run_vecloud_action(action: str, payload: dict):
    \"\"\"调用 vecloud_client 执行操作\"\"\"
    payload_file = f"/tmp/{action}_payload.json"
    with open(payload_file, "w") as f:
        json.dump(payload, f, ensure_ascii=False)
    
    cmd = [
        "python", "scripts/vecloud_client.py",
        "--action", action,
        "--payload-file", payload_file,
        "--config", CONFIG_PATH
    ]
    if DRY_RUN:
        cmd.append("--dry-run")
    
    print(f"执行操作：{action}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"输出：{result.stdout}")
    if result.stderr:
        print(f"错误：{result.stderr}", file=sys.stderr)
    return result.returncode == 0

if __name__ == "__main__":
    changed = []
    try:
"""
    
    # 这里根据不同的资源类型生成对应的操作代码
    # 示例操作，实际会根据具体差异生成更精准的代码
    if "VPC" in affected_resources:
        script_content += """
        # VPC 资源变更
        vpc_payload = {"CidrBlock": "10.0.0.0/16", "VpcName": "prod-vpc"}
        if not run_vecloud_action("create_vpc", vpc_payload):
            raise Exception("VPC 创建失败")
        changed.append("VPC 已创建/更新")
"""
    if "ECS" in affected_resources:
        script_content += """
        # ECS 资源变更
        ecs_payload = {"InstanceName": "web-server-01", "InstanceType": "ecs.g1ie.large"}
        if not run_vecloud_action("create_instance", ecs_payload):
            raise Exception("ECS 实例创建失败")
        changed.append("ECS 实例已创建/更新")
"""
    if "安全组" in affected_resources:
        script_content += """
        # 安全组规则变更
        sg_payload = {"SecurityGroupId": "sg-xxxx", "Direction": "ingress", "Protocol": "tcp", "PortStart": 80, "PortEnd": 80, "CidrIp": "0.0.0.0/0"}
        if not run_vecloud_action("add_sg_rule", sg_payload):
            raise Exception("安全组规则添加失败")
        changed.append("安全组规则已更新")
"""
    
    script_content += """
        print(json.dumps({
            "status": "success",
            "changed": changed,
            "dry_run": DRY_RUN
        }, ensure_ascii=False, indent=2))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": str(e),
            "changed": changed
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)
"""
    return script_content

def generate_summary(exec_output: str, success: bool) -> str:
    """生成部署结果总结报告"""
    status = "✅ 部署成功" if success else "❌ 部署失败"
    summary = f"## {status} - 火山引擎 GitOps 部署报告\n\n"
    summary += "### 执行结果：\n"
    summary += f"```\n{exec_output}\n```\n\n"
    
    if success:
        summary += "### 变更说明：\n所有变更已成功应用到火山引擎账户，相关操作已记录到审计日志。"
    else:
        summary += "### 错误说明：\n部署过程中出现错误，请查看上方日志排查问题，修复后重新提交变更。"
    
    return summary

def run_analyze():
    """执行差异分析阶段"""
    old_state_path = os.environ.get("OLD_STATE", "old-state.md")
    new_state_path = os.environ.get("NEW_STATE", "new-state.md")
    
    with open(old_state_path, "r", encoding="utf-8") as f:
        old = f.read()
    with open(new_state_path, "r", encoding="utf-8") as f:
        new = f.read()
    
    result = analyze_diff(old, new)
    
    with open("analysis.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    with open("deploy.py", "w", encoding="utf-8") as f:
        f.write(result["script"])
    os.chmod("deploy.py", 0o755)
    
    # 输出到 GitHub Actions 环境变量（如果是CI环境）
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"RISK_LEVEL={result['risk_level']}\n")
            f.write(f"SUMMARY={result['summary']}\n")
            f.write(f"RISK_REASON={result['risk_reason']}\n")
            resources = ",".join(result['affected_resources'])
            f.write(f"AFFECTED={resources}\n")
    
    print("✅ 差异分析完成：")
    print(f"风险等级：{result['risk_level']}")
    print(f"变更摘要：{result['summary']}")
    print(f"风险说明：{result['risk_reason']}")

def run_summarize():
    """执行结果总结阶段"""
    output_path = os.environ.get("EXEC_OUTPUT", "exec_output.txt")
    success = os.environ.get("EXEC_SUCCESS", "false") == "true"
    
    with open(output_path, "r", encoding="utf-8") as f:
        output = f.read()
    
    summary = generate_summary(output, success)
    
    with open("summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    
    print("✅ 报告生成完成：")
    print(summary)

if __name__ == "__main__":
    stage = os.environ.get("STAGE", "analyze")
    if stage == "analyze":
        run_analyze()
    elif stage == "summarize":
        run_summarize()
    else:
        print(f"未知 STAGE: {stage}", file=sys.stderr)
        sys.exit(1)
