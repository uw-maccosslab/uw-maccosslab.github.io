#!/usr/bin/env python3
"""
Fetch Skyline events and webinars and update the Support & Training section.

This script scrapes:
- Events from https://skyline.ms/home/software/Skyline/events/project-begin.view
- Webinars from https://skyline.ms/home/software/Skyline/wiki-page.view?name=webinars

And updates the Support & Training tab in pages/resources.md with year-based navigation.
"""

import re
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# URLs to scrape
EVENTS_URL = "https://skyline.ms/home/software/Skyline/events/project-begin.view"
WEBINARS_URL = "https://skyline.ms/home/software/Skyline/wiki-page.view?name=webinars"

# Headers to avoid being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def fetch_events():
    """Fetch events from the Skyline events page."""
    print("Fetching events from Skyline website...")

    try:
        response = requests.get(EVENTS_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching events: {e}")
        return {"upcoming": [], "past": defaultdict(list)}

    soup = BeautifulSoup(response.text, "html.parser")

    upcoming_events = []
    past_events = defaultdict(list)

    # Find the main content - look for "Upcoming" and "Past" section headers
    # The page structure has h4 headers: "#### Upcoming" and "#### Past"
    page_text = response.text

    # Find positions of Upcoming and Past sections in the HTML
    upcoming_start = page_text.lower().find(">upcoming<")
    past_start = page_text.lower().find(">past<")

    if upcoming_start == -1 or past_start == -1:
        print("Warning: Could not find Upcoming/Past section markers, falling back to year-based detection")
        # Fallback to old behavior
        return fetch_events_by_year(soup)

    # Parse upcoming section (between "Upcoming" and "Past" headers)
    upcoming_html = page_text[upcoming_start:past_start]
    upcoming_soup = BeautifulSoup(upcoming_html, "html.parser")

    # Parse past section (after "Past" header)
    past_html = page_text[past_start:]
    past_soup = BeautifulSoup(past_html, "html.parser")

    # Extract events from upcoming section
    for link in upcoming_soup.find_all("a", href=True):
        text = link.get_text(strip=True)
        href = link["href"]

        # Skip navigation links and empty links
        if not text or text in ["Sign In", "MacCoss Lab Software", "#"]:
            continue

        # Get parent text for context
        parent_text = ""
        for parent in link.parents:
            if parent.name in ["p", "div", "li"]:
                parent_text = parent.get_text()
                break

        # Extract year from text
        year_match = re.search(r"\b(20\d{2})\b", text + " " + parent_text)
        if not year_match:
            continue

        year = int(year_match.group(1))

        event_info = extract_event_info(text, href, parent_text)
        if event_info:
            event_info["year"] = year
            upcoming_events.append(event_info)

    # Extract events from past section
    for link in past_soup.find_all("a", href=True):
        text = link.get_text(strip=True)
        href = link["href"]

        # Skip navigation links and empty links
        if not text or text in ["Sign In", "MacCoss Lab Software", "#"]:
            continue

        # Get parent text for context
        parent_text = ""
        for parent in link.parents:
            if parent.name in ["p", "div", "li"]:
                parent_text = parent.get_text()
                break

        # Extract year from text
        year_match = re.search(r"\b(20\d{2})\b", text + " " + parent_text)
        if not year_match:
            continue

        year = int(year_match.group(1))

        event_info = extract_event_info(text, href, parent_text)
        if event_info:
            event_info["year"] = year
            past_events[year].append(event_info)

    print(f"Found {len(upcoming_events)} upcoming events")
    print(f"Found events for years: {sorted(past_events.keys(), reverse=True)}")

    return {"upcoming": upcoming_events, "past": past_events}


def fetch_events_by_year(soup):
    """Fallback: fetch events using year-based detection (deprecated)."""
    upcoming_events = []
    past_events = defaultdict(list)

    for link in soup.find_all("a", href=True):
        text = link.get_text(strip=True)
        href = link["href"]

        if not text or text in ["Sign In", "MacCoss Lab Software", "#"]:
            continue

        parent_text = ""
        for parent in link.parents:
            if parent.name in ["p", "div", "li"]:
                parent_text = parent.get_text()
                break

        year_match = re.search(r"\b(20\d{2})\b", text + " " + parent_text)
        if not year_match:
            continue

        year = int(year_match.group(1))

        event_info = extract_event_info(text, href, parent_text)
        if event_info:
            event_info["year"] = year
            # All events go to past in fallback mode
            past_events[year].append(event_info)

    return {"upcoming": upcoming_events, "past": past_events}


def extract_event_info(text, href, parent_text):
    """Extract structured event information from text and href."""
    # Skip certain non-event links
    skip_patterns = ["watch the", "review the", "slides", "videos", "recording"]
    if any(pattern in text.lower() for pattern in skip_patterns):
        return None

    # Clean up the text
    name = text.strip()

    # Make href absolute if needed
    if href.startswith("/"):
        href = f"https://skyline.ms{href}"
    elif not href.startswith("http"):
        href = f"https://skyline.ms/{href}"

    # Try to extract location and date from parent text
    location = ""
    date_str = ""

    # Common location patterns
    location_patterns = [
        r"Seattle,?\s*WA",
        r"Boston,?\s*MA",
        r"Baltimore,?\s*MD",
        r"San Diego,?\s*CA",
        r"Anaheim,?\s*CA",
        r"Houston,?\s*TX",
        r"Minneapolis,?\s*MN",
        r"Barcelona,?\s*Spain",
        r"Zurich",
        r"ETH,?\s*Zurich",
        r"Dortmund",
        r"ISAS Dortmund",
        r"Northeastern University",
        r"University of Washington",
        r"IIT,?\s*Bombay",
        r"Mumbai,?\s*India",
    ]

    for pattern in location_patterns:
        match = re.search(pattern, parent_text, re.IGNORECASE)
        if match:
            location = match.group(0)
            break

    # Extract date patterns
    date_patterns = [
        r"\(([A-Za-z]+\s+\d+[-–]\d+,?\s+\d{4})\)",  # (March 2-5, 2026)
        r"\(([A-Za-z]+\s+\d+\s*[-–]\s*\d+,?\s+\d{4})\)",  # (April 27 - May 9, 2026)
        r"\(([A-Za-z]+\s+\d+,?\s+\d{4})\)",  # (June 1, 2025)
    ]

    for pattern in date_patterns:
        match = re.search(pattern, parent_text)
        if match:
            date_str = match.group(1)
            break

    return {"name": name, "url": href, "location": location, "date": date_str}


def fetch_webinars():
    """Fetch webinars from the Skyline webinars page."""
    print("Fetching webinars from Skyline website...")

    try:
        response = requests.get(WEBINARS_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching webinars: {e}")
        return defaultdict(list)

    soup = BeautifulSoup(response.text, "html.parser")
    webinars = defaultdict(list)

    # Find all webinar links - they have pattern like "#1:", "#2:", etc.
    for link in soup.find_all("a", href=True):
        text = link.get_text(strip=True)

        # Match webinar pattern like "#26: DIA with FragPipe..."
        webinar_match = re.match(r"#(\d+):\s*(.+)", text)
        if webinar_match:
            number = int(webinar_match.group(1))
            title = webinar_match.group(2)
            href = link["href"]

            # Make href absolute
            if href.startswith("/"):
                href = f"https://skyline.ms{href}"
            elif not href.startswith("http"):
                href = f"https://skyline.ms/{href}"

            # Try to find the year/month from surrounding text
            parent_text = ""
            for parent in link.parents:
                if parent.name in ["p", "div", "td"]:
                    parent_text = parent.get_text()
                    break

            # Extract year from parent text or webinar number pattern
            year = None
            month = ""

            # Check for year pattern in parent
            year_match = re.search(r"\b(20\d{2})\b", parent_text)
            if year_match:
                year = int(year_match.group(1))

            # Extract month if present
            month_match = re.search(
                r"\((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}?\)",
                parent_text,
                re.IGNORECASE,
            )
            if month_match:
                month = month_match.group(0).strip("()")

            # Infer year from webinar number if not found
            if not year:
                if number >= 25:
                    year = 2025
                elif number >= 23:
                    year = 2024
                elif number >= 22:
                    year = 2023
                elif number >= 20:
                    year = 2021
                elif number >= 18:
                    year = 2020
                elif number >= 17:
                    year = 2018
                elif number >= 13:
                    year = 2017
                elif number >= 8:
                    year = 2015
                else:
                    year = 2014

            webinars[year].append(
                {"number": number, "title": title, "url": href, "month": month}
            )

    # Sort webinars by number within each year
    for year in webinars:
        webinars[year].sort(key=lambda x: x["number"], reverse=True)

    print(f"Found webinars for years: {sorted(webinars.keys(), reverse=True)}")

    return webinars


def generate_support_section(events, webinars):
    """Generate the Support & Training section with year-based navigation."""
    lines = []

    # Count total events and webinars
    total_past_events = sum(len(e) for e in events["past"].values())
    total_webinars = sum(len(w) for w in webinars.values())
    total_upcoming = len(events["upcoming"])

    # Header with last updated timestamp
    lines.append("## Support & Training")
    lines.append("")
    current_date = datetime.now().strftime("%B %d, %Y")
    lines.append(f"*Last updated: {current_date} — {total_upcoming} upcoming events, {total_past_events} past events, {total_webinars} webinars*")
    lines.append("")
    lines.append("### Forums and Discussion")
    lines.append("- [Skyline Support Board](https://skyline.ms/forum)")
    lines.append("- [Panorama Support Board](https://panoramaweb.org/forum)")
    lines.append(
        "- **[University of Washington Proteomics Listserv](https://mailman23.u.washington.edu/mailman/listinfo/proteomics)** - If you are at UW and doing proteomics you should join this list."
    )
    lines.append("")

    # Upcoming Events section
    lines.append("### Upcoming Events")
    lines.append("")

    if events["upcoming"]:
        for event in events["upcoming"]:
            date_info = f" ({event['date']})" if event.get("date") else ""
            lines.append(f"- **[{event['name']}]({event['url']})**{date_info}")
    else:
        lines.append(
            "*Check [Skyline Events](https://skyline.ms/home/software/Skyline/events/project-begin.view) for upcoming courses and events.*"
        )
    lines.append("")

    # Webinars section
    lines.append("### Skyline Webinar Series")
    lines.append("")
    lines.append(
        "The Skyline Team presents tutorial webinars designed to help you get the most out of Skyline targeted proteomics software. Each ~90 minute webinar includes Q&A, presentations, and tutorial data."
    )
    lines.append("")

    # Get all webinar years
    webinar_years = sorted(webinars.keys(), reverse=True)

    if webinar_years:
        # Show most recent webinars inline
        recent_year = webinar_years[0]
        lines.append(f"**Recent Webinars ({recent_year}):**")
        for webinar in webinars[recent_year][:5]:  # Show up to 5 recent webinars
            month_info = f" ({webinar['month']})" if webinar.get("month") else ""
            lines.append(
                f"- [#{webinar['number']}: {webinar['title']}]({webinar['url']}){month_info}"
            )
        lines.append("")
        lines.append(
            f"*[View all {sum(len(w) for w in webinars.values())} webinars](https://skyline.ms/home/software/Skyline/wiki-page.view?name=webinars)*"
        )
        lines.append("")

    # Past Events with year navigation
    lines.append("### Past Events by Year")
    lines.append("")

    # Get all years from past events
    past_years = sorted(events["past"].keys(), reverse=True)

    if not past_years:
        lines.append(
            "*Visit [Skyline Events](https://skyline.ms/home/software/Skyline/events/project-begin.view) for event history.*"
        )
    else:
        # Build year navigation and content
        lines.append('<div class="events-container">')
        lines.append("")

        # Year navigation sidebar
        lines.append('<div class="event-year-navigation">')
        for i, year in enumerate(past_years):
            event_count = len(events["past"][year])
            active_class = ' class="active"' if i == 0 else ""
            lines.append(
                f'<button{active_class} onclick="showEventYear({year})">{year} ({event_count})</button>'
            )
        lines.append("</div>")
        lines.append("")

        # Year content
        lines.append('<div class="event-year-content-area">')
        for i, year in enumerate(past_years):
            display = "block" if i == 0 else "none"
            lines.append(f'<div id="events-{year}" style="display: {display};">')
            lines.append(f"<h4>{year} Events</h4>")
            lines.append("<ul>")

            for event in events["past"][year]:
                location_info = f" - {event['location']}" if event.get("location") else ""
                date_info = f" ({event['date']})" if event.get("date") else ""
                lines.append(
                    f"<li><a href=\"{event['url']}\">{event['name']}</a>{location_info}{date_info}</li>"
                )

            lines.append("</ul>")
            lines.append("</div>")
            lines.append("")

        lines.append("</div>")
        lines.append("</div>")
        lines.append("")

        # JavaScript for year navigation
        lines.append("<script>")
        lines.append("function showEventYear(year) {")
        lines.append(
            "  document.querySelectorAll('.event-year-content-area > div').forEach(d => d.style.display = 'none');"
        )
        lines.append(
            "  document.querySelectorAll('.event-year-navigation button').forEach(b => b.classList.remove('active'));"
        )
        lines.append(
            "  document.getElementById('events-' + year).style.display = 'block';"
        )
        lines.append("  event.target.classList.add('active');")
        lines.append("}")
        lines.append("</script>")
        lines.append("")

    return "\n".join(lines)


def generate_event_styles():
    """Generate CSS styles for the events section."""
    return """
.events-container {
  display: flex;
  gap: 20px;
  margin: 20px 0;
}

.event-year-navigation {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 100px;
  position: sticky;
  top: 20px;
  height: fit-content;
}

.event-year-navigation button {
  padding: 8px 12px;
  border: 1px solid #ddd;
  background: #f8f9fa;
  cursor: pointer;
  text-align: left;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.event-year-navigation button:hover {
  background: #e9ecef;
}

.event-year-navigation button.active {
  background: #2E86AB;
  color: white;
  border-color: #2E86AB;
}

.event-year-content-area {
  flex: 1;
}

.event-year-content-area h4 {
  margin-top: 0;
  color: #2E86AB;
}

.event-year-content-area ul {
  padding-left: 20px;
}

.event-year-content-area li {
  margin-bottom: 8px;
}

@media (max-width: 768px) {
  .events-container {
    flex-direction: column;
  }
  
  .event-year-navigation {
    flex-direction: row;
    flex-wrap: wrap;
    position: static;
  }
  
  .event-year-navigation button {
    flex: 0 0 auto;
  }
}
"""


def update_resources_file(support_content, event_styles):
    """Update the resources.md file with the new Support & Training content."""
    resources_path = Path(__file__).parent.parent / "pages" / "resources.md"

    print(f"Reading {resources_path}...")
    content = resources_path.read_text()

    # Find and replace the Support & Training section
    # The section starts with '<div id="support"' (with possible leading whitespace)
    # and ends before '<style>'

    # Use regex to find the support section with optional whitespace
    support_pattern = r'\s*<div id="support" class="tab-content">'
    match = re.search(support_pattern, content)

    if not match:
        print("Error: Could not find Support & Training section marker.")
        return False

    support_start = match.start()
    print(f"Found support section at position {support_start}")

    # Find the <style> tag that follows the support section
    style_marker = "\n<style>"
    style_pos = content.find(style_marker, support_start)

    if style_pos == -1:
        print("Error: Could not find <style> section after Support & Training.")
        return False

    print(f"Found <style> at position {style_pos}")

    # Build the new support section
    new_support_section = f'''<div id="support" class="tab-content">
    <div markdown="1">

{support_content}

</div>
</div>
</div>'''

    # Replace everything from support_start to style_pos
    content = content[:support_start] + "\n  " + new_support_section + content[style_pos:]
    print("Updated Support & Training section.")

    # Add or update event styles in the style block
    if ".events-container" not in content:
        # Find the closing </style> tag and add our styles before it
        style_end = content.rfind("</style>")
        if style_end != -1:
            content = content[:style_end] + event_styles + "\n" + content[style_end:]
            print("Added event styles.")

    # Write the updated content
    resources_path.write_text(content)
    print(f"Saved updated {resources_path}")

    return True


def main():
    """Main function to fetch events and update the resources page."""
    print("=" * 60)
    print("Fetching Skyline Events and Webinars")
    print("=" * 60)

    # Fetch data
    events = fetch_events()
    webinars = fetch_webinars()

    # Generate content
    support_content = generate_support_section(events, webinars)
    event_styles = generate_event_styles()

    # Update the file
    success = update_resources_file(support_content, event_styles)

    if success:
        print("\n" + "=" * 60)
        print("Successfully updated Support & Training section!")
        print("=" * 60)
    else:
        print("\nFailed to update resources.md")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
