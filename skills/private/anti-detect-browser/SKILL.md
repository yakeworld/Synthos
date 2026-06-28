---
name: anti-detect-browser
description: "反检测浏览器生态评估与集成 — 覆盖 CloakBrowser 等 stealth Chromium 工具的发现、安装、配置、与 Playwright 集成。用于需要绕过 bot 检测的爬取场景。"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    version: 1.0.0
    author: Synthos
    signature: 'tool_name: str -> integration_guide: dict'
    atom_type: skill
    priority: P2
---

## IO_CONTRACT

- **input**: `tool_name: str, use_case: str` — 工具名、使用场景
- **output**: `result: dict (install_cmd, config, integration_notes)` — 安装命令、配置、集成说明

## CloakBrowser 2026-06-21

### 基本信息


## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

- **项目**: [CloakHQ/CloakBrowser](https://github.com/CloakHQ/CloakBrowser)
- **Stars**: ⭐ 26,707
- **PyPI**: `cloakbrowser` 0.3.32
- **许可证**: MIT
- **描述**: Stealth Chromium — 通过所有 bot 检测的隐身 Chromium，Playwright 的即插即用替代品，源码级指纹修补
- **语言**: Python
- **兼容**: Python 3.9/3.10/3.11/3.12/3.13

### 核心特性

1. **源码级指纹修补** — 不是简单的 UA 欺骗，而是底层 Chromium 源码修改
2. **30/30 检测测试全通过**
3. **Playwright 兼容 API** — 可作为 Playwright 的 drop-in replacement
4. **多 profile 管理** — 每个 profile 有唯一指纹
5. **HTTP/SOCKS5 代理支持**
6. **Cookie 隔离**
7. **User-Agent 切换**
8. **Canvas/WebGL 修改**

### 安装

```bash
pip install cloakbrowser
# 或指定版本
pip install cloakbrowser==0.3.32
```

### 与 Playwright 对比

| 特性 | Playwright | CloakBrowser |
|------|-----------|-------------|
| 指纹修改 | 有限（UA 等） | 源码级完整修补 |
| bot 检测通过率 | 中等 | 高（30/30 通过） |
| 安装复杂度 | 简单 | 中等 |
| 性能开销 | 低 | 中（指纹修补增加内存） |
| 适用场景 | 一般自动化 | 反检测爬取、多账号管理 |
| API 兼容 | 原生 Playwright | Playwright 兼容 API |

### 典型用法

```python
# 安装后作为 Playwright 替代
from cloakbrowser import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=['--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 ...',
        viewport={'width': 1920, 'height': 1080}
    )
    page = context.new_page()
    page.goto('https://example.com')
```

### 集成建议

1. **与 pdf-download-racing 技能配合**：当前下载引擎主要依赖 Tor + curl_cffi，CloakBrowser 可作为一个补充路径，用于需要完整浏览器渲染的页面
2. **不替代 curl_cffi**：curl_cffi 用于 API 级别的 TLS 伪装，CloakBrowser 用于浏览器级完整模拟
3. **多路径策略**：
   - Tier 1: curl_cffi（最快，API 级别）
   - Tier 2: CloakBrowser（中等，浏览器级别，需要渲染）
   - Tier 3: Playwright stealth（备用）

### 参考文件

- `references/cloakbrowser-install.md` — 安装与配置指南
- `references/cloakbrowser-vs-curl-cffi.md` — 与 curl_cffi 的对比和集成策略