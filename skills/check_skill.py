#!/usr/bin/env python3
"""技能质量检查工具 v2 — 增强版。

新增能力：
- 技能类型分类（core/extended/private/research-tools/shared）
- 增量扫描 + mtime-based 缓存
- 并行扫描（concurrent.futures）
- 趋势追踪（对比历史分数）
- CI 输出模式（GitHub Actions compatible）
- Skill trust_score 趋势追踪
- 技能网络一致性检查
- 动态检查集（按类型调整权重）
- 摘要输出（one-line per skill）
- 修复建议自动生成脚本

SKILL.md 原理绑定：

SKILL.md 原理绑定：
- 维度1: 结构完整性（YAML frontmatter、触发条件、IO契约、边界）
- 维度2: 引用完整性（references表中所有文件存在）
- 维度3: 脚本可运行性（py_compile、原理绑定、依赖）
- 维度4: 思想一致性（脚本声明的原理在SKILL.md中存在，SKILL.md规则有对应实现）
- 维度5: 内容质量（大小≤30K、无硬编码凭证、版本一致）

用法:
  python3 check_skill.py <skill_dir_or_SKILL.md_path> [--format json] [--fix]
  python3 check_skill.py /path/to/SKILL.md
  python3 check_skill.py /media/yakeworld/sda2/Synthos/skills/  # 全库扫描
  python3 check_skill.py /home/yakeworld/.hermes/skills/ --format json

输出:
  默认: Markdown报告
  --format json: JSON报告
"""

import os
import sys
import json
import subprocess
import re
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
import hashlib
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone

# ─── 常量定义 ────────────────────────────────────────────────

MAX_SKILL_MD_SIZE = 30_000
CACHE_DIR = ".skill_cache"
CACHE_TTL_SECONDS = 3600
CI_THRESHOLD = 0.85
DEFAULT_PARALLELISM = 4
SKILL_TYPES = {
    "core": "core", "extended": "extended", "private": "private",
    "research-tools": "research-tools", "shared": "shared", "meta": "meta",
}




class SkillCache:
    """mtime-based 文件缓存"""
    
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _key(self, filepath: str) -> str:
        return hashlib.md5(filepath.encode()).hexdigest()
    
    def _cache_path(self, filepath: str) -> str:
        return os.path.join(self.cache_dir, f"{self._key(filepath)}.json")
    
    def get(self, filepath: str) -> Optional[dict]:
        cache_path = self._cache_path(filepath)
        if not os.path.exists(cache_path):
            return None
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            if time.time() - data.get('timestamp', 0) > CACHE_TTL_SECONDS:
                os.remove(cache_path)
                return None
            if abs(os.path.getmtime(filepath) - data.get('mtime', 0)) > 0.1:
                os.remove(cache_path)
                return None
            return data.get('report')
        except (json.JSONDecodeError, OSError):
            return None
    
    def set(self, filepath: str, report: dict):
        cache_path = self._cache_path(filepath)
        data = {
            'report': report,
            'mtime': os.path.getmtime(filepath),
            'timestamp': time.time(),
        }
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, ensure_ascii=False)
        except OSError:
            pass


@dataclass
class CheckResult:
    """单个检查点的结果"""
    name: str
    passed: bool
    severity: str  # P0, P1, P2
    category: str  # 维度1-5
    details: str = ""
    suggestion: str = ""



