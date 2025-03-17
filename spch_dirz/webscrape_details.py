import requests
from bs4 import BeautifulSoup


# URL of the webpage
url = "https://sg001-harmony.sliq.net/00293/Harmony/en/View/RecentEnded/20250224/-1"

# Fetch the webpage
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Extract video links
video_links = []
for a_tag in soup.find_all("a", href=True):
    href = a_tag["href"]
    if "/PowerBrowser/PowerBrowserV2/" in href:
        full_url = f"https://sg001-harmony.sliq.net{href}"
        video_links.append(full_url)



def clean_text(text):
    return text.replace("\xa0", " ").strip()


def split_time_range(time_range):
    times = clean_text(time_range).split("-")
    return times[0].strip(), times[1].strip() if len(times) > 1 else (times[0].strip(), None)


def split_date(date_text):
    """
    example date : Wednesday, Mar 12, 2025
    """
    parts = date_text.split(",")
    if len(parts) < 2:
        return "Unknown", "Unknown", "Unknown", "Unknown"
    
    day, month_date, year = parts[0].strip(), parts[1].strip(), parts[-1].strip()
    date_parts = month_date.split()
    
    if len(date_parts) == 2:
        month, date = date_parts
    else:
        month, date, year = (date_parts + ["Unknown"] * 3)[:3]
    
    return day, month, date, year



all_video_details = []

for url2 in video_links[:2]:
    response = requests.get(url2)
    soup = BeautifulSoup(response.text, "html.parser")

    # Search for .m3u8 links
    m3u8_links = []
    for tag in soup.find_all("script"):
        if ".m3u8" in tag.text:
            m3u8_links.append(tag.text.split(".m3u8")[0] + ".m3u8")

    # Scrape video details
    description = soup.find("span", id="description")
    fallback_description = soup.find("span", class_="headerTitle")
    location = soup.find("span", id="location")
    scheduled_date = soup.find("div", id="scheduleddate")
    scheduled_time = soup.find("div", id="scheduledtime")
    scheduled_duration = soup.find("div", id="scheduledduration")
    actual_date = soup.find("div", id="actualdate")
    actual_time = soup.find("div", id="actualtime")
    actual_duration = soup.find("div", id="actualduration")

    # Clean and split times
    scheduled_start, scheduled_end = split_time_range(scheduled_time.text if scheduled_time else "")
    actual_start, actual_end = split_time_range(actual_time.text if actual_time else "")

    # Split date
    scheduled_day, scheduled_month, scheduled_date_num, scheduled_year = split_date(scheduled_date.text if scheduled_date else "Unknown")
    actual_day, actual_month, actual_date_num, actual_year = split_date(actual_date.text if actual_date else "Unknown")

    # Build video details dictionary
    video_info = {
        "video_link":url2,
        "m3u8_link": "https" + m3u8_links[0].split('https')[-1] if m3u8_links else None,
        "description": clean_text(description.text) if description else clean_text(fallback_description.text) if fallback_description else "Unknown",
        "location": clean_text(location.text) if location else "Unknown",
        "scheduled": {
            "day": scheduled_day,
            "month": scheduled_month,
            "date": scheduled_date_num,
            "year": scheduled_year,
            "start_time": scheduled_start,
            "end_time": scheduled_end,
            "duration": clean_text(scheduled_duration.text) if scheduled_duration else "Unknown",
        },
        "actual": {
            "day": actual_day,
            "month": actual_month,
            "date": actual_date_num,
            "year": actual_year,
            "start_time": actual_start,
            "end_time": actual_end,
            "duration": clean_text(actual_duration.text) if actual_duration else "Unknown",
        }
    }

    all_video_details.append(video_info)

# # Print all video details
# for video in all_video_details:
#     print(video)

import json
with open("all_video_details.json", "w") as f:
    json.dump(all_video_details, f, indent=4)