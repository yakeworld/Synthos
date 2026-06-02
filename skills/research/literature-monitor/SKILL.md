---
name: literature-monitor
description: "Continuous monitoring of new research papers across multiple sources — arXiv, PubMed, bioRxiv/medRxiv, OpenAlex, and journal TOCs. Automated daily/weekly digests of new papers on your topics."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Research, Monitoring, Alert, Digest, Daily-Update, Journal-TOC, RSS, Continuous-Search]
    related_skills: [pubmed, arxiv, biorxiv, openalex, blogwatcher, llm-wiki, notebooklm-cli]
---

# Literature Monitor — Continuous Paper Tracking

Automated monitoring of new research papers across multiple sources. Set up recurring checks for your research topics and receive digests of new publications.

## Quick Reference

| Source | Command |
|--------|---------|
| arXiv daily | `curl -s "https://export.arxiv.org/api/query?cat=cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=20"` |
| PubMed daily | `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=YOUR+TOPIC+AND+last30days[Date+-+Publication]&retmax=20&retmode=json"` |
| bioRxiv daily | `curl -s "https://api.biorxiv.org/details/biorxiv/0"` |
| OpenAlex new | `curl -s "https://api.openalex.org/works?search=TOPIC&filter=from_publication_date:2024-01-01&sort=date:desc&per_page=10"` |
| Journal TOC RSS | Use blogwatcher with journal RSS feeds |
| Google Scholar alerts | Use Google Scholar's "Create alert" for ongoing monitoring |

## Sources to Monitor

### 1. arXiv Categories

| Category | Field | Description |
|----------|-------|-------------|
| cs.AI | cs.AI | Artificial Intelligence |
| cs.LG | cs.LG | Machine Learning |
| cs.CL | cs.CL | Computation and Language (NLP) |
| cs.CV | cs.CV | Computer Vision |
| stat.ML | stat.ML | Machine Learning (Statistics) |
| q-bio.GN | q-bio.GN | Genomics |
| q-bio.QM | q-bio.QM | Quantitative Methods (Bio) |
| q-bio.NC | q-bio.NC | Neurons and Cognition |
| cs.NE | cs.NE | Neural Systems |
| cs.RO | cs.RO | Robotics |
| eess.SY | eess.SY | Systems and Control |
| math.OC | math.OC | Optimization and Control |
| cs.SI | cs.SI | Social and Information Networks |

### 2. PubMed — Date-Filtered Searches

```bash
# Papers published in the last 24 hours
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=YOUR+TOPIC+AND+last24hours[Date+-+Publication]&retmax=20&retmode=json"

# Papers published in the last 7 days
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=YOUR+TOPIC+AND+last7days[Date+-+Publication]&retmax=20&retmode=json"

# Papers published in the last 30 days
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=YOUR+TOPIC+AND+last30days[Date+-+Publication]&retmax=20&retmode=json"
```

### 3. bioRxiv/medRxiv — Latest Uploads

```bash
# Get all latest bioRxiv preprints
curl -s "https://api.biorxiv.org/details/biorxiv/0"

# Get all latest medRxiv preprints
curl -s "https://api.biorxiv.org/details/medrxiv/0"

# Get latest from a specific subject category
curl -s "https://api.biorxiv.org/details/biorxiv/Neuroscience"
```

### 4. OpenAlex — Recent Papers

```bash
# Recent papers on your topic (last 30 days)
curl -s "https://api.openalex.org/works?search=YOUR+TOPIC&filter=from_publication_date:2024-11-01&sort=date:desc&per_page=20&select=title,publication_date,cited_by_count,primary_location,open_access"

# Papers from specific journals
curl -s "https://api.openalex.org/works?search=YOUR+TOPIC&filter=primary_location.source.id:https://openalex.org/S123456789&sort=date:desc&per_page=10"
```

## Journal TOC RSS Feeds

Monitor top journals via their RSS/Atom feeds using blogwatcher:

### Medical Journals

