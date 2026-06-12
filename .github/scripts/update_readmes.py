#!/usr/bin/env python3
"""
Update README.md with the latest listings from listings.json.

This repository tracks everything in a single "Opportunities" table.
This script reads the listings data, generates one markdown table, and
embeds it in the README between the marker comments.
"""

import os
from datetime import datetime
import util


def main():
    try:
        # Load listings
        listings = util.get_listings_from_json()

        # Validate schema
        util.check_schema(listings)

        # Keep only visible listings, then sort (active first, newest first)
        visible = [l for l in listings if l.get("is_visible", True)]
        visible = util.sort_listings(visible)

        # Generate the single table
        table = create_opportunities_table(visible)

        # Get README path
        readme_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..",
            "README.md"
        )

        # Embed table in README
        util.embed_table(
            readme_path,
            table,
            "<!-- OPPORTUNITIES_TABLE_START -->",
            "<!-- OPPORTUNITIES_TABLE_END -->"
        )

        # Set commit message
        now = datetime.now(util.PST)
        timestamp = now.strftime("%Y-%m-%d %H:%M PST")
        util.set_output("commit_message", f"Update README ({timestamp})")

        active = sum(1 for l in visible if l.get("active", True))
        print(f"Successfully updated README: {len(visible)} opportunities ({active} active)")

    except Exception as e:
        util.fail(str(e))


def create_opportunities_table(listings):
    """Create the single Opportunities table."""
    rows = []
    header = "| Status | Organization | Opportunity | Type | Location | Application | Date Posted |"
    separator = "| ------ | ------------ | ----------- | ---- | -------- | ----------- | ----------- |"
    rows.append(header)
    rows.append(separator)

    for listing in listings:
        active = listing.get("active", True)
        status = "✅ **[OPEN]**" if active else "🔒 **[CLOSED]**"

        org = util.sanitize_table_cell(listing["company_name"])

        title = util.sanitize_table_cell(listing["title"])
        title += util.get_sponsorship_badge(listing.get("sponsorship", ""))
        title += util.get_status_badge(active)

        opp_type = util.sanitize_table_cell(listing.get("opportunity_type", ""))
        location = util.format_locations(listing.get("locations", []))
        link = util.format_link(listing["url"]) if active else ":lock:"
        date = util.format_date(listing["date_posted"])

        row = f"| {status} | {org} | {title} | {opp_type} | {location} | {link} | {date} |"
        rows.append(row)

    return "\n".join(rows)


if __name__ == "__main__":
    main()
