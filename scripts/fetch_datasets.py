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
    """Fetch datasets from the Panorama Public JSON API.

    The MacCoss Lab datasets live in a public Panorama Public project, so
    selectRows.api is callable without authentication. If an API key happens
    to be available it's used (cheap, no harm), but it is not required.
    """
    import base64

    base_url = "https://panoramaweb.org/Panorama%20Public/query-selectRows.api"
    params = {
        "schemaName": "panoramapublic",
        "query.queryName": "experimentannotations",
        "query.columns": "Created,Title,Organism,Instrument,Authors,pxid,Container/Path",
        "query.Authors~contains": "MacCoss",
        "query.showRows": "all",
        "query.sort": "-Created",
        "query.containerFilterName": "AllFolders",  # include all subfolders
    }

    headers = {"User-Agent": "MacCossLab-Website-Script/1.0"}

    api_key = get_api_key()
    if api_key:
        auth_string = f"apikey:{api_key}"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()
        headers["Authorization"] = f"Basic {auth_bytes}"
        print("Using API key for authentication...")
    else:
        print("No API key found; querying public endpoint anonymously.")

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except ValueError as e:
        print(f"Failed to parse JSON response: {e}")
        return None

    rows = data.get("rows") or []
    if not rows:
        print(f"API returned {data.get('rowCount', 0)} rows")
        return None

    print(f"API returned {len(rows)} datasets")
    datasets = []
    for row in rows:
        created = row.get("Created", "")
        year = int(created[:4]) if created and len(created) >= 4 else 0
        pxid = row.get("pxid", "") or ""

        datasets.append({
            "date": created[:10] if created else "",
            "year": year,
            "title": row.get("Title", ""),
            "organism": row.get("Organism", "") or "",
            "instrument": row.get("Instrument", "") or "",
            "authors": row.get("Authors", "") or "",
            "pxid": pxid,
            "path": row.get("Container/Path", "") or "",
        })
    return datasets


def fetch_panorama_datasets():
    """Fetch datasets from Panorama Public via the JSON API.

    Raises RuntimeError if the API call fails or returns no rows, so the
    script exits non-zero rather than silently writing an empty datasets
    section to resources.md.
    """
    print("Fetching Panorama Public datasets...")

    datasets = fetch_panorama_datasets_api()
    if datasets:
        return datasets

    raise RuntimeError(
        "Panorama Public API returned no datasets. Refusing to overwrite "
        "resources.md. Check network access to panoramaweb.org and rerun."
    )


def generate_datasets_section(datasets):
    """Generate markdown for the datasets section, grouped by year."""
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

    current_date = datetime.now().strftime("%B %d, %Y")
    lines.append(f"*Last updated: {current_date} — {len(datasets)} datasets available*")
    lines.append("")

    years = {}
    for ds in datasets:
        year = ds.get("year", 0)
        years.setdefault(year, []).append(ds)

    for year in sorted(years.keys(), reverse=True):
        lines.append(f"### {year}")
        lines.append("")
        lines.append('<table class="invisible-table">')
        for ds in years[year]:
            title = ds.get("title", "Untitled")
            pxid = ds.get("pxid", "")
            path = ds.get("path", "")

            if path:
                url = f"https://panoramaweb.org{path}/project-begin.view"
                title_cell = f'<a href="{url}">{title}</a>'
            else:
                title_cell = title

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
    content = content[:datasets_start] + new_datasets_section + content[section_end:]
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

    try:
        datasets = fetch_panorama_datasets()
    except RuntimeError as e:
        print(f"Error: {e}")
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
