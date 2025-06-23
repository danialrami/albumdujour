#!/usr/bin/env python3
"""
Enhanced Music Library Website Builder
Reads from Google Sheets and generates a static website with embedded music players
Enhanced with timestamp-based categorization and optimized full-width responsive layout
"""

import gspread
import json
from pathlib import Path
from datetime import datetime
import re
from urllib.parse import urlparse, parse_qs
import shutil

class MusicSiteBuilder:
    def __init__(self):
        # Set up paths for local credential structure
        self.website_dir = Path(__file__).parent  # Current directory
        
        # Alternative credential paths (external to repo)
        self.alt_credentials_path = Path("/Users/danielramirez/Nextcloud/ore/Notes/Life/concrete-spider-446700-f9-4646496845d1.json")
        self.alt_apple_tokens_path = Path("/Users/danielramirez/Nextcloud/ore/Notes/Life/utilities/musickit")
        
        # Temporary credential paths (copied during build, never committed)
        self.temp_credentials_path = self.website_dir / 'temp_credentials.json'
        self.temp_apple_tokens_dir = self.website_dir / 'temp_musickit'
        
        # Output directory (build folder in website directory)
        self.output_dir = self.website_dir / "build"
        
        # Google Sheets info
        self.spreadsheet_name = "2025-media"
        self.worksheet_index = 0
        
        print(f"🗂️  Website directory: {self.website_dir}")
        print(f"🔑 Alternative credentials path: {self.alt_credentials_path}")
        print(f"🍎 Alternative Apple tokens path: {self.alt_apple_tokens_path}")
        
    def setup_temporary_credentials(self):
        """Copy credentials from alternative paths for build process"""
        print("🔑 Setting up temporary credentials...")
        
        # Copy Google Sheets credentials
        if self.alt_credentials_path.exists():
            shutil.copy2(self.alt_credentials_path, self.temp_credentials_path)
            print(f"✅ Copied Google Sheets credentials")
        else:
            raise FileNotFoundError(f"Google Sheets credentials not found at: {self.alt_credentials_path}")
        
        # Copy Apple Music tokens if they exist
        if self.alt_apple_tokens_path.exists():
            if self.temp_apple_tokens_dir.exists():
                shutil.rmtree(self.temp_apple_tokens_dir)
            shutil.copytree(self.alt_apple_tokens_path, self.temp_apple_tokens_dir)
            print(f"✅ Copied Apple Music tokens")
        else:
            print(f"⚠️  Apple Music tokens not found at: {self.alt_apple_tokens_path}")
    
    def cleanup_temporary_credentials(self):
        """Remove temporary credential files"""
        print("🧹 Cleaning up temporary credentials...")
        
        if self.temp_credentials_path.exists():
            self.temp_credentials_path.unlink()
            print("✅ Removed temporary Google Sheets credentials")
        
        if self.temp_apple_tokens_dir.exists():
            shutil.rmtree(self.temp_apple_tokens_dir)
            print("✅ Removed temporary Apple Music tokens")
        
    def setup_google_sheets(self):
        """Initialize Google Sheets connection"""
        print("🔗 Connecting to Google Sheets...")
        
        if not self.temp_credentials_path.exists():
            raise FileNotFoundError(f"Temporary credentials not found at: {self.temp_credentials_path}")
            
        gc = gspread.service_account(filename=str(self.temp_credentials_path))
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
        """Generate the main HTML file with simplified design"""
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
            <h1><img src="assets/favicon.svg" alt="Album du Jour" class="title-icon"> Album du Jour</h1>
            <p class="subtitle">🤖💕</p>
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
            <p>Built with 🩷</p>
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
        """Generate a collapsible section with full-width layout"""
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
        <section class="collapsible-section full-width-section" data-section="{section_id}">
            <button class="section-toggle" aria-expanded="false">
                <h2>{title} <span class="count">({len(albums)})</span></h2>
                <span class="toggle-icon">▼</span>
            </button>
            <div class="section-content">
                <div class="album-grid-fullwidth">
                    {album_cards}
                </div>
            </div>
        </section>
        """
    
    def generate_album_card_html(self, album, is_current=False):
        """Generate HTML for a single album card with optimized embed sizing"""
        # Determine which embed to show (prefer Spotify, fallback to Apple)
        embed_html = ""
        if is_current:
            # For current music (album du jour), show embeds prominently with exact container sizing
            if album['spotify_embed']:
                embed_html = f"""
                <div class="embed-container current-embed-container">
                    <iframe src="{album['spotify_embed']}" 
                            width="100%" 
                            height="450"
                            class="dynamic-embed current-embed spotify-embed" 
                            frameborder="0" 
                            allowtransparency="true" 
                            allow="encrypted-media"
                            title="Spotify - {album['album']}"
                            style="border-radius: 10px;"></iframe>
                </div>
                """
            elif album['apple_embed']:
                embed_html = f"""
                <div class="embed-container current-embed-container">
                    <iframe src="{album['apple_embed']}" 
                            width="100%" 
                            height="500"
                            class="dynamic-embed current-embed apple-embed" 
                            frameborder="0" 
                            allow="autoplay *; encrypted-media *; fullscreen *; clipboard-write" 
                            style="width:100%;max-width:660px;overflow:hidden;border-radius:10px;"
                            sandbox="allow-forms allow-popups allow-same-origin allow-scripts allow-storage-access-by-user-activation allow-top-navigation-by-user-activation"
                            title="Apple Music - {album['album']}"></iframe>
                </div>
                """
            else:
                embed_html = '<div class="embed-container current-embed-container"><p class="no-embed">No embed available</p></div>'
        else:
            # For other sections (Recently Added/Finished), use condensed vertical embeds
            if album['spotify_embed']:
                embed_html = f"""
                <div class="embed-container grid-embed-container">
                    <iframe data-src="{album['spotify_embed']}" 
                            width="100%" 
                            height="240"
                            class="dynamic-embed grid-embed spotify-embed lazy-embed" 
                            frameborder="0" 
                            allowtransparency="true" 
                            allow="encrypted-media"
                            title="Spotify - {album['album']}"
                            style="border-radius: 8px;"></iframe>
                </div>
                """
            elif album['apple_embed']:
                embed_html = f"""
                <div class="embed-container grid-embed-container">
                    <iframe data-src="{album['apple_embed']}" 
                            width="100%" 
                            height="280"
                            class="dynamic-embed grid-embed apple-embed lazy-embed" 
                            frameborder="0" 
                            allow="autoplay *; encrypted-media *" 
                            style="overflow: hidden; border-radius: 8px;"
                            title="Apple Music - {album['album']}"></iframe>
                </div>
                """
            else:
                embed_html = '<div class="embed-container grid-embed-container"><p class="no-embed">No embed available</p></div>'
        
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
        """Generate CSS with full-width layout and condensed embeds for Recently sections"""
        print("🎨 Generating CSS with full-width layout and optimized embed sizing...")
        
        css_content = """/* LUFS Brand Colors and Full-Width Responsive Design */
