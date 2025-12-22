#!/usr/bin/env python3
"""
Fetch MacCoss Lab datasets from Panorama Public and update the Datasets tab.

This script fetches all public datasets associated with MacCoss Lab from
Panorama Public and updates the Datasets section of the resources page.

Data source:
- https://panoramaweb.org/project/Panorama%20Public/begin.view
  (filtered by authors containing "MacCoss")

Authentication:
- Set PANORAMA_API_KEY environment variable, or
- Create a .env file with PANORAMA_API_KEY=your-key, or
- The script will fall back to a curated dataset list
"""

import os
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def get_api_key():
    """Get Panorama API key from environment or .env file."""
    # Check environment variable first
    api_key = os.environ.get("PANORAMA_API_KEY")
    if api_key:
        return api_key

    # Check for .env file in project root
    script_dir = Path(__file__).parent
    env_file = script_dir.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("PANORAMA_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")

    # Check for credentials file in home directory
    creds_file = Path.home() / ".panorama_credentials"
    if creds_file.exists():
        for line in creds_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("api_key"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")

    return None


def fetch_panorama_datasets_api():
    """Fetch datasets from Panorama Public using the JSON API with authentication."""
    import base64

    api_key = get_api_key()

    if not api_key:
        print("No API key found. Set PANORAMA_API_KEY environment variable or create .env file.")
        print("Falling back to curated dataset list...")
        return None

    print("Using API key for authentication...")

    # Encode the API key for Basic auth (LabKey format: "apikey:KEY")
    auth_string = f"apikey:{api_key}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()

    # Use the JSON API endpoint
    base_url = "https://panoramaweb.org/Panorama%20Public/query-selectRows.api"
    params = {
        "schemaName": "panoramapublic",
        "query.queryName": "experimentannotations",
        "query.columns": "Created,Title,Organism,Instrument,Authors,pxid,Container/Path",
        "query.Authors~contains": "MacCoss",
        "query.showRows": "all",
        "query.sort": "-Created",
        "query.containerFilterName": "AllFolders",  # Critical: include all subfolders
    }

    headers = {
        "User-Agent": "MacCossLab-Website-Script/1.0",
        "Authorization": f"Basic {auth_bytes}",
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()

        if "rows" in data and len(data["rows"]) > 0:
            print(f"API returned {len(data['rows'])} datasets")
            datasets = []
            for row in data["rows"]:
                # Extract year from date
                created = row.get("Created", "")
                year = int(created[:4]) if created and len(created) >= 4 else 0

                # Clean up pxid (remove None)
                pxid = row.get("pxid", "") or ""

                dataset = {
                    "date": created[:10] if created else "",
                    "year": year,
                    "title": row.get("Title", ""),
                    "organism": row.get("Organism", "") or "",
                    "instrument": row.get("Instrument", "") or "",
                    "authors": row.get("Authors", "") or "",
                    "pxid": pxid,
                    "path": row.get("Container/Path", "") or "",
                }
                datasets.append(dataset)
            return datasets
        else:
            print(f"API returned {data.get('rowCount', 0)} rows")
            return None

    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except ValueError as e:
        print(f"Failed to parse JSON response: {e}")
        return None


def fetch_panorama_datasets():
    """Fetch datasets from Panorama Public search page."""
    print("Fetching Panorama Public datasets...")

    # Try API with authentication first
    datasets = fetch_panorama_datasets_api()
    if datasets:
        return datasets

    # Fallback: Try unauthenticated request (usually returns empty)
    base_url = "https://panoramaweb.org/Panorama%20Public/query-executeQuery.view"
    params = {
        "schemaName": "panoramapublic",
        "query.queryName": "experimentannotations",
        "query.Authors~contains": "MacCoss",
        "query.showRows": "ALL",
        "query.sort": "-Created",
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=60)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching Panorama Public: {e}")
        return get_hardcoded_datasets()

    soup = BeautifulSoup(response.text, "html.parser")

    # Look for data in the table
    datasets = []
    table = soup.find("table", class_="labkey-data-region")

    if not table:
        print("No data table found, using curated list...")
        return get_hardcoded_datasets()

    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 5:
            dataset = parse_table_row(cells)
            if dataset:
                datasets.append(dataset)

    print(f"Found {len(datasets)} datasets from direct query")

    if not datasets:
        print("No datasets from API, using curated list...")
        return get_hardcoded_datasets()

    return datasets


def fetch_from_search_panel():
    """Fetch datasets from the search panel page by parsing HTML."""
    print("Fetching from search panel...")

    # The search panel URL with MacCoss filter
    url = (
        "https://panoramaweb.org/project/Panorama%20Public/begin.view"
        "#searchTab:expSearchPanel"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching search panel: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # The page uses JavaScript to load data, so we may not find it in the HTML
    # Let's try to find any experiment data that might be pre-rendered
    datasets = []

    # Look for labkey data regions
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 3:
                # Check if this looks like an experiment row
                text = row.get_text()
                if "MacCoss" in text or "PXD" in text:
                    dataset = parse_table_row(cells)
                    if dataset:
                        datasets.append(dataset)

    if not datasets:
        print("Could not parse datasets from search panel")
        print("Using fallback: hardcoded recent datasets list")
        return get_hardcoded_datasets()

    return datasets


def parse_table_row(cells):
    """Parse a table row into a dataset dictionary."""
    try:
        # Try to extract: Date, Title, Organism, Instrument, Authors, PX ID
        dataset = {
            "date": "",
            "title": "",
            "organism": "",
            "instrument": "",
            "authors": "",
            "pxid": "",
            "url": "",
        }

        # The structure varies, try to extract what we can
        for i, cell in enumerate(cells):
            text = cell.get_text(strip=True)

            # Check for date pattern (YYYY-MM-DD)
            if re.match(r"\d{4}-\d{2}-\d{2}", text):
                dataset["date"] = text
                continue

            # Check for PXD ID
            if text.startswith("PXD"):
                dataset["pxid"] = text
                continue

            # Check for URL links
            link = cell.find("a")
            if link and link.get("href"):
                href = link.get("href")
                if "panoramaweb.org" in href or href.startswith("/"):
                    if not dataset["url"]:
                        dataset["url"] = href
                        dataset["title"] = link.get_text(strip=True)

            # Try to identify by content
            if "Homo sapiens" in text or "Mus musculus" in text:
                dataset["organism"] = text
            elif "Orbitrap" in text or "Q Exactive" in text or "TSQ" in text:
                dataset["instrument"] = text
            elif "MacCoss" in text:
                dataset["authors"] = text

        # Only return if we have at least a title
        if dataset["title"]:
            return dataset

    except Exception as e:
        print(f"Error parsing row: {e}")

    return None


def get_hardcoded_datasets():
    """
    Return a curated list of MacCoss Lab datasets.

    Since the Panorama Public search page uses JavaScript to load data,
    we maintain a curated list of datasets that is updated periodically.
    This list is organized by year and research category.
    """
    datasets = [
        # 2025 Datasets
        {
            "year": 2025,
            "title": "Evaluation of a modified Orbitrap Astral Zoom prototype for quantitative proteomics",
            "pxid": "PXD064536",
            "organism": "Homo sapiens, Gallus gallus",
            "instrument": "Orbitrap Astral, Orbitrap Astral Zoom, Stellar",
            "url": "https://panoramaweb.org/maccoss/astral-zoom/project-begin.view",
            "category": "Instrumentation",
        },
        {
            "year": 2025,
            "title": "DIA Analysis of Microvasculature in Alzheimer's Disease",
            "pxid": "",
            "organism": "Homo sapiens",
            "instrument": "Orbitrap Exploris 480, Orbitrap Fusion Lumos",
            "url": "https://panoramaweb.org/maccoss/microvasculature-ad/project-begin.view",
            "category": "Clinical Applications",
        },
        {
            "year": 2025,
            "title": "Tutorials on How to Use PRM Conductor, a Skyline External Tool",
            "pxid": "",
            "organism": "",
            "instrument": "",
            "url": "https://panoramaweb.org/maccoss/prm-conductor/project-begin.view",
            "category": "Software & Methods",
        },
        {
            "year": 2025,
            "title": "Development of highly multiplex targeted proteomics assays in biofluids",
            "pxid": "PXD065471",
            "organism": "Homo sapiens, Gallus gallus",
            "instrument": "Orbitrap Exploris 480, Stellar",
            "url": "https://panoramaweb.org/maccoss/multiplex-biofluids/project-begin.view",
            "category": "Method Development",
        },
        {
            "year": 2025,
            "title": "DIA to inform Triple Quad Assay development",
            "pxid": "PXD059611",
            "organism": "Homo sapiens",
            "instrument": "TSQ Altis, Q Exactive HF",
            "url": "https://panoramaweb.org/maccoss/dia-tq-assay/project-begin.view",
            "category": "Method Development",
        },
        # 2024 Datasets
        {
            "year": 2024,
            "title": "Carafe enables high quality in silico spectral library generation for DIA proteomics",
            "pxid": "PXD056793",
            "organism": "Homo sapiens, Saccharomyces cerevisiae",
            "instrument": "Orbitrap Fusion Lumos, Orbitrap Exploris 480, Orbitrap Astral",
            "url": "https://panoramaweb.org/maccoss/carafe/project-begin.view",
            "category": "Computational Methods",
        },
        {
            "year": 2024,
            "title": "A framework for quality control in quantitative proteomics",
            "pxid": "PXD051318",
            "organism": "Homo sapiens, Mus musculus, Saccharomyces cerevisiae",
            "instrument": "Orbitrap Eclipse, Orbitrap Fusion Lumos",
            "url": "https://panoramaweb.org/maccoss/qc-framework/project-begin.view",
            "category": "Method Development",
        },
        {
            "year": 2024,
            "title": "Detection and Quantification of Drug-Protein Adducts in Human Liver",
            "pxid": "PXD054246",
            "organism": "Homo sapiens",
            "instrument": "Orbitrap Exploris 480, Orbitrap Eclipse",
            "url": "https://panoramaweb.org/maccoss/drug-adducts/project-begin.view",
            "category": "Clinical Applications",
        },
        {
            "year": 2024,
            "title": "A transformer model for de novo sequencing of DIA mass spectrometry data",
            "pxid": "PXD053291",
            "organism": "Homo sapiens, Mus musculus",
            "instrument": "Orbitrap Astral, Q Exactive HF-X",
            "url": "https://panoramaweb.org/maccoss/transformer-dia/project-begin.view",
            "category": "Computational Methods",
        },
        {
            "year": 2024,
            "title": "Characterization of Stellar MS",
            "pxid": "PXD052734",
            "organism": "Homo sapiens, Gallus gallus, Escherichia coli",
            "instrument": "Stellar",
            "url": "https://panoramaweb.org/maccoss/stellar/project-begin.view",
            "category": "Instrumentation",
        },
        {
            "year": 2024,
            "title": "AD-BXD Mouse PreFrontal Cortex Proteomics",
            "pxid": "PXD045403",
            "organism": "Mus musculus",
            "instrument": "Orbitrap Fusion, Orbitrap Fusion Lumos",
            "url": "https://panoramaweb.org/maccoss/adbxd-pfc/project-begin.view",
            "category": "Disease Research",
        },
        {
            "year": 2024,
            "title": "Mouse Skeletal Muscle Sarcopenia",
            "pxid": "PXD048723",
            "organism": "Mus musculus",
            "instrument": "Orbitrap Eclipse",
            "url": "https://panoramaweb.org/maccoss/sarcopenia/project-begin.view",
            "category": "Disease Research",
        },
        {
            "year": 2024,
            "title": "Evaluation of Linearity, Lower Limit of Measurement Interval and Imprecision",
            "pxid": "PXD041410",
            "organism": "Homo sapiens",
            "instrument": "Xevo TQ-S",
            "url": "https://panoramaweb.org/maccoss/linearity-eval/project-begin.view",
            "category": "Method Validation",
        },
        # 2023 Datasets
        {
            "year": 2023,
            "title": "AD-BXD Mouse Hippocampus Proteomics",
            "pxid": "PXD045425",
            "organism": "Mus musculus",
            "instrument": "Orbitrap Fusion Lumos",
            "url": "https://panoramaweb.org/maccoss/adbxd-hippocampus/project-begin.view",
            "category": "Disease Research",
        },
        {
            "year": 2023,
            "title": "Comparing peptide identifications by FAIMS versus quadrupole gas phase fractionation",
            "pxid": "PXD043458",
            "organism": "Homo sapiens",
            "instrument": "Orbitrap Eclipse",
            "url": "https://panoramaweb.org/maccoss/faims-gpf/project-begin.view",
            "category": "Method Development",
        },
        {
            "year": 2023,
            "title": "Mag-Net: Rapid enrichment of membrane-bound particles for plasma proteomics",
            "pxid": "PXD042947",
            "organism": "Homo sapiens",
            "instrument": "Orbitrap Eclipse",
            "url": "https://panoramaweb.org/maccoss/mag-net/project-begin.view",
            "category": "Method Development",
        },
        {
            "year": 2023,
            "title": "Evaluating the Performance of the Astral Mass Analyzer for DIA Proteomics",
            "pxid": "PXD042704",
            "organism": "Homo sapiens",
            "instrument": "Orbitrap Fusion Lumos, Orbitrap Astral",
            "url": "https://panoramaweb.org/maccoss/astral-eval/project-begin.view",
            "category": "Instrumentation",
        },
        {
            "year": 2023,
            "title": "Metrologically traceable quantification of apolipoprotein E isoforms in CSF",
            "pxid": "PXD038803",
            "organism": "Homo sapiens",
            "instrument": "Xevo TQ-S",
            "url": "https://panoramaweb.org/maccoss/apoe-csf/project-begin.view",
            "category": "Clinical Applications",
        },
        # 2022 Datasets
        {
            "year": 2022,
            "title": "Dynamic DIA Mass Spectrometry with Real-Time Retrospective Alignment",
            "pxid": "PXD038508",
            "organism": "Homo sapiens",
            "instrument": "Orbitrap Fusion Lumos",
            "url": "https://panoramaweb.org/maccoss/dynamic-dia/project-begin.view",
            "category": "Method Development",
        },
        {
            "year": 2022,
            "title": "A Peptide-Centric Quantitative Proteomics Dataset for Alzheimer's Disease",
            "pxid": "PXD034525",
            "organism": "Homo sapiens",
            "instrument": "Orbitrap Fusion Lumos",
            "url": "https://panoramaweb.org/maccoss/ad-peptide-quant/project-begin.view",
            "category": "Disease Research",
        },
        {
            "year": 2022,
            "title": "Quantitative XL-MS Analysis of HHARI",
            "pxid": "PXD030871",
            "organism": "Homo sapiens",
            "instrument": "Q Exactive",
            "url": "https://panoramaweb.org/maccoss/xlms-hhari/project-begin.view",
            "category": "Method Development",
        },
        # 2021 Datasets
        {
            "year": 2021,
            "title": "Skyline Batch: An Intuitive User Interface for Batch Processing",
            "pxid": "PXD029665",
            "organism": "Saccharomyces cerevisiae",
            "instrument": "TripleTOF 5600",
            "url": "https://panoramaweb.org/maccoss/skyline-batch/project-begin.view",
            "category": "Software & Methods",
        },
        {
            "year": 2021,
            "title": "Grizzly Bear Serum DIA Proteomics",
            "pxid": "PXD023555",
            "organism": "Ursus arctos horribilis",
            "instrument": "Q Exactive HF",
            "url": "https://panoramaweb.org/maccoss/grizzly-bear/project-begin.view",
            "category": "Wildlife Proteomics",
        },
        {
            "year": 2021,
            "title": "Phospho-proteomic Profiling of Chemical Perturbations (LINCS)",
            "pxid": "PXD017458",
            "organism": "Homo sapiens",
            "instrument": "Q Exactive HF",
            "url": "https://panoramaweb.org/maccoss/lincs-phospho/project-begin.view",
            "category": "Large-Scale Studies",
        },
        {
            "year": 2021,
            "title": "Alzheimer's Disease Isomerization",
            "pxid": "PXD025668",
            "organism": "Homo sapiens",
            "instrument": "Orbitrap Fusion Lumos",
            "url": "https://panoramaweb.org/maccoss/ad-isomerization/project-begin.view",
            "category": "Disease Research",
        },
        {
            "year": 2021,
            "title": "Age-Related Disruption of the Proteome and Acetylome in Mouse Hearts",
            "pxid": "PXD027458",
            "organism": "Mus musculus",
            "instrument": "Q Exactive HF-X",
            "url": "https://panoramaweb.org/maccoss/heart-aging/project-begin.view",
            "category": "Aging Research",
        },
        # 2020 and earlier (selected highlights)
        {
            "year": 2020,
            "title": "Highly Multiplex Targeted Proteomics Enabled by Real-Time Alignment",
            "pxid": "PXD018675",
            "organism": "Homo sapiens",
            "instrument": "Orbitrap Fusion Lumos",
            "url": "https://panoramaweb.org/maccoss/realtime-align/project-begin.view",
            "category": "Method Development",
        },
        {
            "year": 2019,
            "title": "Matrix-matched calibration curves for quantitative proteomics",
            "pxid": "PXD014815",
            "organism": "Saccharomyces cerevisiae, Homo sapiens",
            "instrument": "Q Exactive HF, Orbitrap Fusion Lumos, TSQ Quantiva",
            "url": "https://panoramaweb.org/maccoss/matrix-matched/project-begin.view",
            "category": "Method Validation",
        },
        {
            "year": 2019,
            "title": "Skyline for Small Molecules: A Unifying Software Package for Metabolomics",
            "pxid": "",
            "organism": "Homo sapiens, Mus musculus",
            "instrument": "Xevo TQ-S, Triple Quad 5500, Synapt G2 HDMS",
            "url": "https://panoramaweb.org/maccoss/skyline-small-molecules/project-begin.view",
            "category": "Software & Methods",
        },
        {
            "year": 2018,
            "title": "Using Skyline for LC-IMS-MS Data Analysis",
            "pxid": "PXD010650",
            "organism": "Bos taurus, Saccharomyces cerevisiae",
            "instrument": "6560 Q-TOF LC/MS",
            "url": "https://panoramaweb.org/maccoss/skyline-ims/project-begin.view",
            "category": "Software & Methods",
        },
        {
            "year": 2018,
            "title": "System Suitability Protocol for LC-MRM-MS",
            "pxid": "PXD010535",
            "organism": "Bos taurus",
            "instrument": "Multiple platforms",
            "url": "https://panoramaweb.org/maccoss/system-suitability/project-begin.view",
            "category": "Method Validation",
        },
        {
            "year": 2015,
            "title": "Large-scale inter-laboratory study for cancer biomarker assays",
            "pxid": "",
            "organism": "Homo sapiens",
            "instrument": "Multiple platforms",
            "url": "https://panoramaweb.org/maccoss/cptac-interlaboratory/project-begin.view",
            "category": "Large-Scale Studies",
        },
    ]

    print(f"Using {len(datasets)} curated datasets")
    return datasets


def generate_datasets_section(datasets):
    """Generate markdown content for the datasets section.

    Supports both API data (year-based organization) and hardcoded data (category-based).
    API data doesn't have categories, so we organize by year instead.
    Uses invisible tables with dataset title on left, PXD on right.
    """
    lines = []

    lines.append("## Public Datasets on [Panorama Public](http://panoramaweb.org/public.url)")
    lines.append("")
    lines.append("**We have made available a number of mass spectrometry datasets on Panorama Public**")
    lines.append("")
    lines.append("**[Browse all MacCoss Lab datasets on Panorama Public →]"
                 "(https://panoramaweb.org/project/Panorama%20Public/begin.view"
                 "#searchTab:expSearchPanel?Targeted%20MS%20Experiment%20List."
                 "authors~containsoneof=MacCoss&)**")
    lines.append("")

    # Get current date for the update timestamp
    current_date = datetime.now().strftime("%B %d, %Y")
    lines.append(f"*Last updated: {current_date} — {len(datasets)} datasets available*")
    lines.append("")

    # Check if we have category data (hardcoded) or just year data (API)
    has_categories = any(ds.get("category") for ds in datasets)

    if has_categories:
        # Group datasets by category (hardcoded fallback data)
        categories = {}
        for ds in datasets:
            cat = ds.get("category", "Other")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(ds)

        # Define category order and descriptions
        category_order = [
            ("Instrumentation", "Mass spectrometer characterization and benchmarking"),
            ("Method Development", "Novel proteomics methods and workflows"),
            ("Computational Methods", "AI, machine learning, and data analysis approaches"),
            ("Clinical Applications", "Biomarker discovery and clinical proteomics"),
            ("Disease Research", "Alzheimer's, aging, and disease proteomics"),
            ("Method Validation", "Analytical validation and quality control"),
            ("Software & Methods", "Skyline and software workflow datasets"),
            ("Large-Scale Studies", "Multi-site and community resource datasets"),
            ("Aging Research", "Age-related proteome studies"),
            ("Wildlife Proteomics", "Non-model organism studies"),
        ]

        for cat_name, cat_desc in category_order:
            if cat_name not in categories:
                continue

            cat_datasets = sorted(categories[cat_name], key=lambda x: -x.get("year", 0))

            lines.append(f"### {cat_name}")
            lines.append(f"*{cat_desc}*")
            lines.append("")

            # Invisible table
            lines.append('<table class="invisible-table">')
            for ds in cat_datasets:
                title = ds.get("title", "Untitled")
                pxid = ds.get("pxid", "")
                year = ds.get("year", "")
                url = ds.get("url", "")

                # Build title with optional year
                if url:
                    title_cell = f'<a href="{url}">{title}</a>'
                else:
                    title_cell = title
                if year:
                    title_cell += f" ({year})"

                # Build PXD link
                if pxid:
                    pxd_cell = (f'<a href="http://proteomecentral.proteomexchange.org/'
                                f'cgi/GetDataset?ID={pxid}">{pxid}</a>')
                else:
                    pxd_cell = ""

                lines.append(f"<tr><td>{title_cell}</td><td>{pxd_cell}</td></tr>")

            lines.append("</table>")
            lines.append("")
    else:
        # Group datasets by year (API data)
        years = {}
        for ds in datasets:
            year = ds.get("year", 0)
            if year not in years:
                years[year] = []
            years[year].append(ds)

        # Sort years in descending order
        for year in sorted(years.keys(), reverse=True):
            year_datasets = years[year]

            lines.append(f"### {year}")
            lines.append("")

            # Invisible table
            lines.append('<table class="invisible-table">')
            for ds in year_datasets:
                title = ds.get("title", "Untitled")
                pxid = ds.get("pxid", "")
                path = ds.get("path", "")

                # Build Panorama URL from path
                if path:
                    url = f"https://panoramaweb.org{path}/project-begin.view"
                    title_cell = f'<a href="{url}">{title}</a>'
                else:
                    title_cell = title

                # Build PXD link
                if pxid:
                    pxd_cell = (f'<a href="http://proteomecentral.proteomexchange.org/'
                                f'cgi/GetDataset?ID={pxid}">{pxid}</a>')
                else:
                    pxd_cell = ""

                lines.append(f"<tr><td>{title_cell}</td><td>{pxd_cell}</td></tr>")

            lines.append("</table>")
            lines.append("")

    lines.append("*All datasets include processed results as Skyline documents and raw datafiles. "
                 "Many datasets are paired with published manuscripts.*")
    lines.append("")

    return "\n".join(lines)


def update_resources_page(datasets_content):
    """Update the resources.md file with the new datasets content."""
    # Determine the correct path
    script_dir = Path(__file__).parent
    resources_path = script_dir.parent / "pages" / "resources.md"

    if not resources_path.exists():
        print(f"Error: {resources_path} not found")
        return False

    print(f"Reading {resources_path}...")
    content = resources_path.read_text()

    # Find the datasets section
    # Look for: <div id="datasets" class="tab-content">
    datasets_pattern = r'<div id="datasets" class="tab-content">'
    match = re.search(datasets_pattern, content)

    if not match:
        print("Error: Could not find Datasets section marker.")
        return False

    datasets_start = match.start()
    print(f"Found datasets section at position {datasets_start}")

    # Find the next tab section (Educational Materials)
    next_section_pattern = r'\s*<div id="educational" class="tab-content">'
    next_match = re.search(next_section_pattern, content[datasets_start + 10:])

    if next_match:
        section_end = datasets_start + 10 + next_match.start()
    else:
        print("Error: Could not find end of Datasets section.")
        return False

    print(f"Datasets section ends at position {section_end}")

    # Build the new datasets section
    new_datasets_section = f'''<div id="datasets" class="tab-content">
    <div markdown="1">

{datasets_content}

</div>
  </div>

'''

    # Replace the section
    content = content[:datasets_start] + "  " + new_datasets_section + content[section_end:]
    print("Updated Datasets section.")

    # Write the updated content
    resources_path.write_text(content)
    print(f"Saved updated {resources_path}")

    return True


def main():
    """Main function to fetch datasets and update the resources page."""
    print("=" * 60)
    print("Fetching MacCoss Lab Datasets from Panorama Public")
    print("=" * 60)

    # Try to fetch datasets (will fall back to hardcoded list if needed)
    datasets = fetch_panorama_datasets()

    if not datasets:
        print("Error: No datasets found")
        return 1

    print(f"\nTotal datasets: {len(datasets)}")

    # Generate content
    datasets_content = generate_datasets_section(datasets)

    # Update the resources page
    if update_resources_page(datasets_content):
        print("\n" + "=" * 60)
        print("Successfully updated Datasets section!")
        print("=" * 60)
        return 0
    else:
        print("\nError: Failed to update resources page")
        return 1


if __name__ == "__main__":
    exit(main())
