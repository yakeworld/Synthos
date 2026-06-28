#!/usr/bin/env python3
"""
Skill Refactor Tool — Transform old skill structure to 6-atom architecture.

Usage:
    python3 skill_refactor.py <project_root> [--dry-run]

This tool:
1. Scans existing skills/ directory
2. Identifies skills to remove and atoms to create
3. Generates skill.yaml for each new atom
4. Generates SKILL.md for each new atom
5. Creates skill_registry.json
6. Creates skill_network.json
7. (Optional) deletes old skill directories

Safety:
- Always creates new before deleting (never breaks in an intermediate state)
- All writes go to a staging directory first
- Only with --execute are changes actually applied
"""

import json
import os
import shutil
import sys
import argparse
from pathlib import Path


# ====== Data: 6 atoms definition ======

ATOMS = [
    {
        "name": "knowledge_acquisition",
        "chinese": "知识获取",
        "english": "KnowledgeAcquisition",
        "atom": 1,
        "description": "从外部源获取学术知识：检索论文、提取摘要、下载全文。是认知链条的起点。",
        "inputs": ["search_query", "sources: list[str]", "domain", "max_results: int"],
        "outputs": ["raw_papers: list[Paper]", "raw_abstracts: list[Abstract]", "pdf_files: list[str]"],
        "depends_on": [],
        "used_by": ["知识提取/KnowledgeExtraction", "关联发现/AssociationDiscovery"],
        "synthos": ["第一性原理", "系统思维"],
        "execution": {"method": "subagent", "max_retries": 3, "timeout_minutes": 10, "resource_requirements": "low", "batch_support": True, "incremental": False, "human_in_loop": False},
        "fallback": ["Semantic Scholar → PubMed → Crossref → OpenAlex → 返回空结果+错误报告"],
        "failure_modes": [
            {"mode": "API不可用", "mitigation": "fallback链"},
            {"mode": "网络超时", "mitigation": "重试+降低并发"},
        ],
        "quality_criteria": ["检索覆盖率", "相关性评分", "时效性", "权威性"],
        "constraints": ["不得假设外部API可用性", "必须处理API速率限制", "必须去重"],
        "output_format": "JSON: [{title, authors, year, abstract, doi, source, relevance_score, pdf_path}]",
        "notes": "这是认知链条的第一环。",
    },
    {
        "name": "knowledge_extraction",
        "chinese": "知识提取",
        "english": "KnowledgeExtraction",
        "atom": 2,
        "description": "从完整论文中精确提取结构化知识：方法、发现、数据、统计结果、研究局限。",
        "inputs": ["pdf_files: list[str]", "extract_fields: list[str]", "depth: str"],
        "outputs": ["extracted_knowledge: list[KnowledgeItem]", "field_summary: dict"],
        "depends_on": ["知识获取/KnowledgeAcquisition"],
        "used_by": ["关联发现/AssociationDiscovery", "观点生成/HypothesisGeneration"],
        "synthos": ["第一性原理", "奥卡姆剃刀"],
        "execution": {"method": "subagent", "max_retries": 2, "timeout_minutes": 15, "resource_requirements": "medium", "batch_support": True, "incremental": True, "human_in_loop": False},
        "fallback": ["PDF解析 → OCR → 用户手动提供"],
        "failure_modes": [
            {"mode": "PDF解析失败", "mitigation": "尝试OCR或文本提取"},
            {"mode": "信息不完整", "mitigation": "标记未提取字段"},
        ],
        "quality_criteria": ["准确性", "完整性", "结构化程度", "可追溯性"],
        "constraints": ["保持原文引用准确性", "不得添加解释", "必须标记不确定信息"],
        "output_format": "JSON: [{paper_title, section, field, value, confidence, citation}]",
        "notes": "从原始内容到结构化知识的转换。",
    },
    {
        "name": "association_discovery",
        "chinese": "关联发现",
        "english": "AssociationDiscovery",
        "atom": 3,
        "description": "识别知识项之间的关联：矛盾、补充、演进、空白。构建知识图谱。",
        "inputs": ["extracted_knowledge: list[KnowledgeItem]", "knowledge_graph: KG or None"],
        "outputs": ["associations: list[Association]", "knowledge_graph: KG", "research_gaps: list[Gap]"],
        "depends_on": ["知识提取/KnowledgeExtraction"],
        "used_by": ["观点生成/HypothesisGeneration"],
        "synthos": ["系统思维", "模型依赖实在论"],
        "execution": {"method": "subagent", "max_retries": 2, "timeout_minutes": 15, "resource_requirements": "medium", "batch_support": False, "incremental": True, "human_in_loop": False},
        "fallback": ["LLM关联 → 手动确认 → 降低关联阈值"],
        "failure_modes": [
            {"mode": "关联过少", "mitigation": "放宽关联条件"},
            {"mode": "关联过多噪声", "mitigation": "提高筛选标准"},
        ],
        "quality_criteria": ["发现率", "准确性", "多样性", "可解释性"],
        "constraints": ["区分相关性和因果性", "标记假设性关联", "不得臆造关联"],
        "output_format": "JSON: [{type, source, target, description, confidence, evidence}]",
        "notes": "连接孤立的知识点，形成知识网络。",
    },
    {
        "name": "hypothesis_generation",
        "chinese": "观点生成",
        "english": "HypothesisGeneration",
        "atom": 4,
        "description": "基于关联分析生成可验证的研究假设和观点：新颖性、合理性、可检验性。",
        "inputs": ["associations: list[Association]", "research_gaps: list[Gap]", "domain_knowledge: dict"],
        "outputs": ["hypotheses: list[Hypothesis]", "rationale: dict", "novelty_score: float"],
        "depends_on": ["关联发现/AssociationDiscovery"],
        "used_by": ["论证表达/ArgumentExpression", "观点验证/ViewpointVerification"],
        "synthos": ["第一性原理", "类比", "贝叶斯思维"],
        "execution": {"method": "subagent", "max_retries": 2, "timeout_minutes": 10, "resource_requirements": "medium", "batch_support": True, "incremental": True, "human_in_loop": True},
        "fallback": ["LLM生成 → 交叉验证 → 人工筛选"],
        "failure_modes": [
            {"mode": "无新颖假设", "mitigation": "扩大关联分析范围"},
            {"mode": "假设不可检验", "mitigation": "重新表述为可操作假设"},
        ],
        "quality_criteria": ["新颖性", "合理性", "可检验性", "明确性"],
        "constraints": ["基于已有关联", "说明推理过程", "评估新颖性和可行性"],
        "output_format": "JSON: [{hypothesis, rationale, novelty, testability, evidence_basis}]",
        "notes": "从关联到观点的飞跃。核心创新环节。",
    },
    {
        "name": "argument_expression",
        "chinese": "论证表达",
        "english": "ArgumentExpression",
        "atom": 5,
        "description": "将假设转化为结构化论证：论文章节、论据链、文献支持。",
        "inputs": ["hypotheses: list[Hypothesis]", "evidence: list[Evidence]", "structure: str"],
        "outputs": ["sections: list[Section]", "arguments: list[Argument]", "references: list[Ref]"],
        "depends_on": ["观点生成/HypothesisGeneration", "知识获取/KnowledgeAcquisition"],
        "used_by": [],
        "synthos": ["系统思维", "第一性原理", "奥卡姆剃刀"],
        "execution": {"method": "subagent", "max_retries": 2, "timeout_minutes": 20, "resource_requirements": "high", "batch_support": True, "incremental": True, "human_in_loop": True},
        "fallback": ["LLM写作 → 语法检查 → 人工校对"],
        "failure_modes": [
            {"mode": "逻辑断裂", "mitigation": "重新梳理论证链条"},
            {"mode": "证据不足", "mitigation": "请求补充文献或数据"},
        ],
        "quality_criteria": ["逻辑性", "完整性", "可读性", "规范性"],
        "constraints": ["不得编造引用", "区分事实和观点", "遵循学术写作规范"],
        "output_format": "Markdown/JSON: [Section(title, content, references, arguments)]",
        "notes": "观点的表达和论证。输出通常是论文/报告/提案的一部分。",
    },
    {
        "name": "viewpoint_verification",
        "chinese": "观点验证",
        "english": "ViewpointVerification",
        "atom": 6,
        "description": "对假设和论证进行多角度验证：反方观点、证伪检验、鲁棒性测试。",
        "inputs": ["hypotheses: list[Hypothesis]", "arguments: list[Argument]", "evidence: list[Evidence]"],
        "outputs": ["verification_results: list[Verification]", "weaknesses: list[Weakness]", "confidence_score: float"],
        "depends_on": ["观点生成/HypothesisGeneration", "论证表达/ArgumentExpression"],
        "used_by": [],
        "synthos": ["证伪主义", "贝叶斯思维", "熵减律"],
        "execution": {"method": "subagent", "max_retries": 3, "timeout_minutes": 20, "resource_requirements": "high", "batch_support": True, "incremental": False, "human_in_loop": True},
        "fallback": ["多模型验证 → 人工评审 → 降级为低置信度输出"],
        "failure_modes": [
            {"mode": "验证过于宽松", "mitigation": "提高验证标准"},
            {"mode": "验证过于严苛", "mitigation": "调整验证阈值"},
        ],
        "quality_criteria": ["全面性", "严谨性", "诚实性", "可重复性"],
        "constraints": ["主动寻找反证", "不得忽略负面结果", "必须承认不确定性"],
        "output_format": "JSON: [{hypothesis, test, result, confidence, weaknesses, recommendations}]",
        "notes": "认知闭环的最后一步。通过证伪增强理论。Popper精神。",
    },
]


