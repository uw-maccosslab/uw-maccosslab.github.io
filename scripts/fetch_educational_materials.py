#!/usr/bin/env python3
"""
Fetch educational materials and update the Educational Materials section.

This script scrapes:
- Skyline tutorials from https://skyline.ms/home/software/Skyline/wiki-page.view?name=tutorials
- Skyline documentation from https://skyline.ms/home/software/Skyline/wiki-page.view?name=documentation
- UWPR LC-MS Tips and Tricks from https://proteomicsresource.washington.edu/protocols05/
- UWPR Data Analysis Tools from https://proteomicsresource.washington.edu/protocols06/

And updates the Educational Materials tab in pages/resources.md.
"""

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

# URLs to scrape
TUTORIALS_URL = "https://skyline.ms/home/software/Skyline/wiki-page.view?name=tutorials"
DOCUMENTATION_URL = (
    "https://skyline.ms/home/software/Skyline/wiki-page.view?name=documentation"
)
UWPR_TIPS_URL = "https://proteomicsresource.washington.edu/protocols05/"
UWPR_TOOLS_URL = "https://proteomicsresource.washington.edu/protocols06/"

# Headers to avoid being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def fetch_skyline_tutorials():
    """Fetch tutorials from the Skyline tutorials page.

    Note: We use a curated list because the Skyline tutorials page has complex
    HTML with navigation sidebars and translation links that make scraping unreliable.
    The tutorials list is updated manually when new tutorials are added.
    """
    print("Fetching Skyline tutorials...")

    # Use curated list - dynamic scraping picks up duplicates from sidebar/navigation
    return get_fallback_tutorials()


def category_names_lower():
    """Return lowercase category names for filtering."""
    return [
        "introductory",
        "introduction to full-scan acquisition data",
        "full-scan acquisition data",
        "small molecules",
        "reports",
        "advanced topics",
    ]

    return tutorials


def get_fallback_tutorials():
    """Return fallback hardcoded tutorials list in case scraping fails."""
    tutorials = {
        "Introductory": [
            {"title": "Targeted Method Editing", "url": "https://skyline.ms/tutorial_method_edit.url", "pages": "26"},
            {"title": "Targeted Method Refinement", "url": "https://skyline.ms/tutorial_method_refine.url", "pages": "28"},
            {"title": "Grouped Study Data Processing", "url": "https://skyline.ms/tutorial_grouped.url", "pages": "70"},
            {"title": "Existing & Quantitative Experiments", "url": "https://skyline.ms/tutorial_existing_quant.url", "pages": "43"},
        ],
        "Introduction to Full-Scan Acquisition Data": [
            {"title": "Comparing PRM, DIA, and DDA", "url": "https://skyline.ms/tutorial_comp_acq.url", "pages": "38"},
            {"title": "PRM With an Orbitrap", "url": "https://skyline.ms/tutorial_prm_orbi.url", "pages": "44"},
            {"title": "Basic Data Independent Acquisition", "url": "https://skyline.ms/tutorial_dia.url", "pages": "40"},
        ],
        "Full-Scan Acquisition Data": [
            {"title": "MS1 Full-Scan Filtering", "url": "https://skyline.ms/tutorial_ms1_filtering.url", "pages": "41"},
            {"title": "DDA Search for MS1 Filtering", "url": "https://skyline.ms/tutorial_dda_search.url", "pages": "19"},
            {"title": "Parallel Reaction Monitoring (PRM)", "url": "https://skyline.ms/tutorial_prm.url", "pages": "40"},
            {"title": "Analysis of DIA/SWATH Data", "url": "https://skyline.ms/tutorial_dia_swath.url", "pages": "32"},
            {"title": "Analysis of diaPASEF Data", "url": "https://skyline.ms/tutorial_dia_pasef.url", "pages": "36"},
            {"title": "Library-Free DIA/SWATH", "url": "https://skyline.ms/tutorial_dia_umpire_ttof.url", "pages": "26"},
            {"title": "Peak Boundary Imputation for DIA", "url": "https://skyline.ms/tutorial_peak_impute_dia.url", "pages": "16"},
        ],
        "Small Molecules": [
            {"title": "Small Molecule Targets", "url": "https://skyline.ms/tutorial_small_molecule.url", "pages": "10"},
            {"title": "Small Molecule Method Development", "url": "https://skyline.ms/tutorial_small_method_ce.url", "pages": "37"},
            {"title": "Small Mol. Multidimension Spec. Lib.", "url": "https://skyline.ms/tutorial_small_ims.url", "pages": "23"},
            {"title": "Small Molecule Quantification", "url": "https://skyline.ms/tutorial_small_quant.url", "pages": "27"},
            {"title": "Hi-Res Metabolomics", "url": "https://skyline.ms/tutorial_hi_res_metabolomics.url", "pages": "17"},
        ],
        "Reports": [
            {"title": "Custom Reports", "url": "https://skyline.ms/tutorial_custom_reports.url", "pages": "33"},
            {"title": "Live Reports", "url": "https://skyline.ms/tutorial_live_reports.url", "pages": "48"},
        ],
        "Advanced Topics": [
            {"title": "Absolute Quantification", "url": "https://skyline.ms/tutorial_absolute_quant.url", "pages": "19"},
            {"title": "Advanced Peak Picking Models", "url": "https://skyline.ms/tutorial_peak_picking.url", "pages": "28"},
            {"title": "iRT Retention Time Prediction", "url": "https://skyline.ms/tutorial_irt.url", "pages": "36"},
            {"title": "Collision Energy Optimization", "url": "https://skyline.ms/tutorial_optimize_ce.url", "pages": "12"},
            {"title": "Ion Mobility Spectrum Filtering", "url": "https://skyline.ms/tutorial_ims.url", "pages": "26"},
            {"title": "Spectral Library Explorer", "url": "https://skyline.ms/tutorial_library_explorer.url", "pages": "22"},
            {"title": "Audit Logging", "url": "https://skyline.ms/tutorial_audit_log.url", "pages": "23"},
        ],
    }

    total = sum(len(t) for t in tutorials.values())
    print(f"Using {total} fallback tutorials across {len(tutorials)} categories")
    return tutorials


