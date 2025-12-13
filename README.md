# MacCoss Lab Website

This is the website for the MacCoss Lab at the University of Washington. It can be viewed at: [https://uw-maccosslab.github.io/](https://uw-maccosslab.github.io/) and [https://maccosslab.org](https://maccosslab.org)

## Technical Overview

This website is built using **Jekyll** with the **Minima** theme and hosted on **GitHub Pages**. It features responsive design, tabbed navigation, RSS feeds, and organized content management.

## 📁 Site Structure

```
├── _config.yml              # Jekyll configuration
├── _layouts/
│   ├── default.html         # Custom layout with consistent width
│   └── post.html           # Blog post template
├── _posts/                  # News/blog posts for RSS feed
│   ├── 2024-XX-XX-title.md # Individual news posts
├── assets/
│   ├── css/
│   │   └── style.scss      # Custom styling and responsive design
│   └── images/
│       ├── logos/          # All software/lab logos
│       ├── instruments/    # Mass spectrometer photos
│       ├── people/         # Lab member photos
│       └── *.jpg          # General photos (lab photo, etc.)
├── pages/                  # Main site pages
│   ├── contact.md
│   ├── funding.md         # Tabbed funding sources
│   ├── news.md            # News/blog listing with RSS
│   ├── people.md          # Lab members with tabs
│   ├── positions.md
│   ├── publications.md
│   └── resources.md       # Tabbed resources (instruments, software, etc.)
└── index.md               # Homepage
```

## Layout & Styling

### Custom Width System
- **Main content**: 1400px max-width on large screens
- **Responsive**: Full width on mobile (≤800px)
- **Consistent alignment**: Header, content, and footer all use same width
- **Implementation**: Custom `_layouts/default.html` + CSS in `assets/css/style.scss`

### Responsive Design
```scss
/* Large screens */
.page-content .wrapper { max-width: 1400px; }

/* Mobile screens (≤768px) */
@media (max-width: 768px) {
  .page-content .wrapper { max-width: 100%; padding: 0 15px; }
}
```

### Tab Navigation System
Multiple pages use JavaScript-powered tabbed interfaces:
- **Resources**: Instrumentation, Software, Datasets, Educational, Support
- **People**: Current Members, Alumni  
- **Funding**: NIH, DOE, IARPA, Foundations

**Implementation**: CSS classes + JavaScript in each page's `<script>` section
- `.tab-container`, `.tab-navigation`, `.tab-button`, `.tab-content`
- URL hash support (`#tabname`) for direct linking
- Mobile-responsive (stacked on small screens)

## Image Organization

### Directory Structure
```
assets/images/
├── logos/              # Software logos, lab logo
│   ├── lab-logo.jpg
│   ├── skyline_logo_h_blue.jpg
│   ├── panorama_logo_h_onwhite_border.png
│   ├── proteowizard-logo.jpg
│   ├── limelight-page-logo.png
│   ├── encyclopedia_logo_small.png
│   ├── cometlogo_1_small.png
│   ├── crux-logo.png
│   └── percolator.png
├── instruments/        # Mass spectrometer photos
│   ├── astral.jpg
│   ├── stellar.jpg
│   ├── eclipse.jpg
│   ├── exploris480.jpg
│   ├── lumos1.jpg      # Side-by-side pair
│   ├── lumos2.jpg      # Side-by-side pair
│   ├── qe-hf.jpg
│   └── tsqaltis.jpg
├── people/            # Lab member headshots
│   └── mike-maccoss.jpg
└── maccoss-lab-photo-2025.jpg  # Group photos
```

### Image Sizing
- **Instrumentation images**: 400px max-width on desktop, 300px on mobile
- **Logo images**: Varies by logo, responsive
- **Fusion Lumos pair**: 150px each, side-by-side layout
- **People photos**: Responsive sizing

```scss
/* Instrumentation tab images */
#instrumentation img {
  max-width: 400px !important;
  width: 75% !important;
}

/* Paired instruments (Fusion Lumos) */
.instrument-pair .instrument-item img {
  width: 150px !important;
}
```

## News & RSS Feed

### RSS Implementation
The site uses **Jekyll-feed plugin** to generate RSS at `/feed.xml`

### Adding News Posts
1. Create file in `_posts/` directory
2. Use naming format: `YYYY-MM-DD-title.md`
3. Include front matter:
```yaml
---
layout: post
title: "Your Post Title"
date: 2024-XX-XX
categories: [category1, category2]
---
```

### News Page (`pages/news.md`)
- Automatically lists all posts from `_posts/`
- Shows title, date, excerpt, categories
- Links to RSS feed
- Styled with `.news-item`, `.post-meta`, `.category-tag` classes

## Automated Publication Updates

The site includes a GitHub Actions workflow that automatically updates publications from PubMed and Google Scholar.

### What Gets Updated
- **New publications** from PubMed (searches for MacCoss MJ as author)
- **Total citations** from Google Scholar profile
- **h-index** from Google Scholar
- **Most cited paper** citation count from Google Scholar
- **Metrics plot** showing publications per year (PubMed) and citations per year (Google Scholar)

### Workflow Schedule
- **Automatic**: Runs weekly on Sundays at midnight UTC
- **Manual**: Can be triggered anytime from Actions tab

### How It Works
1. Workflow runs `scripts/fetch_publications.py`
2. Script fetches Google Scholar metrics and updates the Publication Metrics section
3. Script searches PubMed for recent publications
4. If changes detected, creates a Pull Request for review
5. PR includes all new publications and updated metrics

### Manual Trigger
1. Go to **Actions** tab in GitHub
2. Select **"Update Publications from PubMed"**
3. Click **"Run workflow"**
4. Review and merge the resulting PR

### Dependencies
The workflow installs these Python packages:
- `requests` - HTTP requests for API calls
- `beautifulsoup4` - HTML parsing for Google Scholar scraping
- `matplotlib` - Generating the publication/citation plots
- `numpy` - Numerical support for plotting

### Files Involved
```
├── scripts/
│   └── fetch_publications.py    # Main update script
├── .github/workflows/
│   └── update-publications.yml  # GitHub Actions workflow
├── assets/images/
│   └── publication-metrics.png  # Auto-generated metrics plot
└── pages/
    └── publications.md          # Updated by the script
```

### Troubleshooting
- **Google Scholar metrics not updating**: Google may temporarily block requests. The script will continue with PubMed updates and skip metrics.
- **No new publications found**: The script checks for existing PMIDs to avoid duplicates.
- **Workflow not running**: Check that GitHub Actions is enabled for the repository.

## Security Features

### Email Protection
All email addresses use obfuscation to reduce spam:
- Replace `@` with `[at]`
- Replace `.` with `[dot]`
- Example: `maccoss[at]uw[dot]edu`
- *Not sure if this helps at all*

## Making Updates

### Adding New Software/Tools
1. Add logo to `assets/images/logos/`
2. Update `pages/resources.md` in Software tab
3. Use format:
```markdown
### ![Tool Name](../assets/images/logos/logo-file.png "Tool Name")
**Tool description**
- Bullet points with details
- **Download**: [link](url)
```

### Adding New Instruments
1. Add photo to `assets/images/instruments/`
2. Update `pages/resources.md` in Instrumentation tab
3. Follow existing format with instrument name, description, image

### Adding Lab Members
1. Add photo to `assets/images/people/` (if needed)
2. Update `pages/people.md` in appropriate tab
3. Use consistent formatting for names, titles, descriptions

### Updating Funding Information
1. Edit `pages/funding.md`
2. Add content to appropriate tab (NIH, DOE, IARPA, Foundations)
3. Follow existing formatting patterns

## Key CSS Classes

### Layout
- `.page-content .wrapper` - Main content container
- `.site-header .wrapper` - Header container
- `.hero-section` - Homepage hero area
- `.lab-photo` - Lab photo styling

### Navigation
- `.tab-container` - Tab system wrapper
- `.tab-navigation` - Tab button container
- `.tab-button` - Individual tab buttons
- `.tab-content` - Tab content panels

### Content
- `.news-item` - News post styling
- `.post-meta` - Post metadata (date, categories)
- `.category-tag` - Category labels
- `.instrument-pair` - Side-by-side instrument layout
- `.instrument-item` - Individual instrument in pair

### Responsive Utilities
- `@media (max-width: 768px)` - Mobile breakpoint
- `@media (max-width: 800px)` - Content width breakpoint

## Development Tips

### Testing Locally
```bash
bundle exec jekyll serve
```

### Checking for Broken Links
Verify all image paths after moving files, especially:
- Logo references in `index.md` and `pages/resources.md`
- Instrument photos in `pages/resources.md`
- People photos in `pages/people.md`

### Browser Compatibility
- Tested in Chrome, Firefox, Safari, Edge
- Uses modern CSS (flexbox, CSS grid)
- Fallbacks included for older browsers

### Performance
- Images are optimized for web
- CSS is minified by Jekyll
- Responsive images reduce mobile bandwidth

## Content Guidelines

### Writing Style
- Use clear, concise language
- Include relevant links and citations
- Maintain consistent formatting
- Use appropriate headings hierarchy

### Image Guidelines
- Use high-quality images
- Optimize file sizes for web
- Use descriptive alt text
- Maintain consistent aspect ratios where possible

### Accessibility
- All images have alt text
- Proper heading structure
- High contrast colors
- Keyboard navigation support

---

For technical support or questions about the website, contact the lab's web administrator or refer to the Jekyll documentation at [jekyllrb.com](https://jekyllrb.com/).
