# 重复技能同步详细步骤

## 环境

- Synthos: `/media/yakeworld/sda2/Synthos/skills`
- Hermes: `/home/yakeworld/.hermes/skills`

## 步骤

### 1. 发现重复

```python
synthos_dirs = set(os.listdir(SYNTHOS_BASE))
hermes_dirs = set(os.listdir(HERMES_BASE))
duplicates = synthos_dirs & hermes_dirs  # 60个
only_synthos = synthos_dirs - hermes_dirs  # 2个
only_hermes = hermes_dirs - synthos_dirs   # 10个
```

### 2. 检查内容一致性

```python
non_identical = []
for name in duplicates:
    s_path = SYNTHOS_BASE / name / 'SKILL.md'
    h_path = HERMES_BASE / name / 'SKILL.md'
    
    if s_path.exists() and h_path.exists():
        with open(s_path) as f1, open(h_path) as f2:
            if f1.read() != f2.read():
                non_identical.append(name)
                # 检查整个目录
                for f in sorted(os.listdir(SYNTHOS_BASE / name)):
                    s_file = SYNTHOS_BASE / name / f
                    h_file = HERMES_BASE / name / f
                    if s_file.exists() and h_file.exists():
                        if s_file.read_text() != h_file.read_text():
                            print(f"  DIFF: {name}/{f}")
```

### 3. 统一（Hermes→Synthos）

```python
for name in duplicates:
    s_dir = SYNTHOS_BASE / name
    h_dir = HERMES_BASE / name
    
    # 直接复制
    if os.path.exists(s_dir):
        shutil.rmtree(s_dir)
    shutil.copytree(h_dir, s_dir)
```

### 4. 双向同步

```python
# 仅Synthos → Hermes
for name in only_synthos:
    s_dir = SYNTHOS_BASE / name
    if os.path.exists(s_dir):
        h_dir = HERMES_BASE / name
        shutil.rmtree(h_dir) if os.path.exists(h_dir) else None
        shutil.copytree(s_dir, h_dir)

# 仅Hermes → Synthos（仅SKILL.md或含子技能的目录）
for name in only_hermes:
    h_dir = HERMES_BASE / name
    if os.path.exists(h_dir / 'SKILL.md') or any(
        os.path.isdir(h_dir / d) for d in os.listdir(h_dir)
        if not d.startswith('.')
    ):
        s_dir = SYNTHOS_BASE / name
        shutil.rmtree(s_dir) if os.path.exists(s_dir) else None
        shutil.copytree(h_dir, s_dir)
```

### 5. 验证

```python
# 再次检查一致性
for name in duplicates:
    s_path = SYNTHOS_BASE / name / 'SKILL.md'
    h_path = HERMES_BASE / name / 'SKILL.md'
    with open(s_path) as f1, open(h_path) as f2:
        assert f1.read() == f2.read(), f"Still different: {name}"
```

## 陷阱

1. **不要只比较SKILL.md**：整个目录都需要比较
2. **Hermes是主源**：Hermes的编辑更新更频繁
3. **Graph需要手动更新**：`graph.json`不自动同步
4. **子技能不自动继承SKILL.md**：父级目录需要手动创建SKILL.md

## 结果（2026-06-13）

- 60个重复技能统一
- 6个内容不一致已修复
- 2个仅Synthos技能同步到Hermes
- 1个仅Hermes技能(kg-bridge)同步到Synthos
- Graph更新：63技能，1478节点
- 无残留不一致