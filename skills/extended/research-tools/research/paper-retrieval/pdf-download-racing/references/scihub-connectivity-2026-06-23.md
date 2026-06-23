# SciHub 连通性 & 代码陷阱 (2026-06-23)

## 后端代码 bug 修复

`scihub_racing.py` 中 `try_scihub_curl()` 函数有一处 bug：

```python
# ❌ 错误 (第113行)：
if 'отсутствует' in title_text or 'not found' in title_text:
    return None  # 直接退出函数，不试其他域

# ✅ 修复：
if 'отсутствует' in title_text or 'not found' in title_text:
    continue  # 继续试下一个域
```

后果：当第一个 SciHub 域返回 "article not found" 时，原本应继续试其他域，但旧代码直接返回 None，跳过了其他可能的域。

## 连通性规律

- SciHub 域连通性波动大，不要用单次实验结果断言"全面失效"
- 2026-06-23 `sci-hub.al` 对 Nature 论文返回真实PDF（之前曾被认为不可用）
- `sci-hub.vg` 通过 Tor 最稳定
- 竞速逻辑应设置足够超时（120s+）让所有域尝试完毕
