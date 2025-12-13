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
import time
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server/CI
import matplotlib.pyplot as plt
import numpy as np

# Configuration
PUBMED_SEARCH_TERM = 'Maccoss, Michael[Full Author Name] OR MacCoss MJ[Author]'
PUBLICATIONS_FILE = Path(__file__).parent.parent / 'pages' / 'publications.md'
MAX_RESULTS = 30  # Number of recent publications to fetch

# Google Scholar profile URL
GOOGLE_SCHOLAR_URL = 'https://scholar.google.com/citations?user=icweOB0AAAAJ&hl=en'
GOOGLE_SCHOLAR_SORTED_URL = 'https://scholar.google.com/citations?user=icweOB0AAAAJ&hl=en&sortby=pubdate'

# Output paths
PLOT_OUTPUT_FILE = Path(__file__).parent.parent / 'assets' / 'images' / 'publication-metrics.png'

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
    
    params = {
        'db': 'pubmed',
        'id': ','.join(pmids),
        'retmode': 'xml'
    }
    
    response = requests.get(EFETCH_URL, params=params)
    response.raise_for_status()
    
    return parse_pubmed_xml(response.text)


def parse_pubmed_xml(xml_text):
    """Parse PubMed XML response and extract publication details."""
    publications = []
    root = ET.fromstring(xml_text)
    
    for article in root.findall('.//PubmedArticle'):
        pub = {}
        
        # Get PMID
        pmid = article.find('.//PMID')
        pub['pmid'] = pmid.text if pmid is not None else ''
        
        # Get title
        title = article.find('.//ArticleTitle')
        pub['title'] = title.text if title is not None else ''
        
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


def should_exclude_publication(pub):
    """
    Check if a publication should be excluded from the publications list.
    
    Excludes:
    - Preprints (bioRxiv, arXiv, medRxiv, etc.)
    - Corrigenda, errata, and corrections
    """
    # Check journal name for preprint servers
    journal_lower = pub.get('journal', '').lower()
    preprint_journals = ['biorxiv', 'arxiv', 'medrxiv', 'preprint', 'chemrxiv', 'ssrn']
    if any(preprint in journal_lower for preprint in preprint_journals):
        return True
    
    # Check title for corrigenda, errata, corrections
    title_lower = pub.get('title', '').lower()
    correction_terms = ['corrigendum', 'erratum', 'correction', 'retraction', 'addendum']
    if any(term in title_lower for term in correction_terms):
        return True
    
    return False


def update_publications_file(publications, existing_pmids):
    """Update the publications.md file with new publications."""
    content = PUBLICATIONS_FILE.read_text()
    
    # Filter out publications already in the file
    new_pubs = [p for p in publications if p['pmid'] not in existing_pmids]
    
    # Filter out preprints and corrigenda
    filtered_pubs = []
    excluded_count = 0
    for pub in new_pubs:
        if should_exclude_publication(pub):
            excluded_count += 1
            print(f"  Excluding: {pub['title'][:60]}... ({pub['journal']})")
        else:
            filtered_pubs.append(pub)
    
    if excluded_count > 0:
        print(f"Excluded {excluded_count} preprint(s)/corrigendum(a)")
    
    new_pubs = filtered_pubs
    
    if not new_pubs:
        print("No new publications found.")
        return False
    
    print(f"Found {len(new_pubs)} new publication(s)")
    
    # Group by year
    current_year = datetime.now().year
    
    # Find the insertion point (after "### {current_year}" header)
    year_header = f"### {current_year}"
    
    if year_header in content:
        # Find position after the year header
        header_pos = content.find(year_header)
        insert_pos = content.find('\n', header_pos) + 1
        
        # Skip any blank lines after header
        while insert_pos < len(content) and content[insert_pos] == '\n':
            insert_pos += 1
        
        # Format new publications
        new_content = '\n\n'.join(format_publication(p) for p in new_pubs)
        new_content += '\n\n'
        
        # Insert new publications
        updated_content = content[:insert_pos] + new_content + content[insert_pos:]
        
        PUBLICATIONS_FILE.write_text(updated_content)
        print(f"Updated {PUBLICATIONS_FILE}")
        return True
    else:
        # Year header doesn't exist - we need to create it
        # Find the "## Recent Publications" section and the previous year header
        recent_pubs_header = "## Recent Publications"
        previous_year = current_year - 1
        previous_year_header = f"### {previous_year}"
        
        if recent_pubs_header in content and previous_year_header in content:
            # Find position of previous year header
            prev_year_pos = content.find(previous_year_header)
            
            # Create new year section
            new_year_section = f"### {current_year}\n\n"
            new_year_section += '\n\n'.join(format_publication(p) for p in new_pubs)
            new_year_section += '\n\n'
            
            # Insert new year section before the previous year
            updated_content = content[:prev_year_pos] + new_year_section + content[prev_year_pos:]
            
            PUBLICATIONS_FILE.write_text(updated_content)
            print(f"Created new year header for {current_year} and updated {PUBLICATIONS_FILE}")
            return True
        else:
            print(f"Could not find appropriate insertion point for new publications")
            return False


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
        
        print(f"Google Scholar metrics fetched:")
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


