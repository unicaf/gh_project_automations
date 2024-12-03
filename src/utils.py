import smtplib
from datetime import datetime, timedelta

import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logger import logger


def find_week(weeks, date_str):
    # Parse the input date
    target_date = datetime.strptime(date_str, '%Y-%m-%d')

    for week in weeks:
        # Parse the start date of the week
        start_date = datetime.strptime(week['startDate'], '%Y-%m-%d')
        # Calculate the end date based on the duration
        end_date = start_date + timedelta(days=week['duration'] - 1)

        # Check if the target date falls within this week
        if start_date <= target_date <= end_date:
            return week  # Return the matching week dictionary

    return None  # Return None if no matching week is found


def find_release(releases, date_str):
    # Parse the input date
    target_date = datetime.strptime(date_str, '%Y-%m-%d')

    for release in releases:
        try:
            # Extract the date range from the release name
            date_range = release['name'].split('(')[0].strip()  # Get the part before the version
            if ' - ' in date_range:
                # Extract start and end dates
                start_date_str, end_date_str = date_range.split(' - ')
                # Add the year explicitly if missing
                year = target_date.year  # Assume the target year if year is missing
                if len(start_date_str.split(',')) == 1:
                    start_date_str = f"{start_date_str}, {year}"
                if len(end_date_str.split(',')) == 1:
                    end_date_str = f"{end_date_str}, {year}"
                # Parse dates
                start_date = datetime.strptime(start_date_str.strip(), '%b %d, %Y')
                end_date = datetime.strptime(end_date_str.strip(), '%b %d, %Y')
                logger.debug(f"Parsed: {start_date} - {end_date}")
            else:
                logger.debug(f"Skipping invalid date range: {release['name']}")
                continue

            # Check if the target date falls within this release period
            if start_date <= target_date <= end_date:
                return release  # Return the matching release dictionary
        except ValueError as e:
            logger.error(f"Error parsing release: {release['name']}, Error: {e}")
            continue

    return None  # Return None if no matching release is found


def find_size(sizes, estimate_name):
    # Define size thresholds dynamically from the size definitions
    size_thresholds = {
        'X-Large (1-4 weeks)': (168, float('inf')),  # >168 hours (1-4 weeks)
        'Large (4+ -7 days)': (96, 168),           # 96-168 hours (4-7 days)
        'Medium (2+ -4 days)': (48, 96),           # 48-96 hours (2-4 days)
        'Small (1-2 days)': (24, 48),              # 24-48 hours (1-2 days)
        'Tiny (< 1 day, 1-6 hours)': (0, 24)       # <24 hours (Tiny)
    }

    # Convert the estimate to comparable hours
    if 'week' in estimate_name:
        value = float(estimate_name.split()[0]) * 7 * 24  # weeks to hours
    elif 'day' in estimate_name:
        value = float(estimate_name.split()[0]) * 24  # days to hours
    elif 'hour' in estimate_name:
        value = float(estimate_name.split()[0])  # hours
    elif 'min' in estimate_name:
        value = float(estimate_name.split()[0]) / 60  # minutes to hours
    else:
        value = 0

    # Find the matching size based on thresholds
    for size in sizes:
        size_name = size['name']
        lower, upper = size_thresholds.get(size_name, (None, None))
        if lower is not None and lower < value <= upper:
            return size  # Return the matching size definition

    return None  # Return None if no match found
