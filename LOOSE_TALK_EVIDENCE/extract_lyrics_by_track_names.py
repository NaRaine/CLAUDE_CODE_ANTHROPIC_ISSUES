#!/usr/bin/env python3
"""
Extract lyrics for each specific track from "Loose Talk" album
Using exact track names from CD-TEXT

Tracks:
1. Big Things
2. Stand Near Me
3. Florist
4. Cowboy Hat
5. Demolition
6. Orchestra
7. Holiday
8. Landscape
9. Pictures On A Wall
10. White Noise
11. Loose Talk
"""

import requests
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

tracks = [
    {"num": 1, "title": "Big Things", "isrc": "QMFME2434426"},
    {"num": 2, "title": "Stand Near Me", "isrc": "QMFME2434427"},
    {"num": 3, "title": "Florist", "isrc": "QMFME2434428"},
    {"num": 4, "title": "Cowboy Hat", "isrc": "QMFME2434429"},
    {"num": 5, "title": "Demolition", "isrc": "QMFME2434430"},
    {"num": 6, "title": "Orchestra", "isrc": "QMFME2434431"},
    {"num": 7, "title": "Holiday", "isrc": "QMFME2434432"},
    {"num": 8, "title": "Landscape", "isrc": "QMFME2434433"},
    {"num": 9, "title": "Pictures On A Wall", "isrc": "QMFME2434434"},
    {"num": 10, "title": "White Noise", "isrc": "QMFME2434435"},
    {"num": 11, "title": "Loose Talk", "isrc": "QMFME2434436"}
]

results = {
    "timestamp": datetime.now().isoformat(),
    "album": "Loose Talk - Bryan Ferry and Amelia Barratt",
    "tracks": []
}

print("="*80)
print("LYRICS EXTRACTION: Track-by-Track")
print("="*80)

