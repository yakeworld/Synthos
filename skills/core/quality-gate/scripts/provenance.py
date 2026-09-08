#!/usr/bin/env python3
"""provenance.py — 声明—来源绑定 (reward-integrity, 评审四轮 2026-09-08 重写)

四轮评审指出的直接绕过 (全部关闭):
  B1 result_file 指向目录 → open("rb") 失败 → 哈希 None → `if actual and ...` 跳过校验 → 放行
     → 修正: 必须 os.path.isfile (目录/不存在一律拒绝), 且哈希必须成功计算, 计算失败=拒绝。
  B2 file_hash 只截前缀, startswith 比较 → 1 个字符即背书
     → 修正: 只接受完整 SHA-256 (64 hex, 大小写归一), 严格相等; 短前缀/非法格式=未绑定。
  B3 七字段只查"存在且非空", 无关字段同值仍能背书
     → 修正: 声明—记录语义核验: 正文声明的 60 字符上下文必须命中该 metric 的词表
     (accuracy 类声明不能被 room_temperature 记录背书), tex_location 非空且为
     行号(可验证)或 ≥12 字符的定位片段。
  B4 删除/置 null provenance → loader 返回 None → LEGACY 降级 → 无关同值通过
     → 修正: 材料不得自行选择宽松模式。STRICT 声明 (schema.mode) 或 provenance.json
     文件存在时, provenance 字段为 null/非 dict → STRICT 空记录 (有声明必 FAIL),
     绝不落入 LEGACY。LEGACY 仅当"完全无任何 provenance 痕迹" (向后兼容冻结测试)。

绑定记录 (provenance entry) 必备字段:
  value, metric, unit, run, result_file, file_hash, tex_location
  (run 为独立执行器签发的 run receipt: 命令+退出码+输出摘要, 由执行侧写入,
   本模块只验存在性; "谁签发证据"的信任边界由 P1-3 入口 manifest 固化)

凡数必源, 源必可绑, 绑必语义一致, 不可验=拒绝 (不是跳过)。
"""
import hashlib
import json
import os
import re

REQUIRED_FIELDS = ("value", "metric", "unit", "run", "result_file", "file_hash", "tex_location")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SHA256_FILE = "filesha256:"
_SHA256_TEX = "texsha256:"

# 指标词表: 声明上下文必须命中其一 (小写, 子串匹配)。
# 原则: 宁缺勿滥 — 词表越保守, 越不可能被无关指标背书。
METRIC_VOCAB = {
    "accuracy": ("accuracy", "acc."), "precision": ("precision",),
    "recall": ("recall", "sensitivity"), "f1": ("f1",),
    "auc": ("auc", "auc-roc"), "p_value": ("p<", "p <", "p=", "p-value", "p value",
                                          "p ="),
    "n_subjects": ("n =", "n=", "enrolled", "subjects", "participants", "patients",
                   "samples", "cohort", "cases"),
    "mean": ("mean", "average", "±"), "median": ("median",),
    "std": ("std", "sd "), "confidence_interval": ("ci", "confidence interval"),
    "risk_ratio": ("hr", "odds ratio", "risk ratio", "hazard"),
    "prevalence": ("prevalence", "268 positive", "268 patients", "positive cases"),
    "best_f1": ("f1",), "best_threshold": ("threshold",),
}


def _norm(x):
    """数值归一化 (与 quality-gate-runner._norm 一致)。"""
    if isinstance(x, bool):
        return str(x).lower()
    if isinstance(x, (int, float)):
        return f"{float(x):.4f}".rstrip("0").rstrip(".")
    s = str(x).replace(" ", "")
    m = re.search(r"(\d+\.?\d*)", s)
    if m:
        return f"{float(m.group(1)):.4f}".rstrip("0").rstrip(".")
    return s.lower()


def _sha256_file(path):
    """完整 SHA-256 (小写 hex); 任何失败 → None (调用方必须按'不可验=拒绝'处理)。"""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, IOError):
        return None