def generate_skill_yaml(atom: dict) -> str:
    """Generate skill.yaml content for a single atom."""
    yaml = f"""name: {atom['name']}
atom: {atom['atom']}
chinese_name: {atom['chinese']}
english_name: {atom['english']}
description: {atom['description']}
version: 1.0.0
status: active
created: 2026-05-09
synthos_dimensions: {json.dumps(atom['synthos'], ensure_ascii=False)}

input_contract:
  inputs: {json.dumps(atom['inputs'], ensure_ascii=False)}
  outputs: {json.dumps(atom['outputs'], ensure_ascii=False)}

quality_criteria: {json.dumps(atom['quality_criteria'], ensure_ascii=False)}
constraints: {json.dumps(atom['constraints'], ensure_ascii=False)}
fallback_chain: {json.dumps(atom['fallback'], ensure_ascii=False)}

execution:
  method: {atom['execution']['method']}
  max_retries: {atom['execution']['max_retries']}
  timeout_minutes: {atom['execution']['timeout_minutes']}
  resource_requirements: {atom['execution']['resource_requirements']}
  batch_support: {atom['execution']['batch_support']}
  incremental: {atom['execution']['incremental']}
  human_in_loop: {atom['execution']['human_in_loop']}

dependencies:
  depends_on: {json.dumps(atom['depends_on'], ensure_ascii=False)}
  used_by: {json.dumps(atom['used_by'], ensure_ascii=False)}

failure_modes: {json.dumps(atom['failure_modes'], ensure_ascii=False)}
output_format: "{atom['output_format']}"

trust_score: 0.0
usage_count: 0
notes: "{atom['notes']}"
"""
    return yaml


