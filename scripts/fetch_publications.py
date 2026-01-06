#!/usr/bin/env python3
"""
Fetch publications from PubMed for the MacCoss Lab and update publications.md

This script uses the NCBI E-utilities API to fetch recent publications
and updates the publications page with new entries. It also scrapes
Google Scholar for citation metrics.
"""

import requests
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server/CI
import matplotlib.pyplot as plt

# Configuration
PUBMED_SEARCH_TERM = 'Maccoss, Michael[Full Author Name] OR MacCoss MJ[Author]'
PUBLICATIONS_FILE = Path(__file__).parent.parent / 'pages' / 'publications.md'
MAX_RESULTS = 1000  # Fetch all publications

# Google Scholar profile URL
GOOGLE_SCHOLAR_URL = 'https://scholar.google.com/citations?user=icweOB0AAAAJ&hl=en'
GOOGLE_SCHOLAR_SORTED_URL = 'https://scholar.google.com/citations?user=icweOB0AAAAJ&hl=en&sortby=pubdate'

# Output paths
PLOT_OUTPUT_FILE = Path(__file__).parent.parent / 'assets' / 'images' / 'publication-metrics.png'
RESOURCES_FILE = Path(__file__).parent.parent / 'pages' / 'resources.md'

# NCBI E-utilities base URLs
ESEARCH_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
EFETCH_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'


def search_pubmed(query, max_results=30):
    """Search PubMed and return a list of PMIDs."""
    params = {
        'db': 'pubmed',
        'term': query,
        'retmax': max_results,
        'sort': 'date',
        'retmode': 'json'
    }
    
    response = requests.get(ESEARCH_URL, params=params)
    response.raise_for_status()
    data = response.json()
    
    return data.get('esearchresult', {}).get('idlist', [])


def fetch_publication_details(pmids):
    """Fetch detailed publication information for given PMIDs."""
    if not pmids:
        return []
    
    # Process in batches to avoid timeout
    batch_size = 200
    all_publications = []
    
    for i in range(0, len(pmids), batch_size):
        batch_pmids = pmids[i:i + batch_size]
        params = {
            'db': 'pubmed',
            'id': ','.join(batch_pmids),
            'retmode': 'xml'
        }
        
        response = requests.get(EFETCH_URL, params=params, timeout=60)
        response.raise_for_status()
        
        batch_pubs = parse_pubmed_xml(response.text)
        all_publications.extend(batch_pubs)
    
    return all_publications


def parse_pubmed_xml(xml_text):
    """Parse PubMed XML response and extract publication details."""
    publications = []
    root = ET.fromstring(xml_text)
    
    for article in root.findall('.//PubmedArticle'):
        pub = {}
        
        # Get PMID
        pmid = article.find('.//PMID')
        pub['pmid'] = pmid.text if pmid is not None else ''
        
        # Get title - use itertext() to handle embedded tags like <i>gene</i>
        title = article.find('.//ArticleTitle')
        if title is not None:
            pub['title'] = ''.join(title.itertext())
        else:
            pub['title'] = ''
        
        # Get authors
        authors = []
        for author in article.findall('.//Author'):
            lastname = author.find('LastName')
            initials = author.find('Initials')
            if lastname is not None:
                name = lastname.text
                if initials is not None:
                    name += ' ' + initials.text
                authors.append(name)
        pub['authors'] = ', '.join(authors)
        
        # Get journal
        journal = article.find('.//Journal/Title')
        pub['journal'] = journal.text if journal is not None else ''
        
        # Get publication date
        pub_date = article.find('.//PubDate')
        if pub_date is not None:
            year = pub_date.find('Year')
            month = pub_date.find('Month')
            day = pub_date.find('Day')
            
            pub['year'] = year.text if year is not None else ''
            pub['month'] = month.text if month is not None else ''
            pub['day'] = day.text if day is not None else ''
        else:
            pub['year'] = ''
            pub['month'] = ''
            pub['day'] = ''
        
        # Get volume and pages
        volume = article.find('.//Volume')
        issue = article.find('.//Issue')
        pages = article.find('.//MedlinePgn')
        
        pub['volume'] = volume.text if volume is not None else ''
        pub['issue'] = issue.text if issue is not None else ''
        pub['pages'] = pages.text if pages is not None else ''
        
        # Get DOI
        doi = None
        for article_id in article.findall('.//ArticleId'):
            if article_id.get('IdType') == 'doi':
                doi = article_id.text
                break
        pub['doi'] = doi
        
        publications.append(pub)
    
    return publications