def _is_valid_sha256(s):
    return isinstance(s, str) and bool(_SHA256_RE.match(s.strip().lower()))


def load_provenance(paper_dir, strict_required=False):
    """返回 (provenance_dict, mode)。mode ∈ {"LEGACY", "STRICT"}。

    模式判定 (材料不得自行降级, 评审四轮 B4):
      STRICT — 存在以下任一"provenance 痕迹", 或 strict_required=True (外部验收配置
        强制, 环境变量 SYNTHOS_PROVENANCE_MODE=STRICT — 验收侧决定, 被评估材料无权
        通过删除字段自行落入 LEGACY):
        a) provenance.json 文件存在 (paper 根 或 manuscript)
        b) state.json 含 "provenance" 键
        c) provenance.json schema 含 "mode": "STRICT"
      LEGACY — 完全无任何痕迹且未强制 (向后兼容, 冻结测试路径)。
    STRICT 下 provenance 值为 null/非 dict → 返回 ({}, "STRICT") — 空记录, 有声明必 FAIL,
    绝不落入 LEGACY。
    """
    candidates = [os.path.dirname(paper_dir), paper_dir]

    def _read_pj():
        for d in candidates:
            pj = os.path.join(d, "provenance.json")
            if os.path.exists(pj):
                try:
                    return json.load(open(pj))
                except (json.JSONDecodeError, OSError):
                    # 存在但不可解析 = 声明了溯源却不可读 → STRICT 空记录
                    return {}
        return None

    def _read_state_prov():
        for d in candidates:
            sj = os.path.join(d, "state.json")
            if os.path.exists(sj):
                try:
                    data = json.load(open(sj))
                    if isinstance(data, dict) and "provenance" in data:
                        return data
                except (json.JSONDecodeError, OSError):
                    return None
        return None

    pj = _read_pj()
    state = _read_state_prov()

    strict_declared = isinstance(pj, dict) and str(pj.get("mode", "")).upper() == "STRICT"

    # 痕迹判定: 文件存在 / state 含键 / schema 声明 STRICT / 外部验收配置强制
    if pj is not None or (state is not None and "provenance" in state) \
            or strict_declared or strict_required:
        # STRICT: 取记录
        if isinstance(pj, dict):
            recs = pj.get("provenance", pj)
        elif state is not None:
            recs = state.get("provenance")
        else:
            recs = None
        if isinstance(recs, dict):
            return recs, "STRICT"
        return {}, "STRICT"  # null/非 dict/无痕迹强制 → 空记录, 不降级 (B4)
    return None, "LEGACY"


def _hash_matches(entry, resolved_path, tex_abs):
    """file_hash 严格校验: 完整 SHA-256 相等; 支持 filesha256:/texsha256: 前缀。"""
    fh = entry.get("file_hash")
    if not isinstance(fh, str) or not fh.strip():
        return False
    fh = fh.strip()
    # 复合形式: "filesha256:<64hex> texsha256:<64hex>" (结果文件+手稿双锚定)
    m_file = re.match(r"^filesha256:([0-9a-f]{64})(?:\s+texsha256:([0-9a-f]{64}))?$", fh, re.I)
    if m_file:
        actual = _sha256_file(resolved_path)
        if actual is None:
            return False  # 不可验=拒绝 (B1)
        if actual != m_file.group(1).lower():
            return False
        if m_file.group(2):  # 手稿锚: 防止"结果文件对, 但声明文本被改"
            if not tex_abs or _sha256_file(tex_abs) != m_file.group(2).lower():
                return False
        return True
    m_tex = re.match(r"^texsha256:([0-9a-f]{64})$", fh, re.I)
    if m_tex:
        if not tex_abs or _sha256_file(tex_abs) != m_tex.group(1).lower():
            return False
        return True
    if _is_valid_sha256(fh):
        actual = _sha256_file(resolved_path)
        if actual is None:
            return False  # B1: 读取失败=拒绝, 不是跳过
        return actual == fh.lower()
    return False  # 短前缀/非法格式一律不通过 (B2)


