#!/usr/bin/env python3
"""
Enhanced Music Library Website Builder
Reads from Google Sheets and generates a static website with embedded music players
Enhanced with timestamp-based categorization and improved design
"""

import gspread
import json
from pathlib import Path
from datetime import datetime
import re
from urllib.parse import urlparse, parse_qs

class MusicSiteBuilder:
    def __init__(self):
        # Set up paths for local credential structure
        self.website_dir = Path(__file__).parent  # Current directory
        
        # Paths to credentials and tokens (now in current directory)
        self.credentials_path = self.website_dir / 'concrete-spider-446700-f9-4646496845d1.json'
        self.apple_token_dir = self.website_dir / 'musickit'
        
        # Output directory (build folder in website directory)
        self.output_dir = self.website_dir / "build"
        
        # Google Sheets info
        self.spreadsheet_name = "2025-media"
        self.worksheet_index = 0
        
        print(f"🗂️  Website directory: {self.website_dir}")
        print(f"🔑 Credentials path: {self.credentials_path}")
        print(f"🍎 Apple tokens dir: {self.apple_token_dir}")
        
    def setup_google_sheets(self):
        """Initialize Google Sheets connection"""
        print("🔗 Connecting to Google Sheets...")
        
        if not self.credentials_path.exists():
            raise FileNotFoundError(f"Google Sheets credentials not found at: {self.credentials_path}")
            
        gc = gspread.service_account(filename=str(self.credentials_path))
        spreadsheet = gc.open(self.spreadsheet_name)
        sheet = spreadsheet.get_worksheet(self.worksheet_index)
        return sheet
    
    def parse_timestamp(self, timestamp_str):
        """Parse timestamp, ignore placeholders like '20XX-XX-XXTXX:XX:XXZ'"""
        if not timestamp_str or 'XX' in timestamp_str or timestamp_str.strip() == '':
            return None
        try:
            # Handle both with and without 'Z' suffix
            if timestamp_str.endswith('Z'):
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                return datetime.fromisoformat(timestamp_str)
        except:
            return None
    
    def fetch_music_data(self, sheet):
        """Fetch and process music data from the sheet"""
        print("📊 Fetching music data...")
        records = sheet.get_all_records()
        
        music_data = []
        for i, record in enumerate(records):
            # Get all the fields
            apple_link = record.get('Apple Music Link', '').strip()
            spotify_link = record.get('Spotify Link', '').strip()
            
            # Skip entries without any links
            if not apple_link and not spotify_link:
                continue
                
            music_entry = record.get('Music', '').strip()
            if not music_entry:
                continue
                
            # Parse album and artist
            album, artist = self.parse_album_artist(music_entry)
            
            # Parse timestamps
            date_added = self.parse_timestamp(record.get('Date Added', '').strip())
            date_finished = self.parse_timestamp(record.get('Date Finished', '').strip())
            
            entry = {
                'id': i + 1,
                'album': album,
                'artist': artist,
                'apple_link': apple_link,
                'spotify_link': spotify_link,
                'status': record.get('Status', 'Open').strip(),
                'date_added': date_added,
                'date_finished': date_finished,
                'date_added_raw': record.get('Date Added', '').strip(),
                'date_finished_raw': record.get('Date Finished', '').strip(),
                'rating': record.get('🌞', '').strip()
            }
            
            # Generate embed URLs
            entry['apple_embed'] = self.get_apple_embed_url(apple_link)
            entry['spotify_embed'] = self.get_spotify_embed_url(spotify_link)
            
            music_data.append(entry)
        
        print(f"✅ Processed {len(music_data)} music entries")
        return music_data
    
    def categorize_albums(self, music_data):
        """Categorize albums based on status and timestamps"""
        print("📂 Categorizing albums...")
        
        current_listening = []
        recently_added = []
        recently_finished = []
        
        for entry in music_data:
            # Currently Listening: Status = "Current"
            if entry['status'].lower() == 'current':
                current_listening.append(entry)
            # Recently Finished: Has a valid date_finished timestamp
            elif entry['date_finished'] is not None:
                recently_finished.append(entry)
            # Recently Added: Has a valid date_added timestamp
            elif entry['date_added'] is not None:
                recently_added.append(entry)
        
        # Sort by timestamps (newest first)
        recently_added.sort(key=lambda x: x['date_added'], reverse=True)
        recently_finished.sort(key=lambda x: x['date_finished'], reverse=True)
        
        # Limit to 20 albums each for Recently Added and Recently Finished
        recently_added = recently_added[:20]
        recently_finished = recently_finished[:20]
        
        categorized = {
            'current_listening': current_listening,
            'recently_added': recently_added,
            'recently_finished': recently_finished
        }
        
        print(f"📊 Categorization complete:")
        print(f"   🎧 Currently Listening: {len(current_listening)}")
        print(f"   📀 Recently Added: {len(recently_added)}")
        print(f"   ✅ Recently Finished: {len(recently_finished)}")
        
        return categorized
    
    def parse_album_artist(self, music_entry):
        """Parse 'Album - Artist' format to separate components"""
        # Handle both regular hyphen (-) and em dash (–)
        if ' – ' in music_entry:  # Em dash (from Apple Music)
            parts = music_entry.rsplit(' – ', 1)
            return parts[0].strip(), parts[1].strip()
        elif ' - ' in music_entry:  # Regular hyphen
            parts = music_entry.rsplit(' - ', 1)
            return parts[0].strip(), parts[1].strip()
        return music_entry.strip(), "Unknown Artist"
    
    def get_apple_embed_url(self, apple_link):
        """Convert Apple Music URL to embeddable format"""
        if not apple_link or not apple_link.startswith('https://music.apple.com'):
            return None
        return apple_link.replace('music.apple.com', 'embed.music.apple.com')
    
    def get_spotify_embed_url(self, spotify_link):
        """Convert Spotify URL to embeddable format"""
        if not spotify_link or not spotify_link.startswith('https://open.spotify.com'):
            return None
        
        try:
            # Extract album/track ID from URL
            # URL format: https://open.spotify.com/album/4yP0hdKOZPNshxUOjY0cZj
            parts = spotify_link.split('/')
            if len(parts) >= 5:
                content_type = parts[3]  # album, track, playlist, etc.
                content_id = parts[4].split('?')[0]  # Remove query parameters
                return f"https://open.spotify.com/embed/{content_type}/{content_id}?utm_source=generator"
        except:
            pass
        return None
    
    def create_output_directory(self):
        """Create output directory structure"""
        print("📁 Creating output directory...")
        self.output_dir.mkdir(exist_ok=True)
        assets_dir = self.output_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Copy assets if they exist in the website directory
        source_assets = self.website_dir / "assets"
        if source_assets.exists():
            import shutil
            for asset_file in source_assets.glob("*"):
                if asset_file.is_file():
                    shutil.copy2(asset_file, assets_dir / asset_file.name)
                    print(f"📋 Copied asset: {asset_file.name}")
        else:
            print("⚠️  No assets directory found, skipping asset copy")
    
    def format_date_display(self, date_obj):
        """Format date for display"""
        if date_obj is None:
            return ""
        try:
            return date_obj.strftime('%b %d, %Y')
        except:
            return ""
    
    def generate_html(self, categorized_data):
        """Generate the main HTML file with enhanced design"""
        print("🎨 Generating HTML...")
        
        current_listening = categorized_data['current_listening']
        recently_added = categorized_data['recently_added']
        recently_finished = categorized_data['recently_finished']
        
        total_albums = len(current_listening) + len(recently_added) + len(recently_finished)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Album du Jour - Music Discovery</title>
    <meta name="description" content="Personal music library showcase featuring currently listening, recently added, and recently finished albums.">
    <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="animated-background"></div>
    <div class="container">
        <header class="site-header">
            <h1>🎵 Album du Jour</h1>
            <p class="subtitle">Personal Music Discovery</p>
            <p class="generation-time">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <div class="stats-badges">
                <span class="badge current">{len(current_listening)} Current</span>
                <span class="badge added">{len(recently_added)} Recently Added</span>
                <span class="badge finished">{len(recently_finished)} Recently Finished</span>
                <span class="badge total">{total_albums} Total</span>
            </div>
        </header>
        
        <main class="content">
            {self.generate_currently_listening_section(current_listening)}
            {self.generate_collapsible_section("recently-added", "📀 Recently Added", recently_added)}
            {self.generate_collapsible_section("recently-finished", "✅ Recently Finished", recently_finished)}
        </main>
        
        <footer class="site-footer">
            <a href="https://docs.google.com/spreadsheets/d/1p8zTsGuQVV81tvuZswIHq-pIXCyZn9ixhg-2HWD9X10/edit?gid=0#gid=0" 
               target="_blank" class="sheets-link">
                📊 View Full Library
            </a>
            <p>Built with ❤️ by <strong>LUFS Audio</strong></p>
        </footer>
    </div>
    
    <script src="scripts.js"></script>