def format_publication(pub):
    """Format a publication as markdown."""
    lines = []
    
    # Title
    title = pub['title'].rstrip('.')
    lines.append(f"**{title}**")
    
    # Authors
    lines.append(pub['authors'])
    
    # Journal and date
    journal_info = f"*{pub['journal']}*"
    if pub['year']:
        journal_info += f" {pub['year']}"
        if pub['month']:
            journal_info += f" {pub['month']}"
    if pub['volume']:
        journal_info += f";{pub['volume']}"
        if pub['issue']:
            journal_info += f"({pub['issue']})"
    if pub['pages']:
        journal_info += f":{pub['pages']}"
    
    lines.append(journal_info)
    
    # Links
    links = []
    links.append(f"[PubMed](https://pubmed.ncbi.nlm.nih.gov/{pub['pmid']}/)")
    if pub['doi']:
        links.append(f"[DOI](https://doi.org/{pub['doi']})")
    lines.append(' | '.join(links))
    
    return '\n'.join(lines)


def get_existing_pmids(content):
    """Extract PMIDs already in the publications file."""
    pmid_pattern = r'pubmed\.ncbi\.nlm\.nih\.gov/(\d+)'
    return set(re.findall(pmid_pattern, content))


def is_preprint(pub):
    """
    Check if a publication is a preprint.
    """
    journal_lower = pub.get('journal', '').lower()
    preprint_journals = ['biorxiv', 'arxiv', 'medrxiv', 'preprint', 'chemrxiv', 'ssrn']
    return any(preprint in journal_lower for preprint in preprint_journals)


def count_publication_types(publications):
    """
    Count peer-reviewed publications and preprints.
    Returns (total, peer_reviewed, preprints).
    """
    preprints = sum(1 for pub in publications if is_preprint(pub))
    peer_reviewed = len(publications) - preprints
    return len(publications), peer_reviewed, preprints