def _tex_location_ok(loc):
    """tex_location: 行号 (1..100000) 或 ≥12 字符的定位片段。'nowhere'/空 = 拒绝。"""
    if not isinstance(loc, str):
        return False
    s = loc.strip()
    if re.fullmatch(r"\d{1,6}", s):
        return int(s) >= 1
    return len(s) >= 12


def _metric_semantic_ok(metric, claim_context):
    """声明上下文必须命中 metric 词表 (缺省词表的 metric → 拒绝, 宁严勿漏)。"""
    vocab = METRIC_VOCAB.get(str(metric).lower())
    if not vocab:
        return False
    ctx = (claim_context or "").lower()
    return any(v in ctx for v in vocab)


def _entry_complete(entry, base_dir, tex_abs=None):
    """记录完整性: 七字段 + 结果文件 isfile + 完整哈希匹配 + tex_location 有效。"""
    if not isinstance(entry, dict):
        return False
    for f in REQUIRED_FIELDS:
        if f not in entry or entry[f] in (None, ""):
            return False
    if not _tex_location_ok(entry["tex_location"]):
        return False
    rf = entry["result_file"]
    if not isinstance(rf, str):
        return False
    resolved = None
    for base in (base_dir, os.path.dirname(base_dir)):
        p = rf if os.path.isabs(rf) else os.path.join(base, rf)
        if os.path.isfile(p):  # B1: 目录/不存在 → 继续找; 都没有 → 拒绝
            resolved = p
            break
    if resolved is None:
        return False
    return _hash_matches(entry, resolved, tex_abs)


def is_bound(claim, provenance, base_dir, claim_context="", tex_abs=None):
    """声明 claim (归一化数值或原文) 是否被某条完整且语义一致的记录背书。"""
    if not provenance:
        return False
    target = _norm(claim)
    for entry in provenance.values():
        if _norm(entry.get("value")) != target:
            continue
        if not _entry_complete(entry, base_dir, tex_abs):
            continue
        if not _metric_semantic_ok(entry.get("metric"), claim_context):
            continue
        return True
    return False


def bound_claims(claims, provenance, base_dir, contexts=None, tex_abs=None):
    """claims: list; contexts: 与 claims 等长的正文上下文片段 list。"""
    contexts = contexts or ["" for _ in claims]
    return [c for c, ctx in zip(claims, contexts) if is_bound(c, provenance, base_dir, ctx, tex_abs)]


def unbound_claims(claims, provenance, base_dir, contexts=None, tex_abs=None):
    b = bound_claims(claims, provenance, base_dir, contexts, tex_abs)
    out = []
    for c in claims:
        if c in b:
            b.remove(c)  # 按出现次数移除, 与 bound 的多重集合语义一致
        else:
            out.append(c)
    return out


def verify_entry(entry, base_dir, tex_abs=None):
    """独立校验单条记录 (供 run receipt 生成器/审计用)。返回 (bool, reason)。"""
    if not isinstance(entry, dict):
        return False, "entry not a dict"
    for f in REQUIRED_FIELDS:
        if f not in entry or entry[f] in (None, ""):
            return False, f"missing field {f}"
    if not _tex_location_ok(entry["tex_location"]):
        return False, "tex_location invalid"
    rf = entry["result_file"]
    resolved = None
    for base in (base_dir, os.path.dirname(base_dir)):
        p = rf if os.path.isabs(rf) else os.path.join(base, rf)
        if os.path.isfile(p):
            resolved = p
            break
    if resolved is None:
        return False, f"result_file not a regular file: {rf}"
    if not _hash_matches(entry, resolved, tex_abs):
        return False, "file_hash mismatch or invalid"
    return True, "ok"