</body>
</html>"""
        
        output_file = self.output_dir / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML generated: {output_file}")
    
    def generate_currently_listening_section(self, current_albums):
        """Generate the Currently Listening section (always visible)"""
        if not current_albums:
            return f"""
            <section class="currently-listening">
                <h2>🎧 Currently Listening</h2>
                <div class="empty-section">
                    <p>No album currently being listened to.</p>
                    <p class="subtitle">The album du jour will appear here when selected.</p>
                </div>
            </section>
            """
        
        # Take the first current album as the "album du jour"
        album = current_albums[0]
        
        return f"""
        <section class="currently-listening">
            <h2>🎧 Currently Listening</h2>
            <div class="album-du-jour">
                {self.generate_album_card_html(album, is_current=True)}
            </div>
        </section>
        """
    
    def generate_collapsible_section(self, section_id, title, albums):
        """Generate a collapsible section"""
        if not albums:
            return f"""
            <section class="collapsible-section" data-section="{section_id}">
                <button class="section-toggle" aria-expanded="false">
                    <h2>{title}</h2>
                    <span class="toggle-icon">▼</span>
                </button>
                <div class="section-content">
                    <div class="empty-section">
                        <p>No albums in this section yet.</p>
                    </div>
                </div>
            </section>
            """
        
        album_cards = ""
        for album in albums:
            album_cards += self.generate_album_card_html(album, is_current=False)
        
        return f"""
        <section class="collapsible-section" data-section="{section_id}">
            <button class="section-toggle" aria-expanded="false">
                <h2>{title} <span class="count">({len(albums)})</span></h2>
                <span class="toggle-icon">▼</span>
            </button>
            <div class="section-content">
                <div class="album-grid">
                    {album_cards}
                </div>
            </div>
        </section>
        """
    
    def generate_album_card_html(self, album, is_current=False):
        """Generate HTML for a single album card"""
        # Determine which embed to show (prefer Spotify, fallback to Apple)
        embed_html = ""
        if is_current:
            # For current music, show embeds prominently
            if album['spotify_embed']:
                embed_html = f"""
                <div class="embed-container">
                    <iframe src="{album['spotify_embed']}" 
                            width="100%" height="380" frameborder="0" 
                            allowtransparency="true" allow="encrypted-media"
                            title="Spotify - {album['album']}"
                            style="border-radius: 10px;"></iframe>
                </div>
                """
            elif album['apple_embed']:
                embed_html = f"""
                <div class="embed-container">
                    <iframe src="{album['apple_embed']}" 
                            width="100%" height="450" frameborder="0" 
                            allow="autoplay *; encrypted-media *; fullscreen *; clipboard-write" 
                            style="width:100%;max-width:660px;overflow:hidden;border-radius:10px;"
                            sandbox="allow-forms allow-popups allow-same-origin allow-scripts allow-storage-access-by-user-activation allow-top-navigation-by-user-activation"
                            title="Apple Music - {album['album']}"></iframe>
                </div>
                """
            else:
                embed_html = '<div class="embed-container"><p class="no-embed">No embed available</p></div>'
        else:
            # For other sections, use smaller embeds
            if album['spotify_embed']:
                embed_html = f"""
                <div class="embed-container">
                    <iframe data-src="{album['spotify_embed']}" 
                            width="100%" height="152" frameborder="0" 
                            allowtransparency="true" allow="encrypted-media"
                            title="Spotify - {album['album']}"
                            style="border-radius: 10px;" class="lazy-embed"></iframe>
                </div>
                """
            elif album['apple_embed']:
                embed_html = f"""
                <div class="embed-container">
                    <iframe data-src="{album['apple_embed']}" 
                            width="100%" height="175" frameborder="0" 
                            allow="autoplay *; encrypted-media *" 
                            style="overflow: hidden; border-radius: 10px;"
                            title="Apple Music - {album['album']}" class="lazy-embed"></iframe>
                </div>
                """
            else:
                embed_html = '<div class="embed-container"><p class="no-embed">No embed available</p></div>'
        
        # Build links
        links_html = ""
        if album['apple_link']:
            links_html += f'<a href="{album["apple_link"]}" target="_blank" class="music-link apple">🍎 Apple Music</a>'
        if album['spotify_link']:
            links_html += f'<a href="{album["spotify_link"]}" target="_blank" class="music-link spotify">🎵 Spotify</a>'
        
        # Format dates
        date_display = ""
        if album['date_added']:
            date_display = f'<span class="date">Added: {self.format_date_display(album["date_added"])}</span>'
        elif album['date_finished']:
            date_display = f'<span class="date">Finished: {self.format_date_display(album["date_finished"])}</span>'
        
        rating_display = f'<span class="rating">{album["rating"]}</span>' if album['rating'] else ""
        
        # Add special styling class for current music
        card_class = "album-card current-card" if is_current else "album-card"
        
        return f"""
        <div class="{card_class}" data-status="{album['status'].lower()}">
            <div class="card-header">
                <h3 class="album-title">{album['album']}</h3>
                <p class="artist-name">{album['artist']}</p>
                <div class="card-meta">
                    {date_display}
                    {rating_display}
                </div>
            </div>
            
            {embed_html}
            
            <div class="card-links">
                {links_html}
            </div>
        </div>
        """
    
    def generate_css(self):
        """Generate the enhanced CSS file with LUFS branding"""
        print("🎨 Generating enhanced CSS...")
        
        css_content = """/* LUFS Brand Colors and Enhanced Design */