:root {
    /* LUFS Brand Colors */
    --lufs-teal: #78BEBA;
    --lufs-red: #D35233;
    --lufs-yellow: #E7B225;
    --lufs-blue: #2069af;
    --lufs-black: #111111;
    --lufs-white: #fbf9e2;
    
    /* Derived colors */
    --lufs-teal-alpha: rgba(120, 190, 186, 0.08);
    --lufs-red-alpha: rgba(211, 82, 51, 0.08);
    --lufs-yellow-alpha: rgba(231, 178, 37, 0.08);
    --lufs-blue-alpha: rgba(32, 105, 175, 0.08);
    
    /* Simplified gradients */
    --lufs-gradient: linear-gradient(135deg, var(--lufs-teal), var(--lufs-blue));
    
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

/* Simplified Animated Background */
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
        radial-gradient(circle at 25% 75%, var(--lufs-teal-alpha) 0%, transparent 40%),
        radial-gradient(circle at 75% 25%, var(--lufs-blue-alpha) 0%, transparent 40%),
        radial-gradient(circle at 50% 50%, var(--lufs-yellow-alpha) 0%, transparent 30%);
    animation: float 25s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { 
        transform: translate(0, 0) rotate(0deg); 
    }
    33% { 
        transform: translate(20px, -20px) rotate(120deg); 
    }
    66% { 
        transform: translate(-15px, 15px) rotate(240deg); 
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
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}

.title-icon {
    width: clamp(2rem, 4vw, 3rem);
    height: clamp(2rem, 4vw, 3rem);
    filter: drop-shadow(0 2px 8px rgba(120, 190, 186, 0.3));
}

.subtitle {
    font-size: 1.2rem;
    margin-bottom: 1rem;
    opacity: 0.8;
}

.generation-time {
    font-size: 0.9rem;
    opacity: 0.6;
    margin-bottom: 2rem;
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
    font-size: 0.85rem;
    font-weight: 600;
    border: 1px solid transparent;
}

.badge.current {
    background: var(--lufs-yellow);
    color: var(--lufs-black);
}

.badge.added {
    background: var(--lufs-blue);
    color: var(--lufs-white);
}

.badge.finished {
    background: var(--lufs-teal);
    color: var(--lufs-black);
}

.badge.total {
    background: transparent;
    border-color: var(--lufs-white);
    color: var(--lufs-white);
}

/* Currently Listening Section */
.currently-listening {
    margin-bottom: 4rem;
}

.currently-listening h2 {
    font-size: 2rem;
    margin-bottom: 2rem;
    text-align: center;
}

.album-du-jour {
    max-width: 700px;
    margin: 0 auto;
}

/* Current embed container - exact sizing to match embed */
.current-embed-container {
    width: 100%;
    max-width: 660px;
    margin: 1.5rem auto;
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    background: rgba(255, 255, 255, 0.05);
    /* Exact padding to match embed height */
    padding: 4px;
}

.current-embed-container iframe {
    width: 100%;
    display: block;
    border-radius: 8px;
}

/* Full-width sections for Recently Added/Finished */
.full-width-section {
    margin-left: calc(-50vw + 50%);
    margin-right: calc(-50vw + 50%);
    width: 100vw;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Collapsible Sections */
.collapsible-section {
    margin-bottom: 3rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--border-radius);
    background: rgba(255, 255, 255, 0.02);
    overflow: hidden;
}

.section-toggle {
    width: 100%;
    padding: 1.5rem 2rem;
    background: transparent;
    border: none;
    color: var(--lufs-white);
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1.1rem;
    transition: var(--transition);
}

.section-toggle:hover {
    background: rgba(255, 255, 255, 0.05);
}

.section-toggle h2 {
    margin: 0;
    font-size: 1.5rem;
}

.count {
    font-weight: normal;
    opacity: 0.7;
}

.toggle-icon {
    font-size: 1.2rem;
    transition: transform 0.3s ease;
}

.section-toggle[aria-expanded="true"] .toggle-icon {
    transform: rotate(180deg);
}

.section-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.5s ease;
}

