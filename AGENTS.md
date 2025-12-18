# Claude AI Context for MacCoss Lab Website

This file provides context for Claude AI when working with this repository.

## Project Overview

This is the **MacCoss Lab website** at the University of Washington, hosted on GitHub Pages at:
- https://uw-maccosslab.github.io/
- https://maccosslab.org

The lab focuses on **mass spectrometry-based proteomics** research, developing methods and software for protein analysis.

## Technology Stack

- **Static Site Generator**: Jekyll with Minima theme
- **Hosting**: GitHub Pages
- **Styling**: SCSS (assets/css/style.scss)

## Key Files and Directories

```
_config.yml              # Jekyll configuration
_layouts/                # Custom HTML layouts
_posts/                  # News/blog posts (for RSS feed)
assets/
  css/style.scss         # Custom styling
  images/                # All images (logos, instruments, people, plots)
pages/                   # Main site content pages
scripts/
  fetch_publications.py  # Automated publication fetcher (run manually)
```

## Automated Publication System

The site has an automated system (`scripts/fetch_publications.py`) that:

1. **Fetches Google Scholar metrics** (total citations, h-index, most cited paper)
2. **Fetches ALL publications from PubMed** (searches for MacCoss MJ as author)
3. **Generates a metrics plot** (publications/citations per year)
4. **Regenerates `pages/publications.md`** with year-based navigation sidebar

### Year-Based Navigation
Publications are displayed with a sidebar showing all years. Clicking a year shows only that year's publications. The layout uses:
- `.publications-container` - flexbox layout with sidebar
- `.year-navigation` - sticky sidebar with year buttons
- `.year-content` - content divs for each year (only one visible at a time)

### Publication Sources
- All publications are fetched from PubMed (including preprints)
- This ensures the sidebar counts match the Publications per Year plot

### Workflow Schedule
- **Run manually**: `python3 scripts/fetch_publications.py`
- GitHub Actions was removed because Google Scholar blocks scraping from CI environments

## Content Guidelines

### Adding Publications
Publications are managed automatically via the script. Manual additions should follow this format:
```markdown
**Paper Title**
Author1, Author2, MacCoss MJ, ...
*Journal Name* Year Month;Volume(Issue):Pages
[PubMed](https://pubmed.ncbi.nlm.nih.gov/PMID/) | [DOI](https://doi.org/...)
```

### Adding News Posts
Create files in `_posts/` with format `YYYY-MM-DD-title.md`:
```yaml
---
layout: post
title: "Post Title"
date: YYYY-MM-DD
categories: [category1, category2]
---
Post content here...
```

### Image Organization
- `assets/images/logos/` - Software and lab logos
- `assets/images/instruments/` - Mass spectrometer photos
- `assets/images/people/` - Lab member headshots
- `assets/images/publication-metrics.png` - Auto-generated plot

## Common Tasks

### Update publications manually
```bash
python3 scripts/fetch_publications.py
```

### Test site locally
```bash
bundle exec jekyll serve
```

### Check for preprints/corrigenda
```bash
grep -i "biorxiv\|arxiv\|corrigendum" pages/publications.md
```

## Dependencies for Scripts

Python packages required:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing for Google Scholar
- `matplotlib` - Plot generation
- `numpy` - Numerical support

## Important Notes

1. **Google Scholar scraping**: May occasionally fail if Google blocks requests. The script handles this gracefully and continues with other updates.

2. **PubMed API**: Uses NCBI E-utilities (no API key required for low-volume requests).

3. **Publication metrics format**: Numbers should NOT have `>` or `+` symbols since they're updated weekly.

4. **Tab navigation**: Multiple pages use JavaScript-based tabs (Resources, People, Funding).

5. **Email obfuscation**: All emails use `[at]` and `[dot]` format to reduce spam.

## Lab Information

- **PI**: Michael MacCoss
- **Institution**: University of Washington, Department of Genome Sciences
- **Research focus**: Quantitative proteomics, mass spectrometry methods, Skyline software development
- **Key software**: Skyline, Panorama, Encyclopedia, Limelight

## When Making Changes

1. Test locally with `bundle exec jekyll serve` when possible
2. Check for broken image paths after moving files
3. Maintain consistent formatting in publication entries
4. Ensure new images are optimized for web
5. Run the publication script to verify it still works after changes