def fetch_skyline_documentation():
    """Fetch documentation from the Skyline documentation page."""
    print("Fetching Skyline documentation...")

    try:
        response = requests.get(DOCUMENTATION_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching documentation: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    docs = []

    # Find documentation links - they're usually in list items or paragraphs
    for element in soup.find_all(["li", "p"]):
        text = element.get_text(strip=True)

        # Look for documentation items (bullet points starting with specific keywords)
        if text.startswith("•") or "Skyline" in text:
            links = element.find_all("a", href=True)
            for link in links:
                href = link.get("href", "")
                title = link.get_text(strip=True)

                # Skip navigation links
                if not title or title in ["Sign In", "MacCoss Lab Software"]:
                    continue

                # Look for documentation-related links
                if "doc" in href.lower() or "pdf" in href.lower():
                    if href.startswith("/"):
                        href = f"https://skyline.ms{href}"

                    # Extract description from surrounding text
                    description = text.replace("•", "").strip()
                    description = re.sub(r"\s+", " ", description)

                    docs.append({"title": title, "url": href, "description": description})

    # Also look for specific documentation patterns
    for link in soup.find_all("a", href=True):
        text = link.get_text(strip=True)
        href = link.get("href", "")

        # Common documentation patterns
        doc_patterns = [
            "Custom Reports",
            "Command-Line",
            "Keyboard Shortcuts",
            "External Tools",
            "Interactive Tools",
        ]

        for pattern in doc_patterns:
            if pattern.lower() in text.lower():
                if href.startswith("/"):
                    href = f"https://skyline.ms{href}"

                # Check if not already added
                if not any(d["title"] == text for d in docs):
                    docs.append({"title": text, "url": href, "description": ""})
                break

    print(f"Found {len(docs)} documentation items")
    return docs


def fetch_uwpr_tips():
    """Fetch LC-MS tips and tricks from UWPR."""
    print("Fetching UWPR LC-MS Tips and Tricks...")

    try:
        response = requests.get(UWPR_TIPS_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching UWPR tips: {e}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")

    tips = {
        "Column Preparation": [],
        "HPLC Setup": [],
        "Mass Spec Protocols": [],
        "Hardware": [],
        "Miscellaneous": [],
    }

    current_section = None

    # Find all headers and links
    for element in soup.find_all(["h2", "a"]):
        if element.name == "h2":
            section_text = element.get_text(strip=True).lower()
            if "column" in section_text:
                current_section = "Column Preparation"
            elif "hplc" in section_text or "setup" in section_text:
                current_section = "HPLC Setup"
            elif "mass spec" in section_text and "protocol" in section_text:
                current_section = "Mass Spec Protocols"
            elif "hardware" in section_text:
                current_section = "Hardware"
            elif "miscellaneous" in section_text:
                current_section = "Miscellaneous"

        elif element.name == "a" and current_section:
            href = element.get("href", "")
            text = element.get_text(strip=True)

            # Skip empty or navigation links
            if not text or text.lower() in ["back to top", "go to page"]:
                continue

            # Make URL absolute
            if href.startswith("/"):
                href = f"https://proteomicsresource.washington.edu{href}"
            elif not href.startswith("http") and href:
                href = f"https://proteomicsresource.washington.edu/protocols05/{href}"

            if text and href and len(text) > 3:
                tips[current_section].append({"title": text, "url": href})

    # Count total tips
    total = sum(len(t) for t in tips.values())
    print(f"Found {total} tips across {len(tips)} categories")

    return tips


def fetch_uwpr_tools():
    """Fetch data analysis tools from UWPR."""
    print("Fetching UWPR Data Analysis Tools...")

    try:
        response = requests.get(UWPR_TOOLS_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching UWPR tools: {e}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")

    tools = {
        "Online Calculators": [],
        "Database Search Tools": [],
        "Software Tools": [],
        "Cross-Linking": [],
        "Miscellaneous": [],
    }

    current_section = None

    # Find all headers and links
    for element in soup.find_all(["h3", "a"]):
        if element.name == "h3":
            section_text = element.get_text(strip=True).lower()
            if "calculator" in section_text or "online" in section_text:
                current_section = "Online Calculators"
            elif "database search tool" in section_text:
                current_section = "Database Search Tools"
            elif "software" in section_text:
                current_section = "Software Tools"
            elif "crosslink" in section_text or "cross-link" in section_text:
                current_section = "Cross-Linking"
            elif "miscellaneous" in section_text:
                current_section = "Miscellaneous"

        elif element.name == "a" and current_section:
            href = element.get("href", "")
            text = element.get_text(strip=True)

            # Skip empty or navigation links
            if not text or len(text) < 3:
                continue

            # Skip reference links like "link1", "paper1"
            if re.match(r"^(link|paper)\d+$", text.lower()):
                continue

            # Make URL absolute
            if href.startswith("/"):
                href = f"https://proteomicsresource.washington.edu{href}"
            elif not href.startswith("http") and href:
                href = f"https://proteomicsresource.washington.edu/protocols06/{href}"

            if text and href:
                tools[current_section].append({"title": text, "url": href})

    # Count total tools
    total = sum(len(t) for t in tools.values())
    print(f"Found {total} tools across {len(tools)} categories")

    return tools


def generate_educational_section(tutorials, documentation, uwpr_tips, uwpr_tools):
    """Generate the Educational Materials section content."""
    lines = []

    # Count total tutorials
    total_tutorials = sum(len(t) for t in tutorials.values())

    # Header with last updated timestamp
    lines.append("## Educational Materials")
    lines.append("")
    current_date = datetime.now().strftime("%B %d, %Y")
    lines.append(f"*Last updated: {current_date} — {total_tutorials} Skyline tutorials available*")
    lines.append("")

    # UWPR Resources - quick links
    lines.append("### UWPR Mass Spectrometry Resources")
    lines.append("")
    lines.append(
        "- **[UWPR LC-MS Tips and Tricks](https://proteomicsresource.washington.edu/protocols05/)** — "
        "Protocols, tips, and resources for LC-MS analyses. *Definitely bookmark this page.*"
    )
    lines.append(
        "- **[UWPR Data Analysis Tools](https://proteomicsresource.washington.edu/protocols06/)** — "
        "Online calculators, database search tools, and computational resources."
    )
    lines.append("")

    # UWPR Online Calculators (highlight the most useful)
    if uwpr_tools.get("Online Calculators"):
        lines.append("#### UWPR Online Calculators")
        for tool in uwpr_tools["Online Calculators"][:8]:  # Limit to 8 items
            lines.append(f"- [{tool['title']}]({tool['url']})")
        lines.append("")

    # Skyline Tutorials
    lines.append("### Skyline Tutorials")
    lines.append(
        "*Hands-on tutorials with real data and step-by-step instructions*"
    )
    lines.append("")

    tutorial_order = [
        "Introductory",
        "Introduction to Full-Scan Acquisition Data",
        "Full-Scan Acquisition Data",
        "Small Molecules",
        "Reports",
        "Advanced Topics",
    ]

    for section in tutorial_order:
        if tutorials.get(section):
            lines.append(f"#### {section}")
            for tut in tutorials[section]:
                pages_info = f" ({tut['pages']} pages)" if tut.get("pages") else ""
                lines.append(f"- **[{tut['title']}]({tut['url']})**{pages_info}")
            lines.append("")

    lines.append(
        "[**View all tutorials**](https://skyline.ms/wiki/home/software/Skyline/page.view?name=tutorials)"
    )
    lines.append("")

    # Skyline Documentation
    lines.append("### Skyline Documentation")
    lines.append(
        "*Advanced reference documentation and developer resources*"
    )
    lines.append("")

    # Add key documentation items
    doc_items = [
        {
            "title": "Skyline Custom Reports",
            "url": "https://skyline.ms/wiki/home/software/Skyline/page.view?name=custom_reports",
            "desc": "Learn about the vast array of values you can show in the Document Grid or export",
        },
        {
            "title": "Skyline Command-Line Interface",
            "url": "https://skyline.ms/wiki/home/software/Skyline/page.view?name=SkylineCmd",
            "desc": "Use SkylineRunner.exe and SkylineCmd.exe for command-line operations",
        },
        {
            "title": "Skyline Keyboard Shortcuts",
            "url": "https://skyline.ms/wiki/home/software/Skyline/page.view?name=keyboard_shortcuts",
            "desc": "Quick access to commands without leaving the keyboard",
        },
        {
            "title": "External Tools Documentation",
            "url": "https://skyline.ms/labkey/_webdav/home/software/Skyline/@files/docs/Skyline%20External%20Tools-2_1.pdf",
            "desc": "Integrate statistical and bioinformatics tools with Skyline",
        },
        {
            "title": "Interactive Tools Documentation",
            "url": "https://skyline.ms/labkey/_webdav/home/software/Skyline/@files/docs/Skyline%20Interactive%20Tool%20Support-3_1.pdf",
            "desc": "Develop .NET tools that interact with Skyline in real-time",
        },
    ]

    for doc in doc_items:
        lines.append(f"- **[{doc['title']}]({doc['url']})** — {doc['desc']}")
    lines.append("")

    lines.append(
        "[**View all documentation**](https://skyline.ms/wiki/home/software/Skyline/page.view?name=documentation)"
    )
    lines.append("")

    # Skyline Videos
    lines.append("### Skyline Videos")
    lines.append("*Quick instructional videos for getting started*")
    lines.append("")

    video_items = [
        {
            "title": "Video Demo 1: Creating SRM/MRM Methods",
            "url": "https://skyline.ms/labkey/wiki/home/software/Skyline/page.view?name=video_0-2",
            "time": "28 minutes",
        },
        {
            "title": "Video Demo 2: Results Analysis and Method Refinement",
            "url": "https://skyline.ms/labkey/wiki/home/software/Skyline/page.view?name=video_0-5",
            "time": "25 minutes",
        },
        {
            "title": "Video Demo 3: Importing Existing Experiments",
            "url": "https://skyline.ms/labkey/wiki/home/software/Skyline/page.view?name=video_0-5b",
            "time": "27 minutes",
        },
        {
            "title": "Skyline Trailer Video",
            "url": "https://skyline.ms/labkey/wiki/home/software/Skyline/page.view?name=video_trailer",
            "time": None,
        },
    ]

    for vid in video_items:
        time_info = f" ({vid['time']})" if vid.get("time") else ""
        lines.append(f"- **[{vid['title']}]({vid['url']})**{time_info}")
    lines.append("")

    lines.append(
        "[**View all videos**](https://skyline.ms/wiki/home/software/Skyline/page.view?name=videos)"
    )
    lines.append("")

    # YouTube Channels
    lines.append("### YouTube Channels")
    lines.append("*Course content and instructional videos*")
    lines.append("")

    youtube_items = [
        {
            "title": "Skyline Course at UW",
            "url": "https://www.youtube.com/channel/UCOdJj3Spesm_U_2-N_FT7wg",
            "desc": "University of Washington course materials",
        },
        {
            "title": "May Institute at Northeastern University",
            "url": "https://www.youtube.com/channel/UCnbUMFlIRLaY7fwfSintWuQ",
            "desc": "Comprehensive proteomics course content",
        },
        {
            "title": "Targeted Proteomics Course at ETH, Zurich",
            "url": "https://www.youtube.com/channel/UCLLENascNxL22j3pntI7jVA/playlists",
            "desc": "International course materials",
        },
    ]

    for yt in youtube_items:
        lines.append(f"- **[{yt['title']}]({yt['url']})** — {yt['desc']}")
    lines.append("")

    lines.append(
        "[**View YouTube resources**](https://skyline.ms/wiki/home/software/Skyline/page.view?name=youtube)"
    )
    lines.append("")

    # UWPR Tips highlight (most useful categories)
    lines.append("### LC-MS Tips and Protocols")
    lines.append("*Selected resources from the UWPR LC-MS Tips page*")
    lines.append("")

    # Key UWPR resources to highlight
    key_uwpr_items = [
        {
            "title": "DIA Overview",
            "url": "https://proteomicsresource.washington.edu/protocols05/DIA.php",
        },
        {
            "title": "PRM Overview",
            "url": "https://proteomicsresource.washington.edu/protocols05/PRM.php",
        },
        {
            "title": "MRM/SRM Overview",
            "url": "https://proteomicsresource.washington.edu/protocols05/MRM.php",
        },
        {
            "title": "Common Mass Spec Background Ions",
            "url": "https://proteomicsresource.washington.edu/protocols05/esi_background_ions.php",
        },
        {
            "title": "Avoid Contaminations Guide",
            "url": "https://proteomicsresource.washington.edu/docs/protocols05/Avoid%20Contaminations.pdf",
        },
        {
            "title": "Packing Capillary Columns",
            "url": "https://proteomicsresource.washington.edu/docs/protocols05/Packing_Capillary_Columns.pdf",
        },
    ]

    for item in key_uwpr_items:
        lines.append(f"- [{item['title']}]({item['url']})")
    lines.append("")

    lines.append(
        "[**View all LC-MS tips**](https://proteomicsresource.washington.edu/protocols05/)"
    )

    return "\n".join(lines)


def update_resources_file(educational_content):
    """Update the resources.md file with the new Educational Materials content."""
    resources_path = Path(__file__).parent.parent / "pages" / "resources.md"

    print(f"Reading {resources_path}...")
    content = resources_path.read_text()

    # Find and replace the Educational Materials section
    # It starts with '<div id="educational"' and ends before the next tab or </div></div></div>

    # Use regex to find the educational section
    educational_pattern = r'\s*<div id="educational" class="tab-content">'
    match = re.search(educational_pattern, content)

    if not match:
        print("Error: Could not find Educational Materials section marker.")
        return False

    educational_start = match.start()
    print(f"Found educational section at position {educational_start}")

    # Find the next tab section or the closing divs before <style>
    # Look for the next tab-content div or the support section
    next_section_pattern = r'\s*<div id="support" class="tab-content">'
    next_match = re.search(next_section_pattern, content[educational_start + 10:])

    if next_match:
        # Position relative to educational_start
        section_end = educational_start + 10 + next_match.start()
    else:
        print("Error: Could not find end of Educational Materials section.")
        return False

    print(f"Educational section ends at position {section_end}")

    # Build the new educational section
    new_educational_section = f'''<div id="educational" class="tab-content">
    <div markdown="1">

{educational_content}

</div>
  </div>

'''

    # Replace the section
    content = content[:educational_start] + "\n  " + new_educational_section + content[section_end:]
    print("Updated Educational Materials section.")

    # Write the updated content
    resources_path.write_text(content)
    print(f"Saved updated {resources_path}")

    return True


def main():
    """Main function to fetch educational materials and update the resources page."""
    print("=" * 60)
    print("Fetching Educational Materials")
    print("=" * 60)

    # Fetch data from all sources
    tutorials = fetch_skyline_tutorials()
    documentation = fetch_skyline_documentation()
    uwpr_tips = fetch_uwpr_tips()
    uwpr_tools = fetch_uwpr_tools()

    # Generate content
    educational_content = generate_educational_section(
        tutorials, documentation, uwpr_tips, uwpr_tools
    )

    # Update the file
    success = update_resources_file(educational_content)

    if success:
        print("\n" + "=" * 60)
        print("Successfully updated Educational Materials section!")
        print("=" * 60)
    else:
        print("\nFailed to update resources.md")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