def update_publications_file(publications, existing_pmids):
    """
    Completely regenerate the publications.md file with all publications grouped by year.
    Publications are sorted in reverse chronological order with year-based navigation.
    """
    if not publications:
        print("No publications found.")
        return False
    
    print(f"Processing {len(publications)} publications")
    
    # Group publications by year
    pubs_by_year = {}
    for pub in publications:
        year = pub.get('year', '')
        if year:
            try:
                year = int(year)
                if year not in pubs_by_year:
                    pubs_by_year[year] = []
                pubs_by_year[year].append(pub)
            except ValueError:
                pass
    
    # Sort years in reverse order (newest first)
    sorted_years = sorted(pubs_by_year.keys(), reverse=True)
    
    # Read existing content to preserve the header and metrics section
    content = PUBLICATIONS_FILE.read_text()
    
    # Extract the header portion (everything up to and including the plot)
    header_end_marker = "![Publication and Citation Metrics](../assets/images/publication-metrics.png)"
    if header_end_marker in content:
        header_end = content.find(header_end_marker) + len(header_end_marker)
        header_content = content[:header_end]
    else:
        # Fallback: create minimal header
        header_content = """---
layout: default
title: Publications
permalink: /publications/
---

# Publications

View our complete publication list on [Google Scholar](https://scholar.google.com/citations?user=icweOB0AAAAJ&hl=en) or search [PubMed](https://pubmed.ncbi.nlm.nih.gov/?term=Maccoss%2C+Michael%5BFull+Author+Name%5D+OR+MacCoss+MJ%5BAuthor%5D&sort=date).

## Publication Metrics

- **Total Citations**: -- ([Google Scholar](https://scholar.google.com/citations?user=icweOB0AAAAJ&hl=en))
- **h-index**: --
- **Most Cited Paper**: "Skyline: an open source document editor for creating and analyzing targeted proteomics experiments" (-- citations)

![Publication and Citation Metrics](../assets/images/publication-metrics.png)"""
    
    # Get current date and total publication count
    current_date = datetime.now().strftime("%B %d, %Y")
    total_pubs = sum(len(pubs) for pubs in pubs_by_year.values())
    
    # Build the new publications section with year navigation
    pubs_section = f"""

*Last updated: {current_date} — {total_pubs} publications*

## Publications by Year

<div class="publications-container">
<div class="year-navigation">
"""
    
    # Add year buttons
    for year in sorted_years:
        count = len(pubs_by_year[year])
        active_class = " active" if year == sorted_years[0] else ""
        pubs_section += f'<button class="year-button{active_class}" onclick="showYear(event, \'{year}\')">{year} ({count})</button>\n'
    
    pubs_section += """</div>
<div class="publications-content">
"""
    
    # Add publication content for each year
    for year in sorted_years:
        active_class = " active" if year == sorted_years[0] else ""
        pubs_section += f'\n<div id="year-{year}" class="year-content{active_class}" markdown="1">\n\n'
        pubs_section += f'### {year}\n\n'
        
        # Sort publications within the year (try to sort by month if available)
        year_pubs = pubs_by_year[year]
        # Publications are already sorted by date from PubMed, so just use them
        
        for pub in year_pubs:
            pubs_section += format_publication(pub) + '\n\n'
        
        pubs_section += '</div>\n'
    
    pubs_section += """</div>
</div>

<style>
.publications-container {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.year-navigation {
  flex: 0 0 120px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  position: sticky;
  top: 20px;
  height: fit-content;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}

.year-button {
  background-color: #f8f9fa;
  border: 1px solid #e0e0e0;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  border-radius: 5px;
  transition: all 0.2s ease;
  color: #333;
  text-align: left;
}

.year-button:hover {
  background-color: #e9ecef;
  color: #0056b3;
}

.year-button.active {
  background-color: #0056b3;
  color: white;
  border-color: #0056b3;
}

.publications-content {
  flex: 1;
  min-width: 0;
}

.year-content {
  display: none;
}

.year-content.active {
  display: block;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@media (max-width: 768px) {
  .publications-container {
    flex-direction: column;
  }
  
  .year-navigation {
    flex: none;
    flex-direction: row;
    flex-wrap: wrap;
    position: static;
    max-height: none;
    gap: 8px;
  }
  
  .year-button {
    padding: 6px 10px;
    font-size: 13px;
  }
}
</style>

<script>
function showYear(evt, year) {
  var i, yearContent, yearButtons;
  
  // Hide all year content
  yearContent = document.getElementsByClassName("year-content");
  for (i = 0; i < yearContent.length; i++) {
    yearContent[i].classList.remove("active");
  }
  
  // Remove active class from all year buttons
  yearButtons = document.getElementsByClassName("year-button");
  for (i = 0; i < yearButtons.length; i++) {
    yearButtons[i].classList.remove("active");
  }
  
  // Show the selected year content and mark button as active
  document.getElementById("year-" + year).classList.add("active");
  evt.currentTarget.classList.add("active");
  
  // Update URL hash without scrolling
  if (history.pushState) {
    history.pushState(null, null, '#' + year);
  }
}

// Handle initial load and hash changes
function handleYearHash() {
  var hash = window.location.hash.substring(1);
  if (hash && !isNaN(hash)) {
    var yearButton = null;
    var buttons = document.getElementsByClassName('year-button');
    for (var i = 0; i < buttons.length; i++) {
      if (buttons[i].getAttribute('onclick').includes("'" + hash + "'")) {
        yearButton = buttons[i];
        break;
      }
    }
    if (yearButton) {
      yearButton.click();
    }
  }
}

// Listen for hash changes
window.addEventListener('hashchange', handleYearHash);

// Handle initial page load
document.addEventListener('DOMContentLoaded', handleYearHash);
</script>
"""
    
    # Combine header and publications
    new_content = header_content + pubs_section
    
    PUBLICATIONS_FILE.write_text(new_content)
    print(f"Regenerated {PUBLICATIONS_FILE} with {len(publications)} publications across {len(sorted_years)} years")
    return True