| Journal | RSS Feed |
|---------|----------|
| New England Journal of Medicine | `https://www.nejm.org/rss/clinical` |
| Lancet | `https://www.thelancet.com/feeds/rss` |
| JAMA | `https://jamanetwork.com/data/Journals/JAMA/announcement/RSSfeed.xml` |
| BMJ | `https://www.bmj.com/rss` |
| Nature | `https://www.nature.com/nature.rss` |
| Science | `https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science` |
| Cell | `https://www.cell.com/action/showFeed?type=etoc&feed=rss&jc=cell` |
| PLOS Medicine | `https://journals.plos.org/plosmedicine/article/feed?type=feed&id=feed.1` |

### Neuroscience/Vestibular

| Journal | RSS Feed |
|---------|----------|
| Neuroscience | `https://www.sciencedirect.com/rss/article/neuroscience` |
| Journal of Neuroscience | `https://www.jneurosci.org/rss/current.xml` |
| Brain | `https://academic.oup.com/brain/rss` |
| Annals of Neurology | `https://onlinelibrary.wiley.com/rss/1531-8249` |
| Vestibular Research | `https://www.iospress.nl/Journals/rss/vestibular-research` |

### ADHD/Cognitive Science

| Journal | RSS Feed |
|---------|----------|
| Journal of Child Psychology | `https://onlinelibrary.wiley.com/rss/1469-7610` |
| Biological Psychiatry | `https://www.sciencedirect.com/rss/article/biological-psychiatry` |
| Molecular Psychiatry | `https://www.nature.com/mp/rss` |

## Setting Up Monitoring

### Option 1: Blogwatcher with Journal Feeds

```bash
# Add journal RSS feeds
blogwatcher-cli add "NEJM Clinical" https://www.nejm.org/rss/clinical
blogwatcher-cli add "Lancet" https://www.thelancet.com/feeds/rss
blogwatcher-cli add "Nature" https://www.nature.com/nature.rss
blogwatcher-cli add "Science" https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science
blogwatcher-cli add "J. Neuroscience" https://www.jneurosci.org/rss/current.xml

# Scan and read
blogwatcher-cli scan
blogwatcher-cli articles
```

### Option 2: Direct API Queries (for cron automation)

```bash
# Run this via a cron job to check for new papers daily
#!/bin/bash

# Check PubMed for your topic (last 7 days)
PUBMED_RESULTS=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=YOUR+TOPIC+AND+last7days[Date+-+Publication]&retmax=20&retmode=json")

# Check bioRxiv
BIOREXIV_RESULTS=$(curl -s "https://api.biorxiv.org/details/biorxiv/0")

# Check OpenAlex (last 30 days)
OPENALEX_RESULTS=$(curl -s "https://api.openalex.org/works?search=YOUR+TOPIC&filter=from_publication_date:2024-01-01&sort=date:desc&per_page=20")

# Process and report new papers
echo "=== New Papers Found ==="
# Process each source...
```

### Option 3: Cron Job for Automated Monitoring

```bash
# Use Hermes cron to monitor papers daily
cronjob action=create \
  name="Daily Literature Monitor" \
  schedule="0 9 * * *" \
  prompt="Check for new papers on the following topics: 1) vestibular disorders and eye tracking 2) ADHD and attention 3) neurorehabilitation. Use PubMed, bioRxiv, and OpenAlex to search. Summarize new papers from the last 7 days, highlight high-impact (most cited) papers, and note any preprints worth tracking."
```

## Topic-Specific Monitoring Sets

### For Vestibular Research

```bash
# PubMed
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%22Vestibular+Diseases%22%5BMeSH%5D+AND+last30days%5BDate+-+Publication%5D&retmax=20&retmode=json"

# OpenAlex
curl -s "https://api.openalex.org/works?search=vestibular+disorder+OR+vestibulo-ocular+reflex+OR+motion+sickness&filter=from_publication_date:2024-01-01&sort=date:desc&per_page=20"

# bioRxiv Neuroscience
curl -s "https://api.biorxiv.org/details/biorxiv/Neuroscience"
```

