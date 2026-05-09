"""
【安全应急演练】AK/SK 泄露场景 - 模拟正常业务代码中调用阿里云服务
⚠️ 仅用于安全应急演练
"""

import json
import hmac
import hashlib
import base64
import urllib.parse
import uuid
from datetime import datetime, timezone

import requests



AK = "LTAI5t9uNBJMTX5SZdfwsD1d"
SK = "Bp4qsYqYG4wKHG1DkQohLIpU6XzXn8"


def sign(method, params, secret):
    """阿里云 API 签名"""
    sorted_params = sorted(params.items())
    query_string = "&".join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
        for k, v in sorted_params
    )
    string_to_sign = f"{method}&{urllib.parse.quote('/', safe='')}&{urllib.parse.quote(query_string, safe='')}"
    h = hmac.new(
        (secret + "&").encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha1,
    )
    return base64.b64encode(h.digest()).decode("utf-8")


def call_api(action, extra_params=None, endpoint="ecs.aliyuncs.com", version="2014-05-26"):
    """通用阿里云 API 调用封装"""
    params = {
        "Format": "JSON",
        "Version": version,
        "AccessKeyId": AK,
        "SignatureMethod": "HMAC-SHA1",
        "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "SignatureVersion": "1.0",
        "SignatureNonce": str(uuid.uuid4()),
        "Action": action,
    }
    if extra_params:
        params.update(extra_params)

    params["Signature"] = sign("GET", params, SK)

    resp = requests.get(f"https://{endpoint}/", params=params, timeout=10)
    return resp.json()


# ===== 业务场景1: 运维平台 - 查询服务器运行状态 =====
def query_ecs_status(region_id="cn-beijing"):
    """运维平台定时检查 ECS 实例健康状态"""
    print("[运维平台] 查询 ECS 实例状态...")
    result = call_api("DescribeInstances", {"RegionId": region_id})
    print(f"  响应: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
    return result


# ===== 业务场景2: 业务系统 - 查询可用地域及产品 =====
def query_available_regions():
    """业务系统初始化时查询可用地域列表"""
    print("[业务系统] 查询可用地域列表...")
    result = call_api("DescribeRegions")
    print(f"  响应: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
    return result


# ===== 业务场景3: 日志服务 - 查询操作日志 =====
def query_action_trail():
    """审计系统拉取最近操作日志"""
    print("[审计系统] 查询操作审计日志...")
    result = call_api(
        "LookupEvents",
        endpoint="actiontrail.aliyuncs.com",
        version="2020-07-06",
    )
    print(f"  响应: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
    return result


# ===== 业务场景4: 费用中心 - 查询账单概览 =====
def query_billing_summary():
    """财务系统定时拉取账单数据"""
    print("[财务系统] 查询当月账单概览...")
    now = datetime.now()
    result = call_api(
        "QueryAccountBill",
        {
            "BillingCycle": f"{now.year}-{now.month:02d}",
        },
        endpoint="billing.aliyuncs.com",
        version="2017-12-14",
    )
    print(f"  响应: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
    return result


def main():
    print("=" * 60)
    print("【应急演练】模拟正常业务代码中 AK/SK 的调用过程")
    print(f"演练时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    query_ecs_status()
    query_available_regions()
    query_action_trail()
    query_billing_summary()

    print("\n" + "=" * 60)
    print("以上为正常业务代码中典型的 AK/SK 调用场景")
    print("演练结束")
    print("=" * 60)


if __name__ == "__main__":
    main()