def update_publication_metrics(metrics):
    """Update the Publication Metrics section in publications.md with Google Scholar data."""
    if not metrics:
        print("No metrics to update")
        return False
    
    content = PUBLICATIONS_FILE.read_text()
    
    updated = False
    
    # Update total citations
    if metrics.get('total_citations'):
        # Match pattern like: - **Total Citations**: 51,611
        pattern = r'(\*\*Total Citations\*\*:\s*>?)[\d,]+'
        replacement = f"**Total Citations**: {metrics['total_citations']:,}"
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            updated = True
            print(f"Updated total citations to {metrics['total_citations']:,}")
    
    # Update h-index
    if metrics.get('h_index'):
        # Match pattern like: - **h-index**: 103
        pattern = r'(\*\*h-index\*\*:\s*>?)\d+'
        replacement = f"**h-index**: {metrics['h_index']}"
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            updated = True
            print(f"Updated h-index to {metrics['h_index']}")
    
    # Update most cited paper citation count
    if metrics.get('most_cited_count'):
        # Match pattern like: (5,169 citations)
        pattern = r'\([\d,]+\+?\s*citations\)'
        replacement = f"({metrics['most_cited_count']:,} citations)"
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            updated = True
            print(f"Updated most cited paper to {metrics['most_cited_count']:,} citations")
    
    if updated:
        PUBLICATIONS_FILE.write_text(content)
        print(f"Updated publication metrics in {PUBLICATIONS_FILE}")
        return True
    else:
        print("No metrics were updated")
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
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Define colors
    pub_color = '#2E86AB'  # Blue
    cite_color = '#A23B72'  # Magenta/Pink
    
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
    if metrics:
        update_publication_metrics(metrics)
    else:
        print("Could not fetch Google Scholar metrics")
    
    # Fetch citations per year for the plot
    print()
    print("Fetching citations per year...")
    citations_per_year = fetch_citations_per_year()
    
    print()  # Blank line for readability
    print(f"Searching PubMed for: {PUBMED_SEARCH_TERM}")
    
    # Search for publications
    pmids = search_pubmed(PUBMED_SEARCH_TERM, MAX_RESULTS)
    print(f"Found {len(pmids)} publications")
    
    if not pmids:
        print("No publications found")
        return
    
    # Fetch publication details
    publications = fetch_publication_details(pmids)
    print(f"Fetched details for {len(publications)} publications")
    
    # Get existing PMIDs from the file
    content = PUBLICATIONS_FILE.read_text()
    existing_pmids = get_existing_pmids(content)
    print(f"Found {len(existing_pmids)} existing publications in file")
    
    # Update the file
    update_publications_file(publications, existing_pmids)
    
    # Fetch publications per year and generate the plot
    print()
    print("Fetching publications per year for plot...")
    pubs_per_year = fetch_publications_per_year()
    
    print()
    print("Generating metrics plot...")
    generate_metrics_plot(pubs_per_year, citations_per_year)


if __name__ == '__main__':
    main()