.section-content.expanded {
    max-height: none;
    padding: 2rem;
}

/* Full-width Album Grid - 4 columns on desktop */
.album-grid-fullwidth {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
    margin-top: 1rem;
    max-width: none;
}

/* Album Cards */
.album-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--border-radius);
    padding: 1.2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: var(--transition);
}

.album-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
    border-color: rgba(120, 190, 186, 0.3);
}

.current-card {
    background: rgba(231, 178, 37, 0.1);
    border-color: var(--lufs-yellow);
}

.card-header {
    margin-bottom: 1rem;
}

.album-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.4rem;
    color: var(--lufs-white);
    line-height: 1.3;
}

.artist-name {
    font-size: 0.95rem;
    opacity: 0.8;
    margin-bottom: 0.4rem;
}

.card-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    opacity: 0.7;
}

/* Grid embed containers - condensed vertical, wider horizontal */
.grid-embed-container {
    width: 100%;
    margin: 0.8rem 0;
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    background: rgba(255, 255, 255, 0.03);
    padding: 3px;
}

.grid-embed-container iframe {
    width: 100%;
    display: block;
    border-radius: 6px;
}

.card-links {
    display: flex;
    gap: 0.6rem;
    margin-top: 0.8rem;
    flex-wrap: wrap;
}