:root {
    /* LUFS Brand Colors */
    --lufs-teal: #78BEBA;
    --lufs-red: #D35233;
    --lufs-yellow: #E7B225;
    --lufs-blue: #2069af;
    --lufs-black: #111111;
    --lufs-white: #fbf9e2;
    
    /* Derived colors */
    --lufs-teal-alpha: rgba(120, 190, 186, 0.1);
    --lufs-red-alpha: rgba(211, 82, 51, 0.1);
    --lufs-yellow-alpha: rgba(231, 178, 37, 0.1);
    --lufs-blue-alpha: rgba(32, 105, 175, 0.1);
    
    /* Gradients */
    --lufs-gradient: linear-gradient(135deg, var(--lufs-teal), var(--lufs-blue));
    --lufs-border-gradient: linear-gradient(90deg, var(--lufs-teal), var(--lufs-yellow), var(--lufs-red), var(--lufs-blue));
    
    /* Layout */
    --container-max-width: 1400px;
    --container-padding: 2rem;
    --border-radius: 12px;
    --transition: all 0.3s ease;
}

/* Reset and base styles */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    background-color: var(--lufs-black);
    color: var(--lufs-white);
    line-height: 1.6;
    overflow-x: hidden;
}

/* Animated Background */
.animated-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    background: var(--lufs-black);
    overflow: hidden;
}