### For ADHD Research

```bash
# PubMed
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%22Attention+Deficit+Disorder+with+Hyperactivity%22%5BMeSH%5D+AND+last30days%5BDate+-+Publication%5D&retmax=20&retmode=json"

# OpenAlex
curl -s "https://api.openalex.org/works?search=ADHD+OR+attention+deficit+OR+hyperactivity+disorder&filter=from_publication_date:2024-01-01&sort=date:desc&per_page=20"
```

### For Neuroscience/Brain Research

```bash
# arXiv
curl -s "https://export.arxiv.org/api/query?cat=q-bio.NC+OR+cs.NE&sortBy=submittedDate&sortOrder=descending&max_results=20"

# OpenAlex
curl -s "https://api.openalex.org/works?search=brain+OR+neuroscience+OR+cognitive&filter=from_publication_date:2024-01-01&sort=date:desc&per_page=20"

# bioRxiv
curl -s "https://api.biorxiv.org/details/biorxiv/Neuroscience"
```

## Digest Generation

```bash
# Generate a digest of new papers from all sources
echo "=== Daily Literature Digest ==="
echo "Date: $(date)"
echo ""

echo "--- PubMed (Last 7 Days) ---"
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=YOUR+TOPIC+AND+last7days[Date+-+Publication]&retmax=10&retmode=json" | python3 -c "..."
echo ""

echo "--- bioRxiv (Latest) ---"
curl -s "https://api.biorxiv.org/details/biorxiv/0" | python3 -c "..."
echo ""

echo "--- OpenAlex (Recent) ---"
curl -s "https://api.openalex.org/works?search=YOUR+TOPIC&filter=from_publication_date:2024-01-01&sort=date:desc&per_page=10" | python3 -c "..."
echo ""

echo "--- Journal TOC (via blogwatcher) ---"
blogwatcher-cli scan --quiet
blogwatcher-cli articles --recent
```

## Monitoring Checklist

Before setting up continuous monitoring:

1. **Define your topics**: What specific research questions do you want to track?
2. **Choose sources**: Which databases cover your topics best?
3. **Set frequency**: Daily (high-intensity), weekly (standard), or monthly (low-intensity)
4. **Define alert criteria**: Which papers are worth notifying about?
5. **Set up storage**: Where do digests go? (llm-wiki, NotebookLM, email, etc.)

## Alert Criteria

Filter papers to reduce noise:

```
- Citation count > 0 (for papers older than 1 year)
- Open access only (for full-text access)
- Review article only (for overview papers)
- Clinical trial only (for medical research)
- From top 10% most cited journals
- From specific institutions (your collaborators' institutions)
- By specific authors (key researchers in your field)
```

## Pitfalls

- **Too broad queries**: "cancer" will return hundreds of papers. Be specific with your search terms.
- **Rate limiting**: While OpenAlex and bioRxiv have no limits, PubMed has 3 req/s (free) or 10 req/s (with key). Add delays between queries.
- **Duplicate detection**: The same paper may appear in multiple sources (preprint → journal). Deduplicate by DOI.
- **Stale feeds**: Journal RSS feeds may change URLs. Check periodically.
- **Over-monitoring**: Don't track too many topics simultaneously. Focus on 3-5 core research areas.
- **Language barriers**: Most papers are in English. Non-English papers may be missed unless specifically searched.
- **Citation lag**: New papers won't have citations yet. Don't use citation count as the only quality indicator for very recent papers.

## Related Skills

- `blogwatcher` — RSS feed monitoring infrastructure
- `pubmed` — PubMed search
- `arxiv` — arXiv search
- `biorxiv` — bioRxiv/medRxiv search
- `openalex` — OpenAlex search
- `llm-wiki` — Knowledge base storage for digested papers
- `notebooklm-cli` — AI-powered analysis of new papers