def fetch_google_scholar_metrics():
    """
    Fetch citation metrics from Google Scholar profile.
    
    Returns a dict with:
    - total_citations: Total number of citations
    - h_index: h-index value
    - most_cited_count: Citation count of the most cited paper
    - most_cited_title: Title of the most cited paper
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        # Fetch the main profile page for citation stats
        response = requests.get(GOOGLE_SCHOLAR_URL, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract citation metrics from the stats table
        # The table has class gsc_rsb_st and contains rows with gsc_rsb_std class cells
        total_citations = None
        h_index = None
        
        # Find all table cells with gsc_rsb_std class (these contain the metric values)
        # Structure: row 1 = Citations (All, Since YYYY), row 2 = h-index, row 3 = i10-index
        stats_cells = soup.find_all('td', class_='gsc_rsb_std')
        
        if len(stats_cells) >= 4:
            # First cell is "All" citations, second is "Since YYYY" citations
            # Third cell is "All" h-index, fourth is "Since YYYY" h-index
            try:
                citations_text = stats_cells[0].get_text(strip=True)
                if citations_text:
                    total_citations = int(citations_text.replace(',', ''))
            except (ValueError, IndexError):
                pass
            
            try:
                h_index_text = stats_cells[2].get_text(strip=True)
                if h_index_text:
                    h_index = int(h_index_text.replace(',', ''))
            except (ValueError, IndexError):
                pass
        
        # Find the most cited paper - it's the first one by default (sorted by citations)
        # We need to look at the publications list
        most_cited_count = None
        most_cited_title = None
        
        # The publications are in gsc_a_tr rows
        pub_rows = soup.find_all('tr', class_='gsc_a_tr')
        if pub_rows:
            # The default sort is by citations, so first paper is most cited
            first_pub = pub_rows[0]
            title_elem = first_pub.find('a', class_='gsc_a_at')
            cite_elem = first_pub.find('a', class_='gsc_a_ac')
            
            if title_elem:
                most_cited_title = title_elem.get_text(strip=True)
            if cite_elem:
                cite_text = cite_elem.get_text(strip=True)
                if cite_text:
                    most_cited_count = int(cite_text.replace(',', ''))
        
        print("Google Scholar metrics fetched:")
        print(f"  Total citations: {total_citations}")
        print(f"  h-index: {h_index}")
        print(f"  Most cited paper: {most_cited_count} citations")
        if most_cited_title:
            print(f"    Title: {most_cited_title[:60]}...")
        
        return {
            'total_citations': total_citations,
            'h_index': h_index,
            'most_cited_count': most_cited_count,
            'most_cited_title': most_cited_title
        }
        
    except requests.RequestException as e:
        print(f"Error fetching Google Scholar data: {e}")
        return None
    except Exception as e:
        print(f"Error parsing Google Scholar data: {e}")
        return None


def update_publication_metrics(metrics, pub_counts=None):
    """Update the Publication Metrics section in publications.md with Google Scholar data."""
    if not metrics and not pub_counts:
        print("No metrics to update")
        return False
    
    content = PUBLICATIONS_FILE.read_text()
    
    updated = False
    
    # Update total publications count
    if pub_counts:
        total, peer_reviewed, preprints = pub_counts
        # Match pattern like: - **Total Publications**: 334 (312 peer-reviewed + 22 preprints)
        pattern = r'\*\*Total Publications\*\*:\s*\d+\s*\(\d+\s*peer-reviewed\s*\+\s*\d+\s*preprints\)'
        replacement = f"**Total Publications**: {total} ({peer_reviewed} peer-reviewed + {preprints} preprints)"
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            updated = True
            print(f"Updated total publications to {total} ({peer_reviewed} peer-reviewed + {preprints} preprints)")
    
    # Update total citations
    if metrics and metrics.get('total_citations'):
        # Match pattern like: - **Total Citations**: 51,611
        pattern = r'(\*\*Total Citations\*\*:\s*>?)[\d,]+'
        replacement = f"**Total Citations**: {metrics['total_citations']:,}"
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            updated = True
            print(f"Updated total citations to {metrics['total_citations']:,}")
    
    # Update h-index
    if metrics and metrics.get('h_index'):
        # Match pattern like: - **h-index**: 103
        pattern = r'(\*\*h-index\*\*:\s*>?)\d+'
        replacement = f"**h-index**: {metrics['h_index']}"
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            updated = True
            print(f"Updated h-index to {metrics['h_index']}")
    
    # Update most cited paper citation count
    if metrics and metrics.get('most_cited_count'):
        # Match pattern like: (5,169 citations)
        pattern = r'\([\d,]+\+?\s*citations\)'
        replacement = f"({metrics['most_cited_count']:,} citations)"
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            updated = True
            print(f"Updated most cited paper to {metrics['most_cited_count']:,} citations)")
    
    if updated:
        PUBLICATIONS_FILE.write_text(content)
        print(f"Updated publication metrics in {PUBLICATIONS_FILE}")
        return True
    else:
        print("No metrics were updated")
        return False


def fetch_paper_citations_from_scholar(soup, search_terms):
    """
    Find citation counts for specific papers from a Google Scholar profile page.
    
    Args:
        soup: BeautifulSoup object of the Google Scholar profile page
        search_terms: dict mapping paper_key to a list of search terms to match in title
    
    Returns:
        dict mapping paper_key to citation count (or None if not found)
    """
    results = {key: None for key in search_terms}
    
    # Get all publication rows
    pub_rows = soup.find_all('tr', class_='gsc_a_tr')
    
    for row in pub_rows:
        title_elem = row.find('a', class_='gsc_a_at')
        cite_elem = row.find('a', class_='gsc_a_ac')
        
        if not title_elem:
            continue
            
        title = title_elem.get_text(strip=True).lower()
        
        for paper_key, terms in search_terms.items():
            if results[paper_key] is not None:
                continue  # Already found
            
            # Check if all search terms are in the title
            if all(term.lower() in title for term in terms):
                if cite_elem:
                    cite_text = cite_elem.get_text(strip=True)
                    if cite_text:
                        try:
                            results[paper_key] = int(cite_text.replace(',', ''))
                        except ValueError:
                            pass
    
    return results


def update_software_citations(metrics):
    """
    Update citation counts for software papers in resources.md.
    
    Uses Google Scholar data to update:
    - Skyline paper (MacLean et al, 2010)
    - ProteoWizard paper (Chambers et al, 2012)
    """
    if not RESOURCES_FILE.exists():
        print(f"Resources file not found: {RESOURCES_FILE}")
        return False
    
    # Get citation counts - Skyline is already in metrics as most_cited
    skyline_citations = metrics.get('most_cited_count') if metrics else None
    proteowizard_citations = None
    
    # Need to fetch ProteoWizard citation from Google Scholar
    # We'll look for "cross-platform toolkit for mass spectrometry" in the profile
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(GOOGLE_SCHOLAR_URL, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Search for ProteoWizard paper
        paper_searches = {
            'proteowizard': ['cross-platform', 'toolkit', 'proteomics']
        }
        
        paper_citations = fetch_paper_citations_from_scholar(soup, paper_searches)
        proteowizard_citations = paper_citations.get('proteowizard')
        
    except Exception as e:
        print(f"Error fetching ProteoWizard citations: {e}")
    
    # Update resources.md
    content = RESOURCES_FILE.read_text()
    updated = False
    
    # Update Skyline citation count
    if skyline_citations:
        # Match pattern like: **Cited:** >5098 times
        pattern = r'(\*\*Cited:\*\*\s*>?)[\d,]+(\s*times)'
        # First occurrence is Skyline
        match = re.search(pattern, content)
        if match:
            replacement = f"**Cited:** {skyline_citations:,} times"
            # Replace only the first occurrence (Skyline)
            content = content[:match.start()] + replacement + content[match.end():]
            updated = True
            print(f"Updated Skyline citation count to {skyline_citations:,}")
    
    # Update ProteoWizard citation count
    if proteowizard_citations:
        # Find the second occurrence of the citation pattern
        pattern = r'(\*\*Cited:\*\*\s*>?)[\d,]+(\s*times)'
        matches = list(re.finditer(pattern, content))
        if len(matches) >= 2:
            match = matches[1]  # Second occurrence is ProteoWizard
            replacement = f"**Cited:** {proteowizard_citations:,} times"
            content = content[:match.start()] + replacement + content[match.end():]
            updated = True
            print(f"Updated ProteoWizard citation count to {proteowizard_citations:,}")
    
    if updated:
        RESOURCES_FILE.write_text(content)
        print(f"Updated software citation counts in {RESOURCES_FILE}")
        return True
    else:
        print("No software citation counts were updated")
        return False


def fetch_publications_per_year():
    """
    Fetch publication counts per year from PubMed.
    Returns a dict of {year: count}.
    """
    # Search for all publications (not limited to recent)
    params = {
        'db': 'pubmed',
        'term': PUBMED_SEARCH_TERM,
        'retmax': 1000,  # Get all publications
        'retmode': 'json'
    }
    
    try:
        response = requests.get(ESEARCH_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        pmids = data.get('esearchresult', {}).get('idlist', [])
        
        if not pmids:
            return {}
        
        # Fetch details for all PMIDs to get publication years
        # Process in batches to avoid timeout
        batch_size = 200
        all_years = []
        
        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i:i + batch_size]
            params = {
                'db': 'pubmed',
                'id': ','.join(batch_pmids),
                'retmode': 'xml'
            }
            response = requests.get(EFETCH_URL, params=params, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            for article in root.findall('.//PubmedArticle'):
                pub_date = article.find('.//PubDate')
                if pub_date is not None:
                    year_elem = pub_date.find('Year')
                    if year_elem is not None:
                        try:
                            year = int(year_elem.text)
                            all_years.append(year)
                        except (ValueError, TypeError):
                            pass
        
        # Count publications per year
        year_counts = {}
        for year in all_years:
            year_counts[year] = year_counts.get(year, 0) + 1
        
        print(f"Fetched publication counts for {len(year_counts)} years ({len(all_years)} total publications)")
        return year_counts
        
    except Exception as e:
        print(f"Error fetching publications per year: {e}")
        return {}


def fetch_citations_per_year():
    """
    Fetch citations per year from Google Scholar.
    Returns a dict of {year: count}.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(GOOGLE_SCHOLAR_URL, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the citation graph data - it's in a script or in the chart elements
        # Google Scholar has a "Citations per year" section with class gsc_md_hist_b
        # The years are in elements with class gsc_g_t and counts in gsc_g_al
        
        year_elements = soup.find_all('span', class_='gsc_g_t')
        count_elements = soup.find_all('span', class_='gsc_g_al')
        
        citations_per_year = {}
        
        if year_elements and count_elements and len(year_elements) == len(count_elements):
            for year_elem, count_elem in zip(year_elements, count_elements):
                try:
                    year = int(year_elem.get_text(strip=True))
                    count = int(count_elem.get_text(strip=True).replace(',', ''))
                    citations_per_year[year] = count
                except (ValueError, TypeError):
                    pass
        
        if citations_per_year:
            print(f"Fetched citation counts for {len(citations_per_year)} years")
        else:
            print("Could not parse citations per year from Google Scholar")
            
        return citations_per_year
        
    except Exception as e:
        print(f"Error fetching citations per year: {e}")
        return {}


def generate_metrics_plot(pubs_per_year, citations_per_year):
    """
    Generate a two-panel plot showing publications per year and citations per year.
    Saves the plot to assets/images/publication-metrics.png
    """
    if not pubs_per_year and not citations_per_year:
        print("No data available for plot generation")
        return False
    
    # Create figure with two subplots (shorter height)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 3.5))
    
    # Define colors (same color for both panels)
    pub_color = '#2E86AB'  # Blue
    cite_color = '#2E86AB'  # Blue (matching publications)
    
    # Left panel: Publications per year
    if pubs_per_year:
        years = sorted(pubs_per_year.keys())
        counts = [pubs_per_year[y] for y in years]
        
        ax1.bar(years, counts, color=pub_color, edgecolor='white', linewidth=0.5)
        ax1.set_xlabel('Year', fontsize=11)
        ax1.set_ylabel('Number of Publications', fontsize=11)
        ax1.set_title('Publications per Year', fontsize=13, fontweight='bold')
        ax1.set_xlim(min(years) - 0.5, max(years) + 0.5)
        ax1.set_ylim(0, max(counts) * 1.1)
        
        # Add gridlines
        ax1.yaxis.grid(True, linestyle='--', alpha=0.3)
        ax1.set_axisbelow(True)
        
        # Rotate x-axis labels for better readability
        ax1.tick_params(axis='x', rotation=45)
    else:
        ax1.text(0.5, 0.5, 'No publication data available', 
                ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Publications per Year', fontsize=13, fontweight='bold')
    
    # Right panel: Citations per year
    if citations_per_year:
        years = sorted(citations_per_year.keys())
        counts = [citations_per_year[y] for y in years]
        
        ax2.bar(years, counts, color=cite_color, edgecolor='white', linewidth=0.5)
        ax2.set_xlabel('Year', fontsize=11)
        ax2.set_ylabel('Number of Citations', fontsize=11)
        ax2.set_title('Citations per Year', fontsize=13, fontweight='bold')
        ax2.set_xlim(min(years) - 0.5, max(years) + 0.5)
        ax2.set_ylim(0, max(counts) * 1.1)
        
        # Add gridlines
        ax2.yaxis.grid(True, linestyle='--', alpha=0.3)
        ax2.set_axisbelow(True)
        
        # Rotate x-axis labels for better readability
        ax2.tick_params(axis='x', rotation=45)
    else:
        ax2.text(0.5, 0.5, 'No citation data available', 
                ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Citations per Year', fontsize=13, fontweight='bold')
    
    # Adjust layout
    plt.tight_layout()
    
    # Ensure output directory exists
    PLOT_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the plot
    plt.savefig(PLOT_OUTPUT_FILE, dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"Generated metrics plot: {PLOT_OUTPUT_FILE}")
    return True


def main():
    # First, update Google Scholar metrics and get citations per year
    print("Fetching Google Scholar metrics...")
    metrics = fetch_google_scholar_metrics()
    
    # Fetch citations per year for the plot
    print()
    print("Fetching citations per year...")
    citations_per_year = fetch_citations_per_year()
    
    print()  # Blank line for readability
    print(f"Searching PubMed for: {PUBMED_SEARCH_TERM}")
    
    # Search for ALL publications
    pmids = search_pubmed(PUBMED_SEARCH_TERM, MAX_RESULTS)
    print(f"Found {len(pmids)} publications")
    
    if not pmids:
        print("No publications found")
        return
    
    # Fetch publication details
    publications = fetch_publication_details(pmids)
    print(f"Fetched details for {len(publications)} publications")
    
    # Count publication types (peer-reviewed vs preprints)
    pub_counts = count_publication_types(publications)
    total, peer_reviewed, preprints = pub_counts
    print(f"Publication breakdown: {peer_reviewed} peer-reviewed + {preprints} preprints = {total} total")
    
    # Update publication metrics (Google Scholar + publication counts)
    if metrics or pub_counts:
        update_publication_metrics(metrics, pub_counts)
    else:
        print("Could not fetch metrics")
    
    # Update software citation counts in resources.md
    print()
    print("Updating software citation counts in resources.md...")
    update_software_citations(metrics)
    
    # Regenerate the entire publications file with year navigation
    update_publications_file(publications, set())
    
    # Fetch publications per year and generate the plot
    print()
    print("Fetching publications per year for plot...")
    pubs_per_year = fetch_publications_per_year()
    
    print()
    print("Generating metrics plot...")
    generate_metrics_plot(pubs_per_year, citations_per_year)


if __name__ == '__main__':
    main()
