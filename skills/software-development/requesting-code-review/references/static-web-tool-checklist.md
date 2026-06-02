# Static Data-Driven Web Tool Checklist

Patterns to look for when reviewing single-file HTML tools (academic research tools, data viewers, etc.).

## Duplicate Data Files
```bash
# Find duplicate content files
diff file1.json file2.json  # returns nothing if identical
jq . file1.json | diff - <(jq . file2.json)
```
- Check if `journal.json` and `journals.json` are byte-identical
- Check if `.gz` / `.zip` files are redundant copies of JSON data
- Remove duplicates, keep the canonical name

## Triplicated HTML Content
```bash
# Count structural markers
grep -c '<body' file.html    # should be 1
grep -c '</html>' file.html  # should be 1
grep -c '<head>' file.html   # should be 1
grep -c '<html>' file.html   # should be 1
```
- A single `.html` file should have exactly one `<body>` and one `</html>`
- Triplicated content manifests as duplicate IDs, script imbalance, 3x file size
- Each "copy" will have identical tab structures, identical IDs

## eval() in Browser JS
```bash
grep -n 'eval(' file.html
```
- `eval()` with user-provided or dynamically-generated input is an XSS risk
- Replace with `typeof window[funcName] === 'function' ? window[funcName]() : funcName`
- Or use a safe lookup table / switch statement

## Missing .gitignore
```bash
# Check for large data files that shouldn't be in the repo
du -sh *.json *.gz *.zip
```
- Large JSON data files (6MB+) are fine for GitHub Pages but compress duplicates shouldn't be tracked
- OS files, compiled output, temp files should be ignored

## Missing LICENSE
- Single-file tools almost always lack a LICENSE
- Add a MIT License if no other license is specified

## README Quality Issues
```bash
# Check for trailing whitespace/empty lines
wc -l file.md
tail -c 100 file.md | xxd | tail -3
```
- Broken numbering (1, 3, 3, 4, 5 instead of 1, 2, 3, 4, 5)
- Outdated installation instructions with placeholder paths
- Excessive trailing whitespace (empty lines at end of file)
- Links to services that may be down or geo-blocked (Poe, etc.)

## Duplicate IDs
```bash
grep -o 'id="[^"]*"' file.html | sort | uniq -d
```
- Every HTML ID must be unique in a page
- JS template literals like `${checkboxId}` are false positives (runtime-generated)
- Check that IDs are not simply copy-pasted duplicates across multiple "copies" of content
