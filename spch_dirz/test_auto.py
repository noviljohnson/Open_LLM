import requests
from bs4 import BeautifulSoup


# URL of the webpage
url = "https://sg001-harmony.sliq.net/00293/Harmony/en/PowerBrowser/PowerBrowserV2/20250224/-1/76679"

# Fetch the webpage
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")


# Search for .m3u8 links
m3u8_links = []
for tag in soup.find_all("script"):
    if ".m3u8" in tag.text:
        m3u8_links.append(tag.text.split(".m3u8")[0] + ".m3u8")

print(m3u8_links)
"https"+m3u8_links[0].split('https')[-1]


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

print(video_links)
all_m3u8_links = []
for url2 in video_links:
    # Fetch the webpage
    response = requests.get(url2)
    soup = BeautifulSoup(response.text, "html.parser")


    # Search for .m3u8 links
    m3u8_links = []
    for tag in soup.find_all("script"):
        if ".m3u8" in tag.text:
            m3u8_links.append(tag.text.split(".m3u8")[0] + ".m3u8")

    all_m3u8_links.append(m3u8_links)
len(all_m3u8_links)
for vdo in all_m3u8_links:
    print("https"+vdo[0].split('https')[-1])