.animated-background::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: 
        radial-gradient(circle at 20% 80%, var(--lufs-teal-alpha) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, var(--lufs-red-alpha) 0%, transparent 50%),
        radial-gradient(circle at 40% 40%, var(--lufs-yellow-alpha) 0%, transparent 50%),
        radial-gradient(circle at 60% 60%, var(--lufs-blue-alpha) 0%, transparent 50%);
    animation: float 20s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { 
        transform: translate(0, 0) rotate(0deg); 
    }
    25% { 
        transform: translate(30px, -30px) rotate(90deg); 
    }
    50% { 
        transform: translate(-20px, 20px) rotate(180deg); 
    }
    75% { 
        transform: translate(20px, -10px) rotate(270deg); 
    }
}

/* Container */
.container {
    max-width: var(--container-max-width);
    margin: 0 auto;
    padding: var(--container-padding);
    position: relative;
    z-index: 1;
}

/* Header */
.site-header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 2rem 0;
}

.site-header h1 {
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 700;
    background: var(--lufs-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}

.subtitle {
    color: var(--lufs-teal);
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.generation-time {
    color: rgba(251, 249, 226, 0.7);
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

.stats-badges {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.badge {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9rem;
    transition: var(--transition);
}

.badge:hover {
    transform: translateY(-2px);
}

.badge.current { 
    background-color: var(--lufs-yellow); 
    color: var(--lufs-black); 
}

.badge.added { 
    background-color: var(--lufs-blue); 
    color: var(--lufs-white); 
}

.badge.finished { 
    background-color: var(--lufs-teal); 
    color: var(--lufs-black); 
}

.badge.total { 
    background-color: rgba(251, 249, 226, 0.2); 
    color: var(--lufs-white); 
    border: 1px solid var(--lufs-white);
}

/* Currently Listening Section */
.currently-listening {
    margin-bottom: 3rem;
}

.currently-listening h2 {
    font-size: 2rem;
    margin-bottom: 1.5rem;
    text-align: center;
    color: var(--lufs-white);
}

.album-du-jour {
    display: flex;
    justify-content: center;
}

.album-du-jour .album-card {
    max-width: 600px;
    width: 100%;
    background: var(--lufs-gradient);
    border: 3px solid var(--lufs-yellow);
    box-shadow: 
        0 0 30px rgba(231, 178, 37, 0.3),
        0 10px 40px rgba(0, 0, 0, 0.3);
    transform: scale(1.02);
}

/* Collapsible Sections */
.collapsible-section {
    margin-bottom: 2rem;
    border-radius: var(--border-radius);
    overflow: hidden;
    background: rgba(251, 249, 226, 0.05);
    border: 1px solid rgba(251, 249, 226, 0.1);
}

.section-toggle {
    width: 100%;
    background: transparent;
    border: none;
    padding: 1.5rem;
    color: var(--lufs-white);
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1rem;
    transition: var(--transition);
    min-height: 44px; /* Touch-friendly */
}

.section-toggle:hover {
    background: rgba(251, 249, 226, 0.1);
}

.section-toggle h2 {
    font-size: 1.5rem;
    font-weight: 600;
}

.count {
    color: var(--lufs-teal);
    font-weight: 400;
}

.toggle-icon {
    font-size: 1.2rem;
    transition: transform 0.3s ease;
    color: var(--lufs-teal);
}

.section-toggle[aria-expanded="true"] .toggle-icon {
    transform: rotate(180deg);
}

.section-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

.section-toggle[aria-expanded="true"] + .section-content {
    max-height: none;
}

/* Album Grid */
.album-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    padding: 1.5rem;
}

/* Album Cards */
.album-card {
    background: rgba(251, 249, 226, 0.05);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    border: 1px solid transparent;
    background-image: var(--lufs-border-gradient);
    background-origin: border-box;
    background-clip: padding-box, border-box;
    transition: var(--transition);
    position: relative;
    overflow: hidden;
}

.album-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(17, 17, 17, 0.8);
    z-index: -1;
}

.album-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(120, 190, 186, 0.2);
}

.card-header {
    margin-bottom: 1rem;
}

.album-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--lufs-white);
    margin-bottom: 0.25rem;
    line-height: 1.3;
}

