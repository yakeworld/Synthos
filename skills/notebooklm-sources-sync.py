#!/usr/bin/env python3
"""
notebooklm-sources-sync.py — 比较本地PDF与NotebookLM已上传清单，只上传缺失的文件。

用法:
  python3 notebooklm-sources-sync.py <paper_dir>
  
示例:
  cd /media/yakeworld/sda2/Synthos/outputs/papers/synthos-system-paper
  python3 ../notebooklm-sources-sync.py .

流程:
  1. 读取 notebooklm-sources.json（如不存在则创建）
  2. 扫描 pdfs/ 目录下的所有PDF
  3. 查询NotebookLM当前已上传源文件列表
  4. 比较：只上传缺失的，跳过已有的
  5. 更新 notebooklm-sources.json
"""

import os, sys, json, subprocess, hashlib

def get_local_pdfs(paper_dir):
    """扫描本地pdfs目录"""
    pdf_dir = os.path.join(paper_dir, 'pdfs')
    if not os.path.isdir(pdf_dir):
        # Also check bibtex_pdfs/pdfs
        pdf_dir2 = os.path.join(paper_dir, 'bibtex_pdfs', 'pdfs')
        if os.path.isdir(pdf_dir2):
            pdf_dir = pdf_dir2
        else:
            return []
    
    pdfs = []
    for f in sorted(os.listdir(pdf_dir)):
        if f.endswith('.pdf'):
            fpath = os.path.join(pdf_dir, f)
            size = os.path.getsize(fpath)
            pdfs.append({
                'filename': f,
                'path': fpath,
                'size': size,
                'title': os.path.splitext(f)[0]
            })
    return pdfs

def load_manifest(paper_dir):
    """加载已上传清单"""
    path = os.path.join(paper_dir, 'notebooklm-sources.json')
    if os.path.exists(path):
        return json.load(open(path))
    return {'version': '1.0', 'notebook_id': '', 'sources': [], 'last_synced': ''}

def save_manifest(paper_dir, manifest):
    """保存已上传清单"""
    path = os.path.join(paper_dir, 'notebooklm-sources.json')
    json.dump(manifest, open(path, 'w'), indent=2, ensure_ascii=False)
    print(f"✅ 清单已更新: {path} ({len(manifest['sources'])}个源文件)")

def get_notebooklm_sources():
    """查询NotebookLM当前源文件列表"""
    try:
        result = subprocess.run(
            ['notebooklm', 'source', 'list'],
            capture_output=True, text=True, timeout=30
        )
        lines = result.stdout.split('\n')
        sources = []
        current_id = None
        current_title = None
        for line in lines:
            # Parse table rows: │ ID │ Title │ Type │ ...
            m = re.search(r'│\s*([a-f0-9-]{8,})\s*│\s*([^│]+)\s*│', line)
            if m:
                current_id = m.group(1).strip()
                current_title = m.group(2).strip()
            # Match type indicators
            if 'PDF' in line or 'pdf' in line:
                if current_id and current_title:
                    sources.append({'id': current_id, 'title': current_title})
                    current_id = None
        return sources
    except Exception as e:
        print(f"⚠️ 查询NotebookLM失败: {e}")
        return []

def main():
    if len(sys.argv) < 2:
        print("用法: python3 notebooklm-sources-sync.py <paper_dir>")
        sys.exit(1)
    
    paper_dir = sys.argv[1]
    if not os.path.isdir(paper_dir):
        print(f"❌ 目录不存在: {paper_dir}")
        sys.exit(1)
    
    print(f"📂 论文目录: {paper_dir}")
    
    # 1. 获取本地PDF
    local_pdfs = get_local_pdfs(paper_dir)
    print(f"📄 本地PDF文件: {len(local_pdfs)}个")
    for p in local_pdfs:
        print(f"     {p['filename']} ({p['size']//1024}KB)")
    
    # 2. 加载已上传清单
    manifest = load_manifest(paper_dir)
    uploaded_titles = {s.get('title', '') for s in manifest.get('sources', [])}
    print(f"📋 已上传清单记录: {len(manifest['sources'])}个")
    
    # 3. 查询NotebookLM当前源文件
    print("🔍 查询NotebookLM当前源文件...")
    nb_sources = get_notebooklm_sources()
    nb_titles = {s['title'].lower() for s in nb_sources} if nb_sources else set()
    print(f"   NotebookLM现有源文件: {len(nb_sources) if nb_sources else '查询失败'}")
    
    # 4. 比较：确定需要上传的文件
    to_upload = []
    already_uploaded = []
    for p in local_pdfs:
        title_lower = p['title'].lower()
        if title_lower in nb_titles or title_lower in {t.lower() for t in uploaded_titles}:
            already_uploaded.append(p)
        else:
            to_upload.append(p)
    
    print(f"\n📊 比较结果:")
    print(f"   已上传（跳过）: {len(already_uploaded)}个")
    print(f"   需上传（缺失）: {len(to_upload)}个")
    
    for p in already_uploaded:
        print(f"     ⏭️  {p['filename']}")
    for p in to_upload:
        print(f"     🔄  {p['filename']}")
    
    if not to_upload:
        print("\n✅ 所有PDF已上传，无需操作")
        return
    
    # 5. 上传缺失文件
    print(f"\n📤 开始上传 {len(to_upload)}个文件...")
    for p in to_upload:
        print(f"   正在上传 {p['filename']}...", end=' ', flush=True)
        try:
            result = subprocess.run(
                ['notebooklm', 'source', 'add', p['path'], '--title', p['title']],
                capture_output=True, text=True, timeout=120
            )
            if 'Added source' in result.stdout:
                print('✅')
                # Extract source ID
                m = re.search(r'([a-f0-9-]{36})', result.stdout)
                source_id = m.group(1) if m else 'unknown'
                manifest['sources'].append({
                    'local_path': p['path'],
                    'notebooklm_title': p['title'],
                    'notebooklm_id': source_id,
                    'type': 'pdf',
                    'uploaded_at': '',
                    'status': 'ready'
                })
            else:
                print(f'⚠️  {result.stdout[:100]}')
        except Exception as e:
            print(f'❌ {e}')
    
    # 6. 更新清单
    manifest['last_synced'] = ''
    save_manifest(paper_dir, manifest)
    print(f"\n🎉 同步完成！共上传 {len(to_upload)}个文件")

if __name__ == '__main__':
    import re
    main()
