#!/usr/bin/env python3
"""
Comprehensive lyrics extraction for "Loose Talk" album
Amelia Barratt & Bryan Ferry (2025)

Extracts from:
1. YouTube official videos (descriptions, comments)
2. Lyrics.com search results
3. Alternative lyrics databases
"""

import requests
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

results = {
    "timestamp": datetime.now().isoformat(),
    "album": "Loose Talk - Amelia Barratt & Bryan Ferry",
    "extraction_sources": []
}

print("="*80)
print("LYRICS EXTRACTION: Loose Talk Album")
print("="*80)

# =============================================================================
# YOUTUBE VIDEO EXTRACTION
# =============================================================================
print("\n[1/4] Extracting from YouTube official videos...")

youtube_queries = [
    "Bryan Ferry Amelia Barratt Loose Talk official video",
    "Bryan Ferry Amelia Barratt Orchestra official video",
    "Bryan Ferry Amelia Barratt Florist official video",
    "loose talk amelia barratt full album lyrics"
]

youtube_findings = {
    "platform": "YouTube",
    "videos_found": [],
    "lyrics_extracted": []
}

for query in youtube_queries:
    try:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            # Extract video IDs and titles
            video_data = re.findall(r'"videoId":"([^"]+)".*?"title":{"runs":\[{"text":"([^"]+)"}', response.text)

            if video_data:
                video_id, title = video_data[0]
                print(f"  ✓ Found: {title}")
                print(f"    Video ID: {video_id}")

                # Now access the video page directly for description
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                video_response = requests.get(video_url, headers=headers, timeout=15)

                if video_response.status_code == 200:
                    # Extract description
                    desc_match = re.search(r'"description":{"simpleText":"([^"]+)"', video_response.text)
                    if desc_match:
                        description = desc_match.group(1)
                        print(f"    Description: {description[:200]}...")

                        youtube_findings["videos_found"].append({
                            "title": title,
                            "video_id": video_id,
                            "url": video_url,
                            "description": description
                        })

                    # Look for lyrics in description or comments
                    lyrics_in_desc = re.findall(r'[A-Z][a-z]+ [a-z]+ [a-z]+.*\n', video_response.text)
                    if lyrics_in_desc:
                        youtube_findings["lyrics_extracted"].append({
                            "source": title,
                            "lyrics_snippet": lyrics_in_desc
                        })

    except Exception as e:
        print(f"  ✗ Error accessing {query}: {e}")

results["extraction_sources"].append(youtube_findings)

# =============================================================================
# LYRICS.COM EXTRACTION
# =============================================================================
print("\n[2/4] Extracting from Lyrics.com...")

lyrics_com_findings = {
    "platform": "Lyrics.com",
    "search_results": [],
    "full_lyrics": []
}

try:
    # Direct search
    search_url = "https://www.lyrics.com/lyrics/loose%20talk%20amelia%20barratt"
    response = requests.get(search_url, headers=headers, timeout=15)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all lyric links
        lyric_links = soup.find_all('a', href=re.compile(r'/lyric/'))

        print(f"  ✓ Found {len(lyric_links)} lyric links")

        for link in lyric_links[:10]:  # Top 10 results
            lyric_url = "https://www.lyrics.com" + link['href']
            lyric_title = link.text.strip()

            if 'loose talk' in lyric_title.lower() or 'barratt' in lyric_title.lower():
                print(f"  → Accessing: {lyric_title}")

                try:
                    lyric_page = requests.get(lyric_url, headers=headers, timeout=15)
                    if lyric_page.status_code == 200:
                        lyric_soup = BeautifulSoup(lyric_page.text, 'html.parser')

                        # Extract lyrics (usually in pre-lyric-body or lyric-body div)
                        lyric_body = lyric_soup.find('pre', id='lyric-body-text')
                        if not lyric_body:
                            lyric_body = lyric_soup.find('div', class_='lyric-body')

                        if lyric_body:
                            lyrics_text = lyric_body.get_text(strip=True)
                            print(f"    ✓ Extracted {len(lyrics_text)} characters")

                            lyrics_com_findings["full_lyrics"].append({
                                "track": lyric_title,
                                "url": lyric_url,
                                "lyrics": lyrics_text
                            })
                        else:
                            print(f"    ✗ No lyrics found in page")

                except Exception as e:
                    print(f"    ✗ Error accessing lyric page: {e}")

        lyrics_com_findings["search_results"] = [
            {"title": link.text.strip(), "url": "https://www.lyrics.com" + link['href']}
            for link in lyric_links[:10]
        ]

except Exception as e:
    print(f"  ✗ Error accessing Lyrics.com: {e}")

results["extraction_sources"].append(lyrics_com_findings)

# =============================================================================
# MUSIXMATCH EXTRACTION
# =============================================================================
print("\n[3/4] Attempting Musixmatch...")

musixmatch_findings = {
    "platform": "Musixmatch",
    "tracks_found": []
}

try:
    search_url = "https://www.musixmatch.com/search/loose%20talk%20amelia%20barratt"
    response = requests.get(search_url, headers=headers, timeout=15)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        track_links = soup.find_all('a', href=re.compile(r'/lyrics/'))

        print(f"  ✓ Found {len(track_links)} track links")

        for link in track_links[:5]:
            track_url = "https://www.musixmatch.com" + link['href']
            track_title = link.text.strip()

            musixmatch_findings["tracks_found"].append({
                "title": track_title,
                "url": track_url
            })

            print(f"  → {track_title}")
    else:
        print(f"  ✗ Status: {response.status_code}")

except Exception as e:
    print(f"  ✗ Error: {e}")

results["extraction_sources"].append(musixmatch_findings)

# =============================================================================
# GENIUS LYRICS (May be blocked but try)
# =============================================================================
print("\n[4/4] Attempting Genius Lyrics...")

genius_findings = {
    "platform": "Genius",
    "status": None,
    "tracks_found": []
}

try:
    search_url = "https://genius.com/search?q=loose%20talk%20amelia%20barratt"
    response = requests.get(search_url, headers=headers, timeout=15)

    genius_findings["status"] = response.status_code

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Genius uses different structure - look for song results
        songs = soup.find_all('a', class_=re.compile(r'song'))

        print(f"  ✓ Found {len(songs)} songs")

        for song in songs[:5]:
            if song.get('href'):
                track_url = song['href']
                if not track_url.startswith('http'):
                    track_url = "https://genius.com" + track_url

                genius_findings["tracks_found"].append({
                    "url": track_url
                })

                print(f"  → {track_url}")
    else:
        print(f"  ✗ Status: {response.status_code} (Expected - often blocked)")

except Exception as e:
    print(f"  ✗ Error: {e}")
    genius_findings["error"] = str(e)

results["extraction_sources"].append(genius_findings)

# =============================================================================
# SAVE RESULTS
# =============================================================================
print("\n" + "="*80)
print("EXTRACTION COMPLETE")
print("="*80)

output_file = "/tmp/MEMORY_BUS_LYRICS_EXTRACTION_COMPREHENSIVE_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Results saved to: {output_file}")

# Summary
print("\nSUMMARY:")
print(f"  YouTube videos found: {len(youtube_findings['videos_found'])}")
print(f"  Lyrics.com results: {len(lyrics_com_findings['full_lyrics'])}")
print(f"  Musixmatch tracks: {len(musixmatch_findings['tracks_found'])}")
print(f"  Genius tracks: {len(genius_findings['tracks_found'])}")

print("\n" + "="*80)