.artist-name {
    color: var(--lufs-teal);
    font-size: 1rem;
    margin-bottom: 0.5rem;
}

.card-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.85rem;
    color: rgba(251, 249, 226, 0.7);
}

.date {
    color: var(--lufs-yellow);
}

.rating {
    color: var(--lufs-yellow);
}

/* Embed Container */
.embed-container {
    margin: 1rem 0;
    border-radius: var(--border-radius);
    overflow: hidden;
    background: rgba(0, 0, 0, 0.3);
}

.embed-container iframe {
    width: 100%;
    border: none;
    border-radius: var(--border-radius);
}

.no-embed {
    text-align: center;
    color: rgba(251, 249, 226, 0.5);
    padding: 2rem;
    font-style: italic;
}

/* Music Links */
.card-links {
    display: flex;
    gap: 0.75rem;
    margin-top: 1rem;
}

.music-link {
    flex: 1;
    padding: 0.75rem;
    border-radius: 8px;
    text-decoration: none;
    text-align: center;
    font-weight: 600;
    font-size: 0.9rem;
    transition: var(--transition);
    border: 2px solid transparent;
}

.music-link.apple {
    background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
    color: white;
}

.music-link.spotify {
    background: linear-gradient(135deg, #1db954, #1ed760);
    color: white;
}

.music-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* Empty Section */
.empty-section {
    text-align: center;
    padding: 3rem 1.5rem;
    color: rgba(251, 249, 226, 0.6);
}

.empty-section p {
    margin-bottom: 0.5rem;
}

.empty-section .subtitle {
    font-size: 0.9rem;
    color: rgba(251, 249, 226, 0.4);
}

/* Footer */
.site-footer {
    text-align: center;
    margin-top: 4rem;
    padding: 2rem 0;
    border-top: 1px solid rgba(251, 249, 226, 0.1);
}

.sheets-link {
    display: inline-block;
    padding: 1rem 2rem;
    background: var(--lufs-gradient);
    color: var(--lufs-white);
    text-decoration: none;
    border-radius: 25px;
    font-weight: 600;
    margin-bottom: 1rem;
    transition: var(--transition);
}

.sheets-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(120, 190, 186, 0.3);
}

