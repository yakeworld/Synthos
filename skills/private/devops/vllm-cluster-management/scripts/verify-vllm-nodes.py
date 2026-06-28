#!/usr/bin/env python3
"""
vLLM 集群节点验证脚本
用法: python3 verify-vllm-nodes.py

自动验证所有节点：
1. 连通性
2. 模型一致性
3. 上下文长度一致性
"""

import json
import urllib.request
import sys

# 节点列表（从 config 读取或手动配置）
NODES = [
    ("amax", "http://100.100.252.99:8000"),
    ("amax-1", "http://100.125.10.93:8000"),
    ("amax-fallback", "http://100.82.27.51:8000"),
]

def verify_node(name, url):
    """验证单个节点"""
    try:
        req = urllib.request.Request(url + "/v1/models")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        
        models = data.get("data", [])
        if not models:
            return {"status": "ERROR", "msg": "no models returned"}
        
        m = models[0]
        return {
            "status": "OK",
            "model": m.get("id", "?"),
            "max_model_len": m.get("max_model_len", "?"),
            "owned_by": m.get("owned_by", "?"),
        }
    except Exception as e:
        return {"status": "FAIL", "msg": str(e)[:80]}

def main():
    print("=" * 60)
    print("vLLM CLUSTER VERIFICATION")
    print("=" * 60)
    
    results = []
    for name, url in NODES:
        result = verify_node(name, url)
        result["name"] = name
        result["url"] = url
        results.append(result)
    
    # 输出
    print(f"\n{'Name':15s} {'Status':8s} {'Model':20s} {'CtxLen':10s} {'URL'}")
    print("-" * 80)
    for r in results:
        status_icon = "✅" if r["status"] == "OK" else "❌"
        model = r.get("model", "")
        ctx = r.get("max_model_len", "?")
        print(f"{r['name']:15s} {r['status']:8s} {model:20s} {str(ctx):10s} {r['url']}")
        if r["status"] != "OK":
            print(f"  → {r['msg']}")
    
    # 一致性检查
    ok_results = [r for r in results if r["status"] == "OK"]
    if ok_results:
        ref_model = ok_results[0]["model"]
        ref_ctx = ok_results[0]["max_model_len"]
        
        all_consistent = all(
            r["model"] == ref_model and r["max_model_len"] == ref_ctx
            for r in ok_results
        )
        
        print()
        if all_consistent:
            print(f"✅ 全部 {len(ok_results)} 个节点模型一致: {ref_model} (ctx={ref_ctx})")
        else:
            print("❌ 模型不一致！需要排查：")
            for r in ok_results:
                if r["model"] != ref_model or r["max_model_len"] != ref_ctx:
                    print(f"  - {r['name']}: {r['model']} ctx={r['max_model_len']} (期望 {ref_model} ctx={ref_ctx})")
    
    print()
    print("=" * 60)
    
    # 输出JSON（供脚本使用）
    print(json.dumps({"results": results, "consistent": all_consistent if ok_results else False}))

if __name__ == "__main__":
    main()
