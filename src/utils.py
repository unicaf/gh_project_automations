from datetime import datetime, timedelta
from logger import logger


def find_week(weeks, date_str):
    # Parse the input date
    target_date = datetime.strptime(date_str, '%Y-%m-%d')

    # Get today's date
    today = datetime.today()

    # Calculate the start of the current week (Monday by default)
    start_of_week = datetime(today.year, today.month, today.day) - timedelta(days=today.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate the end of the current week
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

    # Check if the target date is within the current week
    if start_of_week <= target_date <= end_of_week:
        for week in weeks:
            # Parse the start date of the week
            start_date = datetime.strptime(week['startDate'], '%Y-%m-%d')
            # Calculate the end date based on the duration
            end_date = start_date + timedelta(days=week['duration'] - 1)

            # Check if the target date falls within this week
            if start_date <= target_date <= end_date:
                return week  # Return the matching week dictionary

        return None  # Return None if no matching week is found
    else:
        return find_previous_week(weeks, date_str)


def find_previous_week(weeks, date_str):
    # Parse the input date
    target_date = datetime.strptime(date_str, '%Y-%m-%d')

    # Sort the weeks by their startDate
    sorted_weeks = sorted(weeks, key=lambda week: datetime.strptime(week['startDate'], '%Y-%m-%d'))

    previous_week = None
    for i, week in enumerate(sorted_weeks):
        week_start_date = datetime.strptime(week['startDate'], '%Y-%m-%d')
        week_end_date = week_start_date + timedelta(days=week['duration'] - 1)

        # If the current week includes the target date or is in the future, pick the previous week
        if week_start_date <= target_date <= week_end_date or week_start_date > target_date:
            if i > 0:
                previous_week = sorted_weeks[i - 1]
            break

    return previous_week


def find_release(releases, date_str):
    from datetime import datetime

    # Parse the input date
    target_date = datetime.strptime(date_str, '%Y-%m-%d')

    for release in releases:
        try:
            # Extract the date range from the release name
            date_range = release['name'].split('(')[0].strip()  # Get the part before the version
            if ' - ' in date_range:
                start_date_str, end_date_str = date_range.split(' - ')
                # Append the year from the end_date for parsing
                if ',' not in end_date_str:
                    end_date_str += f", {target_date.year}"
                end_date = datetime.strptime(end_date_str.strip(), '%b %d, %Y')

                # Determine the year for the start_date
                if ',' not in start_date_str:
                    # Parse start_date with the same year as end_date by default
                    start_date = datetime.strptime(start_date_str.strip() + f", {end_date.year}", '%b %d, %Y')

                    # Adjust the year if the start month is greater than the end month
                    if start_date.month > end_date.month:
                        start_date = start_date.replace(year=end_date.year - 1)
                else:
                    start_date = datetime.strptime(start_date_str.strip(), '%b %d, %Y')

                # Debugging output for validation
                logger.debug(f"Release: {release['name']}, Start: {start_date}, End: {end_date}")

                # Check if the target date falls within this release period
                if start_date <= target_date <= end_date:
                    return release  # Return the matching release dictionary
        except Exception as e:
            # Log parsing issues for debugging
            logger.error(f"Error parsing release: {release['name']}, Error: {e}")
            continue

    return None  # Return None if no matching release is found


def find_size(sizes, estimate_name):
    # Define size thresholds dynamically from the size definitions
    size_thresholds = {
        'X-Large (1-4 weeks)': (168, float('inf')),  # >168 hours (1-4 weeks)
        'Large (4+ -7 days)': (96, 168),  # 96-168 hours (4-7 days)
        'Medium (2+ -4 days)': (48, 96),  # 48-96 hours (2-4 days)
        'Small (1-2 days)': (24, 48),  # 24-48 hours (1-2 days)
        'Tiny (< 1 day, 1-6 hours)': (0, 24)  # <24 hours (Tiny)
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