.site-footer p {
    color: rgba(251, 249, 226, 0.7);
    font-size: 0.9rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    :root {
        --container-padding: 1rem;
    }
    
    .album-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
        padding: 1rem;
    }
    
    .stats-badges {
        gap: 0.5rem;
    }
    
    .badge {
        font-size: 0.8rem;
        padding: 0.4rem 0.8rem;
    }
    
    .card-links {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .section-toggle {
        padding: 1rem;
    }
    
    .section-toggle h2 {
        font-size: 1.2rem;
    }
}

@media (max-width: 480px) {
    .site-header {
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    .album-card {
        padding: 1rem;
    }
    
    .embed-container iframe {
        height: 120px !important;
    }
    
    .album-du-jour .embed-container iframe {
        height: 300px !important;
    }
}

/* Touch device optimizations */
@media (hover: none) {
    .album-card:hover {
        transform: none;
    }
    
    .album-card:active {
        transform: scale(0.98);
    }
    
    .music-link:hover {
        transform: none;
    }
    
    .music-link:active {
        transform: scale(0.95);
    }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    :root {
        --lufs-white: #ffffff;
        --lufs-black: #000000;
    }
    
    .album-card {
        border: 2px solid var(--lufs-white);
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
    
    .animated-background::before {
        animation: none;
    }
}
"""
        
        output_file = self.output_dir / "styles.css"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print(f"✅ CSS generated: {output_file}")
    
    def generate_javascript(self):
        """Generate JavaScript for interactions"""
        print("⚡ Generating JavaScript...")
        
        js_content = """// Album du Jour - Interactive Functionality
class AlbumSections {
    constructor() {
        this.initializeCollapsibleSections();
        this.initializeLazyLoading();
        this.initializeAccessibility();
    }
    
    initializeCollapsibleSections() {
        const toggleButtons = document.querySelectorAll('.section-toggle');
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.toggleSection(e.currentTarget);
            });
        });
        
        // Restore saved states
        this.restoreSectionStates();
    }
    
    toggleSection(button) {
        const section = button.closest('.collapsible-section');
        const content = section.querySelector('.section-content');
        const icon = section.querySelector('.toggle-icon');
        const isExpanded = button.getAttribute('aria-expanded') === 'true';
        
        // Toggle expanded state
        button.setAttribute('aria-expanded', !isExpanded);
        
        if (!isExpanded) {
            // Expanding
            content.style.maxHeight = content.scrollHeight + 'px';
            icon.style.transform = 'rotate(180deg)';
            
            // Load any lazy embeds in this section
            this.loadLazyEmbedsInSection(section);
        } else {
            // Collapsing
            content.style.maxHeight = '0';
            icon.style.transform = 'rotate(0deg)';
        }
        
        // Save state to localStorage
        localStorage.setItem(`section-${section.dataset.section}`, !isExpanded);
    }
    
    restoreSectionStates() {
        const sections = document.querySelectorAll('.collapsible-section');
        sections.forEach(section => {
            const savedState = localStorage.getItem(`section-${section.dataset.section}`);
            if (savedState === 'true') {
                const button = section.querySelector('.section-toggle');
                // Delay to ensure DOM is ready
                setTimeout(() => {
                    this.toggleSection(button);
                }, 100);
            }
        });
    }
    
    initializeLazyLoading() {
        // Intersection Observer for lazy loading embeds
        const embedObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadEmbed(entry.target);
                    embedObserver.unobserve(entry.target);
                }
            });
        }, { 
            rootMargin: '100px',
            threshold: 0.1
        });
        
        // Observe all lazy embeds
        document.querySelectorAll('.lazy-embed').forEach(iframe => {
            embedObserver.observe(iframe);
        });
    }
    
    loadEmbed(iframe) {
        if (iframe.dataset.src) {
            iframe.src = iframe.dataset.src;
            iframe.removeAttribute('data-src');
            iframe.classList.remove('lazy-embed');
            
            // Add loading indicator
            iframe.style.opacity = '0';
            iframe.addEventListener('load', () => {
                iframe.style.transition = 'opacity 0.3s ease';
                iframe.style.opacity = '1';
            });
        }
    }
    
    loadLazyEmbedsInSection(section) {
        const lazyEmbeds = section.querySelectorAll('.lazy-embed');
        lazyEmbeds.forEach(iframe => {
            this.loadEmbed(iframe);
        });
    }
    
    initializeAccessibility() {
        // Keyboard navigation for collapsible sections
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                if (e.target.classList.contains('section-toggle')) {
                    e.preventDefault();
                    this.toggleSection(e.target);
                }
            }
        });
        
        // Focus management
        const toggleButtons = document.querySelectorAll('.section-toggle');
        toggleButtons.forEach(button => {
            button.addEventListener('focus', () => {
                button.style.outline = '2px solid var(--lufs-teal)';
                button.style.outlineOffset = '2px';
            });
            
            button.addEventListener('blur', () => {
                button.style.outline = 'none';
            });
        });
    }
}