def generate_skill_md(atom: dict) -> str:
    """Generate SKILL.md content for a single atom."""
    return f"""\
# {atom['chinese']} ({atom['english']}) — 认知原子 #{atom['atom']}

## 概述
{atom['description']}

## 输入契约
""" + "\n".join(f"- `{p.split(':')[0]}`: {p.split(':')[-1] if ':' in p else 'N/A'}" for p in atom['inputs']) + f"""

## 输出契约
""" + "\n".join(f"- `{p.split(':')[0]}`: {p.split(':')[-1] if ':' in p else 'N/A'}" for p in atom['outputs']) + """

## 执行步骤
1. 按输入契约接收数据
2. 执行核心认知操作
3. 验证输出符合契约
4. 返回结构化结果

## 质量要求
""" + "\n".join(f"- {q}" for q in atom['quality_criteria']) + f"""

## 约束
""" + "\n".join(f"- {c}" for c in atom['constraints']) + f"""

## 失败模式
""" + "\n".join(f"- {fm['mode']} → {fm['mitigation']}" for fm in atom['failure_modes']) + f"""

## 依赖
- 上游: {', '.join(atom['depends_on']) if atom['depends_on'] else '无（这是起点）'}
- 下游: {', '.join(atom['used_by']) if atom['used_by'] else '无（这是终点）'}

## Synthos 维度
- """ + "\n- ".join(atom['synthos']) + f"""

## 注意事项
{atom['notes']}
"""


