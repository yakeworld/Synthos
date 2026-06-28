# 工作站环境交付报告模板
# 作用: 生成后放置在 ~/workspace/WORK_CHECK_REPORT.md
# 使用时替换 {{占位符}}

# 郭梓豪 · Work2 科研环境工作检查报告

**检查日期**: {{检查日期}}
**服务器**: {{主机名}} ({{IP}})
**用户**: {{用户名}}
**检查人**: Synthos / Hermes Agent

---

## 一、环境概览

| 项目 | 状态 | 版本/详情 |
|:-----|:-----|:----------|
| Python | ✅ | {{版本}} |
| uv (包管理器) | ✅ | {{版本}} |
| Node.js | ✅ | v{{版本}} (nvm) |
| Hermes Agent | ✅ | v{{版本}} |
| Codex CLI | ✅ | v{{版本}} |
| vLLM 推理引擎 | ✅ | http://{{host}}:8000/v1 |
| 模型 | ✅ | {{模型名}} ({{上下文长度}}K ctx) |
| Synthos 技能库 | ✅ | {{N}} 个 SKILL.md |
| Git 配置 | ✅ | {{姓名}} <{{邮箱}}> |

## 二、科学计算栈（在 eye-tracking venv 中）

| 库 | 版本 | 状态 |
|:---|:-----|:-----|
| numpy | {{版本}} | ✅ |
| opencv-python | {{版本}} | ✅ |
| matplotlib | {{版本}} | ✅ |
| pandas | {{版本}} | ✅ |
| scikit-learn | {{版本}} | ✅ |
| scipy | {{版本}} | ✅ |
| jupyter | 已安装 | ✅ |
| pillow | 已安装 | ✅ |
| tqdm | 已安装 | ✅ |

## 三、功能验证结果

### Hermes Agent — 科研推理能力
- 测试: 请求编写 3D 瞳孔椭圆→法向量公式
- 结果: ✅ 返回可用 Python 代码

### Codex CLI — 科研编码能力
- 测试: 椭圆生成+拟合+可视化全流程
- 结果: ✅ 自动生成脚本, 拟合误差 < 2px

## 四、已修复问题

| 问题 | 修复措施 |
|:-----|:---------|
| {{问题}} | ✅ {{修复}} |

## 五、快速使用指南

### 登录
```
ssh {{用户名}}@{{IP}}
```

### 激活 Python 环境
```
source ~/workspace/eye-tracking/.venv/bin/activate
```

### 使用 Hermes
```
hermes chat                          # 交互模式
hermes chat -q "你的问题" -Q         # 单次查询
hermes chat -s 技能名                # 加载技能
```

### 使用 Codex
```
./codex-vllm.sh "写一个脚本来..."     # 一键启动
```

### 安装新包
```
uv pip install 包名
```

### 别名
- `ws` → ~/workspace/
- `proj` → ~/projects/
- `python` → python3

## 六、目录结构

```
~/workspace/
  START_HERE.md
  eye-tracking/.venv/
~/projects/
~/data/
~/Synthos/
```

## 七、下一步
1. 配置 GitHub SSH Key
2. 放入实验代码
3. 跑通第一个 demo

---

*报告由 Synthos / Hermes Agent 自动生成*