// Smooth scrolling for anchor links
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Performance monitoring
function initializePerformanceMonitoring() {
    // Log page load time
    window.addEventListener('load', () => {
        const loadTime = performance.now();
        console.log(`Album du Jour loaded in ${Math.round(loadTime)}ms`);
        
        // Track largest contentful paint
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                console.log(`LCP: ${Math.round(lastEntry.startTime)}ms`);
            });
            observer.observe({ entryTypes: ['largest-contentful-paint'] });
        }
    });
}

// Error handling for embeds
function initializeEmbedErrorHandling() {
    document.addEventListener('error', (e) => {
        if (e.target.tagName === 'IFRAME') {
            const iframe = e.target;
            const container = iframe.closest('.embed-container');
            if (container) {
                container.innerHTML = '<p class="no-embed">Embed failed to load</p>';
            }
        }
    }, true);
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎵 Album du Jour - Initializing...');
    
    try {
        new AlbumSections();
        initializeSmoothScrolling();
        initializePerformanceMonitoring();
        initializeEmbedErrorHandling();
        
        console.log('✅ Album du Jour - Initialized successfully');
    } catch (error) {
        console.error('❌ Album du Jour - Initialization error:', error);
    }
});

// Service worker registration for offline support (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Only register if service worker file exists
        fetch('/sw.js', { method: 'HEAD' })
            .then(() => {
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => {
                        console.log('SW registered: ', registration);
                    })
                    .catch(registrationError => {
                        console.log('SW registration failed: ', registrationError);
                    });
            })
            .catch(() => {
                // Service worker file doesn't exist, skip registration
            });
    });
}
"""
        
        output_file = self.output_dir / "scripts.js"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"✅ JavaScript generated: {output_file}")
    
    def generate_build_readme(self):
        """Generate README for build folder"""
        print("📝 Generating build README...")
        
        readme_content = f"""# Album du Jour - Build Files

