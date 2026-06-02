# API Key Fallback Pattern — .bashrc → File Fallback

## The Problem
When running Python code via Hermes Agent's `execute_code` with `shell=True`, environment variables from `.bashrc` are not accessible because:
1. `bash -c` is non-interactive and doesn't source `.bashrc` by default
2. Even with explicit `source ~/.bashrc`, child Python processes don't inherit exported variables due to subprocess isolation

## The Solution: File-Based Fallback

Store API keys in a file alongside the Python config, and read as fallback when `os.environ` is empty.

### Step 1: Create the key file
```
/media/yakeworld/sda2/academic_writer/work/src/core/.api_key
```
Content: `s2k-7b8a0e1a9c6e4f3d5b8c7a6e4f3d2b1a0c9e8f7d`

### Step 2: Modify config.py to read fallback
```python
class Config:
    def __init__(self):
        self.api_key = os.environ.get('SEMANTIC_SCHOLAR_API_KEY', '')
        if not self.api_key:
            import pathlib
            _key_file = pathlib.Path(__file__).parent / '.api_key'
            if _key_file.is_file():
                self.api_key = _key_file.read_text().strip()
```

### Step 3: Add to .gitignore
```
src/core/.api_key
*.key
*.secret
```

## When to Use
- Running automated scripts in Hermes Agent environment
- API keys need to be available in subprocess contexts
- Environment variables are set in `.bashrc` but not accessible

## Pros and Cons
| | Pros | Cons |
|---|------|------|
| File fallback | Works in all contexts | File must be present |
| .bashrc exports | Standard Linux practice | Not accessible in subprocess |
| /etc/environment | Most reliable | Requires root/sudo |

## Key Insight
The file-based fallback is the **most reliable** solution for Hermes Agent environments where subprocess isolation prevents environment variable propagation.