.music-link {
    padding: 0.4rem 0.8rem;
    border-radius: 16px;
    text-decoration: none;
    font-size: 0.8rem;
    font-weight: 500;
    transition: var(--transition);
    border: 1px solid transparent;
}

.music-link.apple {
    background: var(--lufs-red);
    color: var(--lufs-white);
}

.music-link.spotify {
    background: var(--lufs-teal);
    color: var(--lufs-black);
}

.music-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* Empty sections */
.empty-section {
    text-align: center;
    padding: 3rem 2rem;
    opacity: 0.6;
}

/* Footer */
.site-footer {
    text-align: center;
    margin-top: 4rem;
    padding: 2rem 0;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.sheets-link {
    display: inline-block;
    padding: 0.75rem 1.5rem;
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
    box-shadow: 0 8px 24px rgba(120, 190, 186, 0.3);
}

/* Responsive Design */
@media (max-width: 1200px) {
    .album-grid-fullwidth {
        grid-template-columns: repeat(3, 1fr);
    }
}

@media (max-width: 900px) {
    .album-grid-fullwidth {
        grid-template-columns: repeat(2, 1fr);
        gap: 1.2rem;
    }
    
    .full-width-section {
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
}

@media (max-width: 768px) {
    :root {
        --container-padding: 1rem;
    }
    
    .album-grid-fullwidth {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .full-width-section {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .current-embed-container {
        margin: 1rem auto;
        padding: 3px;
    }
    
    .grid-embed-container {
        padding: 2px;
    }
    
    .section-toggle {
        padding: 1rem 1.5rem;
    }
    
    .section-content.expanded {
        padding: 1.5rem;
    }
    
    .stats-badges {
        gap: 0.5rem;
    }
    
    .badge {
        padding: 0.4rem 0.8rem;
        font-size: 0.8rem;
    }
}

/* Lazy loading placeholder */
.lazy-embed[data-src] {
    background: rgba(255, 255, 255, 0.05);
    display: flex;
    align-items: center;
    justify-content: center;
}

.lazy-embed[data-src]::before {
    content: "Loading...";
    color: rgba(255, 255, 255, 0.5);
}

/* No embed fallback */
.no-embed {
    text-align: center;
    padding: 1.5rem;
    opacity: 0.5;
    font-style: italic;
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
    .animated-background::before {
        animation: none;
    }
    
    * {
        transition: none !important;
    }
}

/* Focus styles for accessibility */
.section-toggle:focus,
.music-link:focus,
.sheets-link:focus {
    outline: 2px solid var(--lufs-teal);
    outline-offset: 2px;
}
"""
        
        output_file = self.output_dir / "styles.css"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print(f"✅ CSS generated: {output_file}")
    
    def generate_javascript(self):
        """Generate JavaScript for collapsible sections and lazy loading"""
        print("⚡ Generating JavaScript...")
        
        js_content = """// Album du Jour - Enhanced Interactions
document.addEventListener('DOMContentLoaded', function() {
    initializeCollapsibleSections();
    initializeLazyLoading();
    initializeAccessibility();
});

function initializeCollapsibleSections() {
    const toggles = document.querySelectorAll('.section-toggle');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const section = this.closest('.collapsible-section');
            const content = section.querySelector('.section-content');
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            // Toggle state
            this.setAttribute('aria-expanded', !isExpanded);
            
            if (!isExpanded) {
                content.classList.add('expanded');
                content.style.maxHeight = content.scrollHeight + 'px';
                
                // Save state
                localStorage.setItem(`section-${section.dataset.section}`, 'expanded');
                
                // Load lazy embeds when section is expanded
                loadLazyEmbedsInSection(section);
            } else {
                content.classList.remove('expanded');
                content.style.maxHeight = '0';
                
                // Save state
                localStorage.setItem(`section-${section.dataset.section}`, 'collapsed');
            }
        });
        
        // Restore saved state
        const section = toggle.closest('.collapsible-section');
        const savedState = localStorage.getItem(`section-${section.dataset.section}`);
        
        if (savedState === 'expanded') {
            // Simulate click to expand
            setTimeout(() => toggle.click(), 100);
        }
    });
}