This directory contains the generated static website files for Album du Jour.

## Generated Files

- `index.html` - Main website page with enhanced design
- `styles.css` - Stylesheet with LUFS branding and responsive design
- `scripts.js` - Interactive functionality for collapsible sections
- `assets/` - Images and static assets including custom favicon
- `favicon.svg` - Custom Album du Jour vinyl record favicon

## Features

### Content Organization
- **Currently Listening**: Prominently displayed "album du jour"
- **Recently Added**: Last 20 albums added (collapsible)
- **Recently Finished**: Last 20 albums completed (collapsible)

### Design Features
- LUFS brand colors and animated background
- Responsive design for all devices
- Collapsible sections with localStorage persistence
- Lazy loading for music embeds
- Accessibility features and keyboard navigation

### Music Integration
- Apple Music and Spotify embeds
- Direct links to music services
- Optimized embed sizes for different sections

## Deployment

These files are ready for deployment to any static hosting service:

- **Netlify**: Drag and drop this folder
- **Vercel**: Connect to Git repository
- **GitHub Pages**: Push to gh-pages branch
- **Traditional hosting**: Upload via FTP/SFTP

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Progressive enhancement for older browsers

## Performance

- Optimized for fast loading
- Lazy loading for embeds
- Minimal JavaScript footprint
- Responsive images and assets

---

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Source:** Album du Jour Enhanced Build System  
**Version:** 2.0  
"""
        
        output_file = self.output_dir / "README.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✅ Build README generated: {output_file}")
    
    def run(self):
        """Main execution method"""
        try:
            print("🚀 Starting Album du Jour Enhanced Build Process...")
            
            # Setup and data fetching
            sheet = self.setup_google_sheets()
            music_data = self.fetch_music_data(sheet)
            categorized_data = self.categorize_albums(music_data)
            
            # Create output and generate files
            self.create_output_directory()
            self.generate_html(categorized_data)
            self.generate_css()
            self.generate_javascript()
            self.generate_build_readme()
            
            print("🎉 Album du Jour Enhanced Build Complete!")
            print(f"📁 Output directory: {self.output_dir}")
            print(f"🌐 Open {self.output_dir}/index.html to view the site")
            
        except Exception as e:
            print(f"❌ Build failed: {str(e)}")
            raise

if __name__ == "__main__":
    builder = MusicSiteBuilder()
    builder.run()

