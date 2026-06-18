#!/usr/bin/env python3
# coding: utf-8
"""
技能吸收引擎 — 跨领域语义匹配与吸收

原则：
1. 奥卡姆剃刀：优先最简技能链，拒绝冗余
2. 类比思维：通过语义匹配发现跨领域技能复用
3. 持续进化：定期扫描外部技能源，吸收可复用的模式
"""

import json
import os
import re
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")

class SkillAbsorber:
    def __init__(self):
        self.our_skills = []
        self.external_skills = []
        self.matching_rules = []
        
    def load_our_skills(self):
        """加载我们当前的技能"""
        self.our_skills = []
        for d in sorted(os.listdir(SKILLS_DIR)):
            dp = os.path.join(SKILLS_DIR, d)
            if not os.path.isdir(dp) or d in ('skill_network.json', 'skill_registry.json'):
                continue
            md_path = os.path.join(dp, 'SKILL.md')
            if os.path.exists(md_path):
                with open(md_path) as f:
                    content = f.read()
                
                fm = content.split('---', 2)[1] if '---' in content[3:] else ''
                name_m = re.search(r'^name:\s*(.+)$', fm, re.MULTILINE)
                desc_m = re.search(r'^description:\s*(.+)$', fm, re.MULTILINE)
                
                if name_m and desc_m:
                    self.our_skills.append({
                        'name': name_m.group(1).strip(),
                        'description': desc_m.group(1).strip(),
                        'directory': d,
                    })
        return self.our_skills
    
    def fetch_anthropic_skills(self):
        """获取Anthropic官方技能"""
        result = subprocess.run([
            "curl", "-sL", 
            "https://api.github.com/repos/anthropics/skills/contents/skills"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            try:
                contents = json.loads(result.stdout)
                skills = []
                for item in contents:
                    if item['type'] == 'dir':
                        # Fetch SKILL.md for each
                        skill_result = subprocess.run([
                            "curl", "-sL", 
                            f"https://raw.githubusercontent.com/anthropics/skills/main/skills/{item['name']}/SKILL.md"
                        ], capture_output=True, text=True)
                        
                        if skill_result.returncode == 0:
                            fm = skill_result.stdout.split('---', 2)[1] if '---' in skill_result.stdout[3:] else ''
                            desc_m = re.search(r'^description:\s*(.+)$', fm, re.MULTILINE)
                            name_m = re.search(r'^name:\s*(.+)$', fm, re.MULTILINE)
                            
                            desc = desc_m.group(1).strip() if desc_m else ""
                            name = name_m.group(1).strip() if name_m else item['name']
                            
                            skills.append({
                                'name': name,
                                'description': desc,
                                'directory': item['name'],
                                'source': 'anthropic'
                            })
                self.external_skills = skills
                return skills
            except:
                return []
        return []
    
    def semantic_match(self, threshold=0.7):
        """语义匹配：发现跨领域技能复用"""
        matches = []
        
        for our in self.our_skills:
            for external in self.external_skills:
                # Simple keyword matching (can be improved with embeddings)
                our_keywords = set(our['description'].lower().split())
                ext_keywords = set(external['description'].lower().split())
                
                # Calculate similarity
                if len(our_keywords) > 0 and len(ext_keywords) > 0:
                    intersection = our_keywords.intersection(ext_keywords)
                    union = our_keywords.union(ext_keywords)
                    similarity = len(intersection) / len(union)
                    
                    if similarity >= threshold:
                        matches.append({
                            'our_skill': our['name'],
                            'external_skill': external['name'],
                            'similarity': similarity,
                            'our_desc': our['description'],
                            'ext_desc': external['description'],
                            'source': external['source']
                        })
        
        return matches
    
    def generate_absorption_plan(self, matches):
        """生成吸收计划"""
        plan = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for match in matches:
            if match['similarity'] >= 0.8:
                plan['high_priority'].append(match)
            elif match['similarity'] >= 0.5:
                plan['medium_priority'].append(match)
            else:
                plan['low_priority'].append(match)
        
        return plan

if __name__ == "__main__":
    absorber = SkillAbsorber()
    
    print("=== 技能吸收引擎 ===")
    print("1. 加载本地技能...")
    our_skills = absorber.load_our_skills()
    print(f"   找到 {len(our_skills)} 个技能")
    
    print("2. 获取外部技能...")
    external_skills = absorber.fetch_anthropic_skills()
    print(f"   找到 {len(external_skills)} 个外部技能")
    
    print("3. 语义匹配...")
    matches = absorber.semantic_match()
    print(f"   找到 {len(matches)} 个匹配")
    
    print("4. 生成吸收计划...")
    plan = absorber.generate_absorption_plan(matches)
    print(f"   高优先级: {len(plan['high_priority'])}")
    print(f"   中优先级: {len(plan['medium_priority'])}")
    print(f"   低优先级: {len(plan['low_priority'])}")
    
    # Save results
    with open(os.path.join(BASE_DIR, "docs", "skill-matches.json"), 'w') as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    
    with open(os.path.join(BASE_DIR, "docs", "absorption-plan.json"), 'w') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print("5. 结果已保存:")
    print(f"   - {os.path.join(BASE_DIR, 'docs', 'skill-matches.json')}")
    print(f"   - {os.path.join(BASE_DIR, 'docs', 'absorption-plan.json')}")