for track in tracks:
    print(f"\n{'='*80}")
    print(f"TRACK {track['num']}: {track['title']}")
    print(f"ISRC: {track['isrc']}")
    print(f"{'='*80}")

    track_result = {
        "track_number": track['num'],
        "title": track['title'],
        "isrc": track['isrc'],
        "lyrics_found": False,
        "lyrics": None,
        "sources_tried": []
    }

    # =============================================================================
    # 1. LYRICS.COM - Most promising
    # =============================================================================
    print("\n[1/5] Searching Lyrics.com...")
    try:
        query = f"{track['title']} bryan ferry amelia barratt"
        search_url = f"https://www.lyrics.com/lyrics/{query.replace(' ', '%20')}"

        response = requests.get(search_url, headers=headers, timeout=15)
        track_result["sources_tried"].append({
            "source": "Lyrics.com",
            "url": search_url,
            "status": response.status_code
        })

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            lyric_links = soup.find_all('a', href=re.compile(r'/lyric/'))

            print(f"  Found {len(lyric_links)} results")

            # Look for exact match
            for link in lyric_links[:5]:
                link_text = link.text.strip().lower()
                if track['title'].lower() in link_text and ('ferry' in link_text or 'barratt' in link_text):
                    lyric_url = "https://www.lyrics.com" + link['href']
                    print(f"  → Exact match found: {link.text.strip()}")
                    print(f"     Accessing: {lyric_url}")

                    try:
                        lyric_page = requests.get(lyric_url, headers=headers, timeout=15)
                        if lyric_page.status_code == 200:
                            lyric_soup = BeautifulSoup(lyric_page.text, 'html.parser')

                            # Try multiple selectors
                            lyric_body = (
                                lyric_soup.find('pre', id='lyric-body-text') or
                                lyric_soup.find('div', class_='lyric-body') or
                                lyric_soup.find('div', id='lyric-body') or
                                lyric_soup.find('pre', class_='lyric-text')
                            )

                            if lyric_body:
                                lyrics_text = lyric_body.get_text(separator='\n', strip=True)
                                print(f"  ✓ SUCCESS! Extracted {len(lyrics_text)} characters")
                                track_result["lyrics"] = lyrics_text
                                track_result["lyrics_found"] = True
                                track_result["source"] = lyric_url
                                break
                    except Exception as e:
                        print(f"  ✗ Error accessing lyric page: {e}")
        else:
            print(f"  ✗ Status: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    # If found, skip other sources for this track
    if track_result["lyrics_found"]:
        results["tracks"].append(track_result)
        continue

    # =============================================================================
    # 2. AZLyrics - May be blocked but try
    # =============================================================================
    print("\n[2/5] Attempting AZLyrics...")
    try:
        # AZLyrics format: artist name lowercase, no spaces, then song
        artist_slug = "bryanferry"
        song_slug = track['title'].lower().replace(' ', '')
        azlyrics_url = f"https://www.azlyrics.com/lyrics/{artist_slug}/{song_slug}.html"

        time.sleep(2)  # Be polite
        response = requests.get(azlyrics_url, headers=headers, timeout=15)
        track_result["sources_tried"].append({
            "source": "AZLyrics",
            "url": azlyrics_url,
            "status": response.status_code
        })

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # AZLyrics puts lyrics in div with no class after div with class "ringtone"
            ringtone_div = soup.find('div', class_='ringtone')
            if ringtone_div:
                lyrics_div = ringtone_div.find_next('div')
                if lyrics_div:
                    lyrics_text = lyrics_div.get_text(separator='\n', strip=True)
                    if len(lyrics_text) > 50:  # Sanity check
                        print(f"  ✓ SUCCESS! Extracted {len(lyrics_text)} characters")
                        track_result["lyrics"] = lyrics_text
                        track_result["lyrics_found"] = True
                        track_result["source"] = azlyrics_url
        else:
            print(f"  ✗ Status: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    if track_result["lyrics_found"]:
        results["tracks"].append(track_result)
        continue

    # =============================================================================
    # 3. Genius - May be blocked
    # =============================================================================
    print("\n[3/5] Attempting Genius...")
    try:
        query = f"bryan-ferry-{track['title'].lower().replace(' ', '-')}"
        genius_url = f"https://genius.com/{query}-lyrics"

        time.sleep(2)
        response = requests.get(genius_url, headers=headers, timeout=15)
        track_result["sources_tried"].append({
            "source": "Genius",
            "url": genius_url,
            "status": response.status_code
        })

        if response.status_code == 200:
            # Genius is harder to scrape but worth trying
            if 'Lyrics__Container' in response.text or 'lyrics' in response.text:
                print(f"  ✓ Page found but scraping complex (status {response.status_code})")
                print(f"     URL available: {genius_url}")
        else:
            print(f"  ✗ Status: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    # =============================================================================
    # 4. Musixmatch
    # =============================================================================
    print("\n[4/5] Attempting Musixmatch...")
    try:
        query = f"bryan-ferry-{track['title'].lower().replace(' ', '-')}"
        musix_url = f"https://www.musixmatch.com/lyrics/{query}"

        time.sleep(2)
        response = requests.get(musix_url, headers=headers, timeout=15)
        track_result["sources_tried"].append({
            "source": "Musixmatch",
            "url": musix_url,
            "status": response.status_code
        })

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            lyrics_spans = soup.find_all('span', class_=re.compile(r'lyrics'))
            if lyrics_spans:
                lyrics_text = '\n'.join([span.get_text() for span in lyrics_spans])
                if len(lyrics_text) > 50:
                    print(f"  ✓ SUCCESS! Extracted {len(lyrics_text)} characters")
                    track_result["lyrics"] = lyrics_text
                    track_result["lyrics_found"] = True
                    track_result["source"] = musix_url
        else:
            print(f"  ✗ Status: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    if track_result["lyrics_found"]:
        results["tracks"].append(track_result)
        continue

    # =============================================================================
    # 5. SongLyrics.com
    # =============================================================================
    print("\n[5/5] Attempting SongLyrics.com...")
    try:
        query = f"bryan-ferry/{track['title'].lower().replace(' ', '-')}"
        songlyrics_url = f"https://www.songlyrics.com/{query}-lyrics/"

        time.sleep(2)
        response = requests.get(songlyrics_url, headers=headers, timeout=15)
        track_result["sources_tried"].append({
            "source": "SongLyrics",
            "url": songlyrics_url,
            "status": response.status_code
        })

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            lyrics_div = soup.find('p', id='songLyricsDiv')
            if lyrics_div:
                lyrics_text = lyrics_div.get_text(separator='\n', strip=True)
                if len(lyrics_text) > 50:
                    print(f"  ✓ SUCCESS! Extracted {len(lyrics_text)} characters")
                    track_result["lyrics"] = lyrics_text
                    track_result["lyrics_found"] = True
                    track_result["source"] = songlyrics_url
        else:
            print(f"  ✗ Status: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    # Add to results
    results["tracks"].append(track_result)

    # Status for this track
    if track_result["lyrics_found"]:
        print(f"\n  ✓✓✓ TRACK {track['num']} COMPLETE: Lyrics extracted")
    else:
        print(f"\n  ✗✗✗ TRACK {track['num']} INCOMPLETE: No lyrics found")

    time.sleep(1)  # Be polite between tracks

# =============================================================================
# SAVE RESULTS
# =============================================================================
print("\n" + "="*80)
print("EXTRACTION COMPLETE")
print("="*80)

output_file = "/tmp/MEMORY_BUS_LYRICS_BY_TRACK_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Results saved to: {output_file}")

# Summary
tracks_with_lyrics = sum(1 for t in results["tracks"] if t["lyrics_found"])
print(f"\nSUMMARY:")
print(f"  Tracks with lyrics: {tracks_with_lyrics}/11")
print(f"  Tracks without lyrics: {11 - tracks_with_lyrics}/11")

if tracks_with_lyrics > 0:
    print(f"\n✓✓✓ SUCCESS: Found lyrics for {tracks_with_lyrics} tracks")
else:
    print(f"\n✗✗✗ NO LYRICS FOUND: Album too new - will need CD audio extraction + transcription")

print("\n" + "="*80)