function initializeLazyLoading() {
    // Load embeds that are currently visible
    loadVisibleEmbeds();
    
    // Set up intersection observer for lazy loading
    if ('IntersectionObserver' in window) {
        const embedObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    loadEmbed(entry.target);
                    embedObserver.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '50px'
        });
        
        // Observe all lazy embeds
        document.querySelectorAll('.lazy-embed[data-src]').forEach(embed => {
            embedObserver.observe(embed);
        });
    } else {
        // Fallback for browsers without IntersectionObserver
        document.querySelectorAll('.lazy-embed[data-src]').forEach(loadEmbed);
    }
}

function loadVisibleEmbeds() {
    // Load embeds in currently visible sections (like Currently Listening)
    document.querySelectorAll('.currently-listening .lazy-embed[data-src]').forEach(loadEmbed);
}

function loadLazyEmbedsInSection(section) {
    // Load all lazy embeds in a specific section
    section.querySelectorAll('.lazy-embed[data-src]').forEach(loadEmbed);
}

function loadEmbed(embed) {
    const src = embed.getAttribute('data-src');
    if (src) {
        embed.src = src;
        embed.removeAttribute('data-src');
        embed.classList.remove('lazy-embed');
    }
}

function initializeAccessibility() {
    // Add keyboard navigation for collapsible sections
    document.querySelectorAll('.section-toggle').forEach(toggle => {
        toggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    // Add focus management
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });
    
    document.addEventListener('mousedown', function() {
        document.body.classList.remove('keyboard-navigation');
    });
}

// Utility function to handle window resize
window.addEventListener('resize', debounce(function() {
    // Recalculate expanded section heights
    document.querySelectorAll('.section-content.expanded').forEach(content => {
        content.style.maxHeight = content.scrollHeight + 'px';
    });
}, 250));

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
"""
        
        output_file = self.output_dir / "scripts.js"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"✅ JavaScript generated: {output_file}")
    
    def build(self):
        """Main build process"""
        try:
            print("🚀 Starting Album du Jour website build...")
            
            # Setup temporary credentials
            self.setup_temporary_credentials()
            
            # Connect to Google Sheets
            sheet = self.setup_google_sheets()
            
            # Fetch and process data
            music_data = self.fetch_music_data(sheet)
            categorized_data = self.categorize_albums(music_data)
            
            # Create output directory and copy assets
            self.create_output_directory()
            
            # Generate website files
            self.generate_html(categorized_data)
            self.generate_css()
            self.generate_javascript()
            
            print("🎉 Album du Jour website build completed successfully!")
            print(f"📁 Output directory: {self.output_dir}")
            print(f"🌐 Open: file://{self.output_dir.absolute()}/index.html")
            
        except Exception as e:
            print(f"❌ Build failed: {str(e)}")
            raise
        finally:
            # Always cleanup temporary credentials
            self.cleanup_temporary_credentials()

if __name__ == "__main__":
    builder = MusicSiteBuilder()
    builder.build()