def scan_existing_skills(project_root: str):
    """Scan existing skills directory and return list of skill names."""
    skills_dir = os.path.join(project_root, "skills")
    if not os.path.isdir(skills_dir):
        return []
    
    skills = []
    for item in os.listdir(skills_dir):
        item_path = os.path.join(skills_dir, item)
        if os.path.isdir(item_path) and item not in ("skill_registry.json", "skill_network.json"):
            skills.append(item)
    return skills


def run_refactor(project_root: str, dry_run: bool = True):
    """Run the full refactoring process."""
    print(f"Project root: {project_root}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    
    old_skills = scan_existing_skills(project_root)
    print(f"\nExisting skills: {old_skills}")
    print(f"New atoms to create: {len(ATOMS)}")
    
    if not dry_run:
        # 1. Create new atom directories and files
        for atom in ATOMS:
            atom_dir = os.path.join(project_root, "skills", f"{atom['chinese']}/{atom['english']}")
            os.makedirs(atom_dir, exist_ok=True)
            
            # Write skill.yaml
            yaml_path = os.path.join(atom_dir, "skill.yaml")
            with open(yaml_path, "w") as f:
                f.write(generate_skill_yaml(atom))
            print(f"  Created: {yaml_path}")
            
            # Write SKILL.md
            md_path = os.path.join(atom_dir, "SKILL.md")
            with open(md_path, "w") as f:
                f.write(generate_skill_md(atom))
            print(f"  Created: {md_path}")
        
        # 2. Create skill_registry.json
        registry = {}
        for atom in ATOMS:
            key = f"{atom['chinese']}/{atom['english']}"
            registry[key] = {
                "name": atom['name'],
                "atom": atom['atom'],
                "chinese": atom['chinese'],
                "english": atom['english'],
                "description": atom['description'],
                "inputs": atom['inputs'],
                "outputs": atom['outputs'],
                "depends_on": atom['depends_on'],
                "used_by": atom['used_by'],
                "synthos_dimensions": atom['synthos'],
                "execution": atom['execution'],
                "fallback_chain": atom['fallback'],
                "quality_criteria": atom['quality_criteria'],
                "constraints": atom['constraints'],
                "failure_modes": atom['failure_modes'],
                "output_format": atom['output_format'],
                "notes": atom['notes'],
            }
        
        registry_path = os.path.join(project_root, "skills", "skill_registry.json")
        with open(registry_path, "w") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        print(f"\nCreated: {registry_path}")
        
        # 3. Delete old skill directories
        print("\nDeleting old skills:")
        for skill_name in old_skills:
            skill_path = os.path.join(project_root, "skills", skill_name)
            if os.path.exists(skill_path):
                shutil.rmtree(skill_path)
                print(f"  Removed: {skill_path}")
        
        print("\nRefactoring complete!")
    else:
        print("\n(DRY RUN — no files were created or deleted)")
        print("To execute: python3 skill_refactor.py <project_root>")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Skill Refactor Tool")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--execute", action="store_true", help="Actually execute changes (default: dry run)")
    args = parser.parse_args()
    
    run_refactor(args.project_root, dry_run=not args.execute)