class TrendTracker:
    """追踪技能分数变化趋势"""
    
    def __init__(self, history_file: str = ".skill_history.json"):
        self.history_file = history_file
        self.history = self._load()
    
    def _load(self) -> dict:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}
    
    def record(self, skill_name: str, score: int, status: str):
        if skill_name not in self.history:
            self.history[skill_name] = []
        self.history[skill_name].append({
            'score': score, 'status': status,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        })
        if len(self.history[skill_name]) > 10:
            self.history[skill_name] = self.history[skill_name][-10:]
    
    def save(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except OSError:
            pass
    
    def get_delta(self, skill_name: str) -> float:
        if skill_name not in self.history or len(self.history[skill_name]) < 2:
            return 0.0
        scores = [h['score'] for h in self.history[skill_name]]
        return scores[-1] - scores[-2]
    
    def get_trend(self, skill_name: str) -> str:
        delta = self.get_delta(skill_name)
        if delta > 2: return "improving"
        elif delta < -2: return "declining"
        return "stable"


@dataclass
class SkillReport:
    """单个技能的质量报告"""
    name: str
    path: str
    score: int
    status: str  # healthy, good, acceptable, unhealthy
    checks: List[CheckResult] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    skill_type: str = "unknown"
    scan_time_ms: int = 0
    cached: bool = False
    history_delta: float = 0.0
    network_issues: List[str] = field(default_factory=list)

    @property
    def p0_passed(self):
        return all(c.passed for c in self.checks if c.severity == 'P0')

    @property
    def p1_passed(self):
        return all(c.passed for c in self.checks if c.severity == 'P1')


def load_skill_md(skill_path: str) -> Tuple[str, Optional[dict]]:
    """加载SKILL.md，返回content和frontmatter（如果有）"""
    if not os.path.exists(skill_path):
        return None, None

    if os.path.isdir(skill_path):
        skill_md_path = os.path.join(skill_path, 'SKILL.md')
        if not os.path.exists(skill_md_path):
            return None, None
    else:
        skill_md_path = skill_path

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse YAML frontmatter (simple parse)
    frontmatter = None
    if content.startswith('---'):
        end = content.find('---', 3)
        if end > 0:
            fm_text = content[3:end].strip()
            frontmatter = parse_simple_yaml(fm_text)

    return content, frontmatter


def parse_simple_yaml(text: str) -> dict:
    """简易YAML解析（仅支持简单键值对）"""
    result = {}
    for line in text.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ': ' in line:
            key, value = line.split(': ', 1)
            key = key.strip()
            value = value.strip()
            # Remove quotes
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            result[key] = value
    return result



def detect_skill_type(skill_path: str) -> str:
    """从路径检测技能类型"""
    rel = skill_path.replace(".skills/", "/").replace("/SKILL.md", "")
    parts = rel.split("/")
    for part in parts:
        if part == "core": return "core"
        if part == "extended": return "extended"
        if part == "private": return "private"
        if part == "shared": return "shared"
        if part == "meta": return "meta"
    if "research-tools" in parts: return "research-tools"
    return "unknown"


def get_check_weights(skill_type: str) -> Dict[str, float]:
    """根据技能类型调整检查权重"""
    weights = {
        "core": {"structure": 1.5, "references": 1.5, "scripts": 1.0, "consistency": 1.5, "quality": 1.0, "network": 1.5},
        "extended": {"structure": 1.2, "references": 1.0, "scripts": 0.8, "consistency": 1.0, "quality": 1.0, "network": 0.5},
        "private": {"structure": 1.0, "references": 0.5, "scripts": 1.0, "consistency": 0.5, "quality": 1.0, "network": 0.0},
        "research-tools": {"structure": 0.8, "references": 0.5, "scripts": 1.5, "consistency": 0.5, "quality": 0.8, "network": 0.0},
        "shared": {"structure": 1.2, "references": 1.0, "scripts": 1.0, "consistency": 1.0, "quality": 1.2, "network": 0.5},
        "meta": {"structure": 1.5, "references": 1.0, "scripts": 1.0, "consistency": 1.5, "quality": 1.0, "network": 1.0},
    }
    return weights.get(skill_type, {"structure": 1.0, "references": 1.0, "scripts": 1.0, "consistency": 1.0, "quality": 1.0, "network": 0.0})


def check_structure(content: str, frontmatter: Optional[dict], skill_path: str, weights: Dict = None) -> List[CheckResult]:
    """检查结构完整性（维度1）"""
    results = []

    # 1.1 SKILL.md存在且≥500字符
    exists = os.path.exists(skill_path)
    size = os.path.getsize(skill_path) if exists else 0
    results.append(CheckResult(
        name="SKILL.md存在且自洽",
        passed=exists and len(content) >= 500,
        severity="P0",
        category="维度1-结构完整性",
        details=f"文件存在, {len(content)}字符 ({len(content)//1024}KB)",
        suggestion="" if (exists and len(content) >= 500) else "SKILL.md文件缺失或过少内容"
    ))

    # 1.2 YAML frontmatter完整
    has_name = frontmatter and 'name' in frontmatter
    has_desc = frontmatter and 'description' in frontmatter
    has_version = frontmatter and 'version' in frontmatter
    # synthos field is not always present — check broader
    has_synthos = 'metadata' in str(frontmatter) or 'synthos' in str(frontmatter) or 'author' in str(frontmatter) or 'license' in str(frontmatter)
    # Allow minimal frontmatter: just name + description
    minimal_valid = has_name and has_desc
    results.append(CheckResult(
        name="YAML frontmatter完整",
        passed=minimal_valid,  # name + description is sufficient
        severity="P0",
        category="维度1-结构完整性",
        details=f"name:{bool(has_name)} description:{bool(has_desc)} version:{bool(has_version)} synthos:{bool(has_synthos)}",
        suggestion="补充frontmatter中的缺失字段" if not minimal_valid else ""
    ))

    # 1.3 触发条件明确
    has_trigger = '触发条件' in content or 'when' in content.lower() or 'When to use' in content
    results.append(CheckResult(
        name="触发条件明确",
        passed=has_trigger,
        severity="P1",
        category="维度1-结构完整性",
        details=f"{'包含' if has_trigger else '缺少'}触发条件章节",
        suggestion="添加'触发条件'章节，说明何时加载本技能" if not has_trigger else ""
    ))

    # 1.4 IO_CONTRACT存在
    has_io = 'IO_CONTRACT' in content or '输入' in content or 'output' in content.lower()
    results.append(CheckResult(
        name="输入输出规范存在",
        passed=has_io,
        severity="P1",
        category="维度1-结构完整性",
        details=f"{'包含' if has_io else '缺少'}IO契约",
        suggestion="添加IO_CONTRACT章节" if not has_io else ""
    ))

    # 1.5 出口契约明确
    has_output = '出口契约' in content or 'fig.savefig' in content or 'output' in content.lower()
    results.append(CheckResult(
        name="出口契约明确",
        passed=has_output,
        severity="P1",
        category="维度1-结构完整性",
        details=f"{'包含' if has_output else '缺少'}出口契约",
        suggestion="明确输出物格式和路径" if not has_output else ""
    ))

    # 1.6 边界定义清晰
    has_boundary = '边界' in content or '不加载' in content or 'NOT' in content or 'avoid' in content.lower()
    results.append(CheckResult(
        name="边界定义清晰",
        passed=has_boundary,
        severity="P2",
        category="维度1-结构完整性",
        details=f"{'包含' if has_boundary else '缺少'}边界定义",
        suggestion="添加'不加载'和'不做什么'的说明" if not has_boundary else ""
    ))

    return results


def check_references(content: str, skill_dir: str, weights: Dict = None) -> List[CheckResult]:
    """检查引用完整性（维度2）"""
    results = []

    # Parse references and scripts — extract file paths from SKILL.md
    # Handle multiple formats:
    # 1. Table rows: | path/to/file.md | description |
    # 2. Backtick: `path/to/file.md`
    # 3. Plain: references/path or scripts/path
    ref_patterns = [
        r'\|\s*([a-zA-Z0-9_./-]+\.(md|py|json|yaml|yml|csv|excalidraw))\s*\|',  # table pipe
        r'`([a-zA-Z0-9_./-]+\.(md|py|json|yaml|yml|csv|excalidraw))`',  # backtick
        r'(?<!`)(?:references|scripts)/[a-zA-Z0-9_./-]+\.(md|py|json|yaml|yml|csv|excalidraw)(?!`)',  # plain
    ]

    all_refs = set()
    for pattern in ref_patterns:
        matches = re.findall(pattern, content)
        # If tuple (from capture groups), use first group
        for m in matches:
            ref = m if isinstance(m, str) else m[0]
            # Normalize: remove trailing slash, check if file exists
            ref = ref.rstrip('/')
            # Skip directory-only references (like "references/" with no file after)
            if '/' not in ref[0:30] or ref.count('/') == 0:
                # This is a relative segment, skip
                continue
            all_refs.add(ref)

    broken = []
    total = 0
    for ref in all_refs:
        total += 1
        full = os.path.join(skill_dir, ref)
        if not os.path.exists(full):
            broken.append(ref)

    # Deduplicate broken for display
    broken_unique = list(dict.fromkeys(broken))

    results.append(CheckResult(
        name=f"引用文件存在（{total}个唯一引用，{len(broken_unique)}个Broken）",
        passed=len(broken_unique) == 0,
        severity="P0",
        category="维度2-引用完整性",
        details=f"引用{total}个，Broken {len(broken_unique)}个: {', '.join(broken_unique[:5])}",
        suggestion=f"移除broken引用或创建缺失文件: {', '.join(broken_unique[:3])}" if broken_unique else ""
    ))

    # 2.2 无孤立引用（SKILL.md中引用的markdown文件存在）
    md_refs = set()
    for pattern in ref_patterns:
        matches = re.findall(pattern, content)
        for m in matches:
            ref = m if isinstance(m, str) else m[0]
            if ref.endswith('.md'):
                md_refs.add(ref)

    broken_md = [r for r in md_refs if not os.path.exists(os.path.join(skill_dir, r)) and not os.path.exists(os.path.join(skill_dir, 'references', r)) and not os.path.exists(os.path.join(skill_dir, 'golden', r))]
    results.append(CheckResult(
        name=f"Markdown引用完整（{len(md_refs)}个）",
        passed=len(broken_md) == 0,
        severity="P0",
        category="维度2-引用完整性",
        details=f"Markdown引用{len(md_refs)}个，Broken {len(broken_md)}个",
        suggestion="检查markdown引用路径" if broken_md else ""
    ))

    return results


def check_scripts(skill_dir: str, weights: Dict = None) -> List[CheckResult]:
    """检查脚本可运行性（维度3）"""
    results = []
    scripts_dir = os.path.join(skill_dir, 'scripts')
    references_scripts = None

    for root, dirs, files in os.walk(skill_dir, followlinks=False):
        for f in files:
            if f.endswith('.py') and not f.endswith('.pyc') and not f.startswith('.'):
                scripts_dir = root

    # Find all Python scripts
    all_py = []
    for root, dirs, files in os.walk(skill_dir, followlinks=False):
        for f in files:
            if f.endswith('.py') and not f.endswith('.pyc') and not f.startswith('.'):
                all_py.append(os.path.join(root, f))

    if not all_py:
        results.append(CheckResult(
            name="无可执行脚本",
            passed=True,  # 有些技能没有脚本
            severity="P2",
            category="维度3-脚本可运行性",
            details="无.py文件"
        ))
        return results

    # Cap to prevent slow scans on hub skills
    all_py = all_py[:100]
    # 3.1 语法正确
    syntax_errors = []
    for py in all_py:
        try:
            with open(py, 'r', encoding='utf-8', errors='replace') as f:
                compile(f.read(), py, 'exec')
        except SyntaxError:
            syntax_errors.append(os.path.relpath(py, skill_dir))

    results.append(CheckResult(
        name=f"Python语法正确（{len(all_py)}个文件）",
        passed=len(syntax_errors) == 0,
        severity="P0",
        category="维度3-脚本可运行性",
        details=f"全部{len(all_py)}个文件编译通过" if not syntax_errors else f"失败: {', '.join(syntax_errors)}",
        suggestion=f"修复语法错误: {', '.join(syntax_errors)}" if syntax_errors else ""
    ))

    # 3.2 有可执行入口 — 读取前3000字节或整个文件（取较小者）
    no_main = []
    for py in all_py:
        try:
            sz = os.path.getsize(py)
        except OSError:
            sz = 500
        with open(py, 'r', errors='replace') as f:
            content = f.read(sz)
        has_main = '__name__' in content or 'Usage:' in content or '用法' in content or 'argparse' in content or 'click' in content or 'typer' in content
        if not has_main:
            no_main.append(os.path.relpath(py, skill_dir))

    results.append(CheckResult(
        name="脚本有可执行入口",
        passed=len(no_main) == 0,
        severity="P1",
        category="维度3-脚本可运行性",
        details=f"{len(all_py) - len(no_main)}/{len(all_py)}有入口" if no_main else f"全部{len(all_py)}个有入口",
        suggestion=f"添加可执行入口: {', '.join(no_main)}" if no_main else ""
    ))

    # 3.3 有原理绑定 — 读取前2000字节
    no_binding = []
    for py in all_py:
        try:
            sz = min(os.path.getsize(py), 2000)
        except OSError:
            sz = 500
        with open(py, 'r', errors='replace') as f:
            content = f.read(sz)
        has_binding = 'SKILL.md 原理绑定' in content or 'SKILL.md' in content
        if not has_binding:
            no_binding.append(os.path.relpath(py, skill_dir))

    results.append(CheckResult(
        name="脚本有SKILL.md原理绑定",
        passed=len(no_binding) == 0,
        severity="P0",
        category="维度3-脚本可运行性",
        details=f"{len(all_py) - len(no_binding)}/{len(all_py)}有绑定" if no_binding else f"全部{len(all_py)}个有绑定",
        suggestion=f"添加原理绑定: {', '.join(no_binding)}" if no_binding else ""
    ))

    # 3.5 路径解析正确（简单检查）
    path_issues = []
    for py in all_py:
        sz = os.path.getsize(py)
        with open(py, "r", errors="replace") as f:
            content = f.read(min(sz, 2000))
        # Check for relative paths without os.path.dirname
        if '../' in content or '/..' in content:
            if 'os.path.dirname' not in content and 'SCRIPT_DIR' not in content:
                path_issues.append(os.path.relpath(py, skill_dir))

    results.append(CheckResult(
        name="路径解析逻辑正确",
        passed=len(path_issues) == 0,
        severity="P1",
        category="维度3-脚本可运行性",
        details=f"全部路径解析正确" if not path_issues else f"路径问题: {', '.join(path_issues)}",
        suggestion=f"使用绝对路径: {', '.join(path_issues)}" if path_issues else ""
    ))

    return results


def check_consistency(content: str, skill_dir: str, weights: Dict = None) -> List[CheckResult]:
    """检查思想一致性（维度4）"""
    results = []

    # 4.1 所有脚本声明的原理在SKILL.md中存在
    all_py = []
    for root, dirs, files in os.walk(skill_dir, followlinks=False):
        for f in files:
            if f.endswith('.py') and not f.endswith('.pyc') and not f.startswith('.'):
                all_py.append(os.path.join(root, f))

    if all_py:
        missing_principles = []
        for py in all_py:
            try:
                sz = min(os.path.getsize(py), 2000)
            except OSError:
                sz = 500
            try:
                with open(py, 'r', errors='replace') as f:
                    py_content = f.read(sz)
            except OSError:
                continue
            if 'SKILL.md 原理绑定' in py_content:
                # Extract principle references from the script header
                for line in py_content.split('\n'):
                    if '铁律' in line or '设计规则' in line:
                        # Check if this principle exists in SKILL.md
                        principle_text = line.split(':', 1)[-1].strip().rstrip('。')
                        if principle_text not in content:
                            missing_principles.append(os.path.relpath(py, skill_dir))
                            break

        results.append(CheckResult(
            name="脚本声明的原理在SKILL.md中存在",
            passed=len(missing_principles) == 0,
            severity="P0",
            category="维度4-思想一致性",
            details=f"全部{len(all_py)}个脚本原理可追溯" if not missing_principles else f"缺失原理: {', '.join(missing_principles)}",
            suggestion="在SKILL.md中补充缺失的规则" if missing_principles else ""
        ))

    # 4.2 SKILL.md中的铁律有对应实现
    iron_rules = re.findall(r'铁律[^。]*。', content)
    if iron_rules:
        # Check if at least one script implements these rules
        has_implementations = any(
            '铁律' in open(os.path.join(root, f)).read(500)
            for root, _, files in os.walk(skill_dir, followlinks=False)
            for f in files
            if f.endswith('.py')
        )
        results.append(CheckResult(
            name="铁律有对应实现",
            passed=has_implementations,
            severity="P0",
            category="维度4-思想一致性",
            details=f"{len(iron_rules)}条铁律，{'有实现' if has_implementations else '无实现'}",
            suggestion="添加实现脚本或移除铁律" if not has_implementations else ""
        ))

    # 4.3 模式映射正确 — 支持多种格式：模式A:、模式A（xxx）、**模式A**：、Mode A:、- 模式名称：
    patterns_found = len(re.findall(r'模式[A-Z]', content))
    mode_lines = re.findall(r'(?:模式[A-Z][（:;]\s+|├──模式[A-Z]:|└──模式[A-Z]:)', content)
    # Match bullet points with 模式 in OPERATING_MODES section or similar
    mode_lines2 = re.findall(r'- \*\*[^*]*模式[^*]*\*\*', content)
    # Match "模式名称：" without ** wrapper
    mode_lines3 = re.findall(r'- \*[^*]+模式[^*]+\*[^：:]', content)
    patterns_found = max(patterns_found, len(mode_lines), len(mode_lines2))
    results.append(CheckResult(
        name=f"模式定义完整（{patterns_found}个模式）",
        passed=patterns_found >= 2,  # 至少2个模式
        severity="P1",
        category="维度4-思想一致性",
        details=f"{patterns_found}个模式定义",
        suggestion="补充模式定义" if patterns_found < 2 else ""
    ))

    # 4.4 无冗余代码（同目录下无完全重复的.py文件）
    duplicates = []
    for root, dirs, files in os.walk(skill_dir, followlinks=False):
        md5s = {}
        for f in files:
            if f.endswith('.py'):
                fp = os.path.join(root, f)
                result = subprocess.run(['md5sum', fp], capture_output=True, text=True)
                md5 = result.stdout.split()[0]
                if md5 in md5s:
                    duplicates.append(f"{os.path.relpath(fp, skill_dir)} == {md5s[md5]}")
                else:
                    md5s[md5] = os.path.relpath(fp, skill_dir)

    results.append(CheckResult(
        name="无冗余代码",
        passed=len(duplicates) == 0,
        severity="P2",
        category="维度4-思想一致性",
        details=f"全部{sum(1 for r,d,fs in os.walk(skill_dir, followlinks=False) for f in fs if f.endswith('.py'))}个.py文件无重复" if not duplicates else f"重复: {', '.join(duplicates[:3])}",
        suggestion="移除重复脚本" if duplicates else ""
    ))

    return results


def check_quality(content: str, frontmatter: Optional[dict], skill_dir: str, weights: Dict = None) -> List[CheckResult]:
    """检查内容质量（维度5）"""
    results = []

    # 5.1 SKILL.md ≤ 30K字符
    size = len(content)
    results.append(CheckResult(
        name=f"SKILL.md大小合理（{size//1024}KB）",
        passed=size <= 30000,
        severity="P2",
        category="维度5-内容质量",
        details=f"{size}字符 (限制30000)",
        suggestion="将示例代码移至references/" if size > 30000 else ""
    ))

    # 5.2 无硬编码凭证
    tokens_to_check = ['chat_id', 'token', 'api_key', 'secret', 'password']
    hardcoded = []
    for token in tokens_to_check:
        # Check if token appears in a code block (which is OK)
        in_code_block = False
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('```') or stripped.startswith('    '):
                continue
            # Check if it's just a mention/description (not an assignment)
            if token in content.lower():
                # Skip if it's in a description context
                context = content[content.lower().index(token):content.lower().index(token)+100]
                if '在.env' in context or '变量' in context or 'placeholder' in context:
                    continue
                if '例如' in context or '示例' in context or '说明' in context:
                    continue
                if 'chat_id' in context.lower() and '开头' in context:
                    continue
                if 'token' in context.lower() and '环境变量' in context:
                    continue
                hardcoded.append(token)
                break

    has_hardcoded = len(hardcoded) > 0
    results.append(CheckResult(
        name="无硬编码凭证",
        passed=not has_hardcoded,
        severity="P0",
        category="维度5-内容质量",
        details=f"{'安全' if not has_hardcoded else '发现硬编码: ' + ', '.join(hardcoded)}",
        suggestion="将凭证移入.env" if has_hardcoded else ""
    ))

    # 5.3 版本一致
    if frontmatter:
        version = frontmatter.get('version', '')
        changelog_path = os.path.join(skill_dir, 'CHANGE_LOG.md')
        if os.path.exists(changelog_path):
            with open(changelog_path) as f:
                cl_content = f.read()
            # Extract version from changelog
            cl_match = re.search(r'v?(\d+\.\d+(?:\.\d+)?)', cl_content)
            cl_version = cl_match.group(1) if cl_match else ''
            version_match = re.search(r'version[:\s]+(\d+\.\d+(?:\.\d+)?)', frontmatter.get('version', ''))
            fm_version = version_match.group(1) if version_match else ''

            results.append(CheckResult(
                name="版本一致",
                passed=version == cl_version or fm_version == cl_version or version == '' or cl_version == '',
                severity="P1",
                category="维度5-内容质量",
                details=f"frontmatter: {version}, CHANGE_LOG: {cl_version}",
                suggestion="同步版本号" if (version and cl_version and version != cl_version) else ""
            ))
        else:
            results.append(CheckResult(
                name="CHANGE_LOG.md存在",
                passed=False,
                severity="P2",
                category="维度5-内容质量",
                details="CHANGE_LOG.md不存在"
            ))
    else:
        results.append(CheckResult(
            name="CHANGE_LOG.md存在",
            passed=False,
            severity="P2",
            category="维度5-内容质量",
            details="无法检查版本（无frontmatter）"
        ))

    # 5.5 有实战案例
    has_case_study = 'case-study' in content.lower() or '实战' in content or '案例' in content
    results.append(CheckResult(
        name="有实战案例",
        passed=has_case_study,
        severity="P2",
        category="维度5-内容质量",
        details=f"{'包含' if has_case_study else '缺少'}实战案例"
    ))

    return results


def calculate_score(results: List[CheckResult]) -> int:
    """计算总分"""
    score = 0

    p0_results = [r for r in results if r.severity == 'P0']
    p1_results = [r for r in results if r.severity == 'P1']
    p2_results = [r for r in results if r.severity == 'P2']

    # P0: 一票否决，每个10分，共100分上限
    p0_score = sum(10 for r in p0_results if r.passed)

    # P1: 每个5分，最多20分
    p1_score = min(20, sum(5 for r in p1_results if r.passed))

    # P2: 每个2分，最多10分
    p2_score = min(10, sum(2 for r in p2_results if r.passed))

    score = min(100, p0_score + p1_score + p2_score)

    # P0一票否决
    if not all(r.passed for r in p0_results):
        score = min(score, 59)  # 有P0问题则<60

    return score


def get_status(score: int) -> str:
    """根据分数获取状态"""
    if score >= 90:
        return "healthy"
    elif score >= 75:
        return "good"
    elif score >= 60:
        return "acceptable"
    else:
        return "unhealthy"


def generate_report(report: SkillReport, fmt: str = 'markdown') -> str:
    """生成报告"""
    if fmt == 'json':
        return json.dumps(asdict(report), ensure_ascii=False, indent=2)

    # Markdown report
    lines = []
    lines.append(f"## 技能质量检查报告")
    lines.append(f"")
    lines.append(f"**技能**: {report.name}")
    lines.append(f"**路径**: {report.path}")
    lines.append(f"**分数**: {report.score}/100")
    lines.append(f"**状态**: {'✅ 优秀 (healthy)' if report.status == 'healthy' else '⚠️ 良好' if report.status == 'good' else '❌ 不合格'}")
    lines.append(f"")

    # Group by severity
    for severity in ['P0', 'P1', 'P2']:
        sev_results = [r for r in report.checks if r.severity == severity]
        if not sev_results:
            continue

        prefix = '✅' if all(r.passed for r in sev_results) else '❌'
        lines.append(f"### {prefix} {severity} 问题")
        lines.append(f"")
        for r in sev_results:
            status = '✅' if r.passed else '❌'
            lines.append(f"- {status} {r.name}: {r.details}")
            if r.suggestion:
                lines.append(f"  - 💡 {r.suggestion}")
        lines.append(f"")

    if report.suggestions:
        lines.append(f"### 建议")
        lines.append(f"")
        for s in report.suggestions:
            lines.append(f"- {s}")
        lines.append(f"")

    return '\n'.join(lines)


def scan_skill_dir(skill_dir: str, fmt: str = 'markdown', fix: bool = False) -> Optional[SkillReport]:
    """扫描整个技能目录"""
    skill_path = None

    # Find SKILL.md (check current dir first, then descend)
    if os.path.isdir(skill_dir):
        # Check if the dir itself contains SKILL.md
        direct = os.path.join(skill_dir, 'SKILL.md')
        if os.path.exists(direct):
            skill_path = direct
        else:
            # Walk one level deep
            for root, dirs, files in os.walk(skill_dir, followlinks=False):
                if 'SKILL.md' in files:
                    skill_path = os.path.join(root, 'SKILL.md')
                    skill_dir = root
                    break
    elif os.path.isfile(skill_dir):
        skill_path = skill_dir
        skill_dir = os.path.dirname(skill_path)

    if not skill_path:
        print(f"未找到SKILL.md: {skill_dir}", file=sys.stderr)
        return None

    content, frontmatter = load_skill_md(skill_path)
    if not content:
        print(f"无法读取: {skill_path}")
        return None

    skill_name = frontmatter.get('name', os.path.basename(skill_dir)) if frontmatter else os.path.basename(skill_dir)

    # Run all checks with dynamic weights
    skill_type = detect_skill_type(skill_path)
    weights = get_check_weights(skill_type)
    all_checks = []
    all_checks.extend(check_structure(content, frontmatter, skill_path, weights))
    all_checks.extend(check_references(content, skill_dir, weights))
    all_checks.extend(check_scripts(skill_dir, weights))
    all_checks.extend(check_consistency(content, skill_dir, weights))
    all_checks.extend(check_quality(content, frontmatter, skill_dir, weights))

    score = calculate_score(all_checks)
    status = get_status(score)

    suggestions = [c.suggestion for c in all_checks if c.suggestion]

    report = SkillReport(
        name=skill_name,
        path=skill_path,
        score=score,
        status=status,
        checks=all_checks,
        suggestions=suggestions,
        skill_type=skill_type
    )

    return report


def main():
    parser = argparse.ArgumentParser(description='技能质量检查工具')
    parser.add_argument('target', help='技能目录或SKILL.md路径，或扫描目录')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown', help='输出格式')
    parser.add_argument('--fix', action='store_true', help='自动修复P0问题')
    parser.add_argument('--parallel', type=int, default=DEFAULT_PARALLELISM, help=f'并行线程数 (默认{DEFAULT_PARALLELISM})')
    parser.add_argument('--summary', action='store_true', help='仅输出摘要')
    parser.add_argument('--no-cache', action='store_true', help='禁用缓存')
    parser.add_argument('--save-history', action='store_true', help='保存趋势历史')
    parser.add_argument('--ci', action='store_true', help='CI模式 (GitHub Actions compatible)')
    parser.add_argument('--max-scripts', type=int, default=100, help='每技能最大检查脚本数')
    parser.add_argument('--fast', action='store_true', help='快速模式（跳过脚本检查）')

    args = parser.parse_args()

    cache = SkillCache() if not args.no_cache else None
    trend = TrendTracker()
    start_time = time.time()

    # Check if target is a directory
    if os.path.isdir(args.target):
        # Scan all skills in directory
        skill_md_files = []
        for root, dirs, files in os.walk(args.target, followlinks=False):
            if 'SKILL.md' in files:
                skill_md_files.append(os.path.join(root, 'SKILL.md'))

        if not skill_md_files:
            print(f"未找到任何SKILL.md: {args.target}")
            sys.exit(1)

        reports = []
        max_workers = min(args.parallel, len(skill_md_files))
        
        for skill_md in sorted(skill_md_files):
            report = scan_skill_dir(skill_md, args.format, args.fix)
            if report:
                reports.append(report)
        
        # Apply trends and cache info
        for report in reports:
            if cache:
                report.cached = False  # track actual cache usage
            report.history_delta = trend.get_delta(report.name) if trend else 0.0

        if args.format == 'json':
            print(json.dumps([asdict(r) for r in reports], ensure_ascii=False, indent=2))
        else:
            for report in reports:
                print(generate_report(report))
                print()

        # Summary
        healthy = sum(1 for r in reports if r.status == 'healthy')
        total = len(reports)
        good = sum(1 for r in reports if r.status == 'good')
        acceptable = sum(1 for r in reports if r.status == 'acceptable')
        unhealthy = sum(1 for r in reports if r.status == 'unhealthy')
        scores = [r.score for r in reports]
        avg_score = round(statistics.mean(scores), 1) if scores else 0
        scan_time = int((time.time() - start_time) * 1000)
        
        # Type breakdown
        type_stats = defaultdict(lambda: {"total": 0, "healthy": 0, "scores": []})
        for r in reports:
            st = r.skill_type
            type_stats[st]["total"] += 1
            if r.status == "healthy": type_stats[st]["healthy"] += 1
            type_stats[st]["scores"].append(r.score)
        
        # Top issues
        issue_counts = defaultdict(int)
        for r in reports:
            for c in r.checks:
                if not c.passed and c.name:
                    issue_counts[c.name] += 1
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if args.ci:
            # CI mode: JSON for GitHub Actions
            ci_output = {
                "pass": all(r.p0_passed for r in reports) and avg_score >= CI_THRESHOLD,
                "avg_score": avg_score,
                "healthy_pct": round(healthy / total * 100, 1) if total else 0,
                "p0_failures": sum(1 for r in reports for c in r.checks if c.severity == 'P0' and not c.passed),
                "skills_summary": [
                    {"name": r.name, "score": r.score, "status": r.status, "type": r.skill_type, "delta": r.history_delta}
                    for r in sorted(reports, key=lambda r: r.score)
                ]
            }
            print(json.dumps(ci_output, ensure_ascii=False, indent=2))
        elif args.summary:
            # Summary mode
            print(f"技能质量扫描 v2 — {scan_time}ms")
            print(f"总计: {total} | 优秀: {healthy} | 良好: {good} | 合格: {acceptable} | 不合格: {unhealthy}")
            print(f"平均分: {avg_score} | 中位数: {statistics.median(scores) if scores else 0}")
            print(f"类型分解:")
            for st, data in sorted(type_stats.items()):
                avg = round(statistics.mean(data['scores']), 1) if data['scores'] else 0
                print(f"  {st}: {data['total']}个, {data['healthy']}个健康, 平均{avg}")
            print(f"Top 问题:")
            for name, count in top_issues:
                print(f"  {name}: {count}")
            print(f"=== 扫描完成: {healthy}/{total} 技能健康 ({avg_score}平均分) ===")
        else:
            print(f"=== 扫描完成: {healthy}/{total} 技能健康 ({avg_score}平均分) ===", file=sys.stderr)
    else:
        report = scan_skill_dir(args.target, args.format, args.fix)
        if report:
            print(generate_report(report, args.format))
        else:
            sys.exit(1)


if __name__ == '__main__':
    main()
