#!/usr/bin/env python3
"""provenance.py — 声明—来源绑定 (reward-integrity P1, 评审三轮 2026-09-07)

L0.5 旧实现的本质局限: 只做"数值集合成员检查" — 无关字段里的同值数字
(如 state.json 的 room_temperature: 85.2) 能背书正文 "Accuracy 85.2%"。
本模块提供"声明—来源绑定": 一个数值声明只有在 state.json 里存在一条
携带完整溯源元数据的记录时, 才算被证据支撑 (而非仅同值命中)。

绑定记录 (provenance entry) 必备字段 (缺一即"未绑定"):
  value         数值 (与声明匹配)
  metric        指标名 (accuracy / p_value / n_subjects ...)
  unit          单位 (% / 无 / s ...)
  run           分析运行标识 (可复现的脚本/命令或 run id)
  result_file   结果文件路径 (相对 paper 根, 必须真实存在)
  file_hash     结果文件 sha256 前缀 (>=16 hex), 防"事后改数据"
  tex_location  tex 中该声明的定位 (行号或上下文片段)

模式:
  - 存在 provenance (provenance.json 或 state.json["provenance"]) → STRICT:
    每个可核对声明必须命中一条"完整绑定"记录; 无关字段同值不算数。
  - 不存在 → LEGACY: 退化为旧集合成员检查 (向后兼容, 冻结测试不变)。

运行无副作用, 纯只读。凡数必源, 源必可绑。
"""
import hashlib
import json
import os

REQUIRED_FIELDS = ("value", "metric", "unit", "run", "result_file", "file_hash", "tex_location")


def _norm(x):
    """与 quality-gate-runner.py 的 _norm 保持一致的数值归一化。"""
    if isinstance(x, bool):
        return str(x).lower()
    if isinstance(x, (int, float)):
        return f"{float(x):.4f}".rstrip("0").rstrip(".")
    import re
    s = str(x).replace(" ", "")
    m = re.search(r"(\d+\.?\d*)", s)
    if m:
        return f"{float(m.group(1)):.4f}".rstrip("0").rstrip(".")
    return s.lower()


def _sha256_prefix(path, n=16):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()[:n]
    except (OSError, IOError):
        return None


def load_provenance(paper_dir):
    """返回 provenance 记录 dict (metric -> entry)。

    查找顺序:
      1. <paper_dir>/../provenance.json   (论文根, 与 state.json 同级)
      2. <paper_dir>/provenance.json      (manuscript 目录)
      3. state.json 顶层 "provenance" 字段 (论文根 或 manuscript)
    找不到任何来源 → 返回 None (LEGACY 模式)。找到 (即使为空 dict) → 返回 dict (STRICT 模式)。
    """
    candidates_dir = [os.path.dirname(paper_dir), paper_dir]
    for d in candidates_dir:
        pj = os.path.join(d, "provenance.json")
        if os.path.exists(pj):
            try:
                data = json.load(open(pj))
                if isinstance(data, dict):
                    return data.get("provenance", data)
            except (json.JSONDecodeError, OSError):
                return {}
    # state.json 内嵌
    for d in candidates_dir:
        sj = os.path.join(d, "state.json")
        if os.path.exists(sj):
            try:
                data = json.load(open(sj))
                if isinstance(data, dict) and "provenance" in data:
                    prov = data["provenance"]
                    return prov if isinstance(prov, dict) else {}
            except (json.JSONDecodeError, OSError):
                return {}
    return None


def _entry_complete(entry, base_dir):
    """一条记录是否具备全部溯源字段, 且结果文件真实存在 + 哈希匹配。"""
    if not isinstance(entry, dict):
        return False
    for field in REQUIRED_FIELDS:
        if field not in entry or entry[field] in (None, ""):
            return False
    # result_file 必须真实存在
    rf = entry["result_file"]
    for base in (base_dir, os.path.dirname(base_dir)):
        p = rf if os.path.isabs(rf) else os.path.join(base, rf)
        if os.path.exists(p):
            declared = str(entry.get("file_hash", ""))[:16]
            if declared:
                actual = _sha256_prefix(p)
                if actual and not actual.startswith(declared):
                    return False  # 哈希不匹配 = 数据被事后改动
            return True
    return False  # 结果文件不存在


def is_bound(claim, provenance, base_dir):
    """声明 claim 是否被某条完整绑定记录支撑。"""
    if not provenance:
        return False
    target = _norm(claim)
    for entry in provenance.values():
        if _norm(entry.get("value")) == target and _entry_complete(entry, base_dir):
            return True
    return False


def bound_claims(claims, provenance, base_dir):
    """返回 claims 中被绑定的子集 (list)。"""
    return [c for c in claims if is_bound(c, provenance, base_dir)]


def unbound_claims(claims, provenance, base_dir):
    """返回 claims 中未被绑定的子集 (list)。"""
    return [c for c in claims if not is_bound(c, provenance, base_dir)]
