# Python 3.12 + shap 安装失败 — 修复方案

Ubuntu 24.04 的系统 Python 3.12 存在嵌套问题：

1. 系统包 /usr/lib/python3.12/dist-packages/ 中的 numexpr、bottleneck 用 numpy 1.x 编译
2. shap 需要 numpy >=2.0.0
3. Python 3.12 venv 只是指向 /usr/bin/python3.12 的符号链接（不完整隔离）
4. PYTHONNOUSERSITE=1 + PYTHONPATH='' 仍会导入 .local/lib/python3.12/site-packages

修复：必须使用 Python 3.11 创建 venv：

```bash
uv venv /tmp/pima_shap_env --python python3.11
source /tmp/pima_shap_env/bin/activate
export PYTHONPATH=''
export PYTHONNOUSERSITE=1
pip install shap numpy scipy pandas scikit-learn matplotlib catboost xgboost lightgbm
```

验证：`python -c "import shap; print(shap.__version__)"` 应正常。