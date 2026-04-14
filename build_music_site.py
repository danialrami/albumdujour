#!/usr/bin/env python3
"""
Enhanced Music Library Website Builder
Reads from Google Sheets and generates a static website with embedded music players
Enhanced with timestamp-based categorization, edge case handling, and compact responsive embeds
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
        self.script_dir = self.website_dir  # For template files (retro_styles.css, retro_scripts.js)
        
        # Local credential paths (stored in repo but gitignored for security)
        self.alt_credentials_path = self.website_dir / "concrete-spider-446700-f9-4646496845d1.json"
        self.alt_apple_tokens_path = Path("/mnt/barracuda/Nextcloud/ore/Notes/Life/utilities/musickit")
        
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
    
    def find_most_recent_album(self, music_data):
        """Find the most recently timestamped album as fallback for current listening"""
        all_timestamped = []
        
        for entry in music_data:
            # Collect all albums with valid timestamps
            if entry['date_added'] is not None:
                all_timestamped.append((entry, entry['date_added'], 'added'))
            if entry['date_finished'] is not None:
                all_timestamped.append((entry, entry['date_finished'], 'finished'))
        
        if not all_timestamped:
            return None, None
        
        # Sort by timestamp (newest first) and return the most recent
        all_timestamped.sort(key=lambda x: x[1], reverse=True)
        most_recent_entry, most_recent_timestamp, timestamp_type = all_timestamped[0]
        
        print(f"🔄 No current albums found. Using most recent: {most_recent_entry['album']} ({timestamp_type}: {most_recent_timestamp.strftime('%b %d, %Y')})")
        
        return most_recent_entry, timestamp_type
    
    def categorize_albums(self, music_data):
        """Categorize albums based on status and timestamps with edge case handling"""
        print("📂 Categorizing albums...")
        
        current_listening = []
        recently_added = []
        recently_finished = []
        fallback_album = None
        fallback_type = None
        
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
        
        # Edge case: If no current albums, find the most recent one as fallback
        if not current_listening:
            fallback_album, fallback_type = self.find_most_recent_album(music_data)
            if fallback_album:
                current_listening = [fallback_album]
                # Remove the fallback album from its original category to avoid duplication
                if fallback_type == 'added' and fallback_album in recently_added:
                    recently_added.remove(fallback_album)
                elif fallback_type == 'finished' and fallback_album in recently_finished:
                    recently_finished.remove(fallback_album)
        
        # Sort by timestamps (newest first)
        recently_added.sort(key=lambda x: x['date_added'], reverse=True)
        recently_finished.sort(key=lambda x: x['date_finished'], reverse=True)
        
        # Limit to 20 albums each for Recently Added and Recently Finished
        recently_added = recently_added[:20]
        recently_finished = recently_finished[:20]
        
        categorized = {
            'current_listening': current_listening,
            'recently_added': recently_added,
            'recently_finished': recently_finished,
            'is_fallback': fallback_album is not None,
            'fallback_type': fallback_type
        }
        
        print(f"📊 Categorization complete:")
        print(f"   🎧 Currently Listening: {len(current_listening)} {'(fallback)' if fallback_album else ''}")
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
        """Generate the main HTML file with retro style"""
        print("🎨 Generating HTML...")
        
        current_listening = categorized_data['current_listening']
        recently_added = categorized_data['recently_added']
        recently_finished = categorized_data['recently_finished']
        is_fallback = categorized_data['is_fallback']
        
        total_albums = len(current_listening) + len(recently_added) + len(recently_finished)
        
        # Read favicon SVG for use in headers
        favicon_svg = ""
        try:
            favicon_path = self.website_dir / "assets" / "favicon.svg"
            if favicon_path.exists():
                with open(favicon_path, 'r') as f:
                    favicon_svg = f.read().strip()
        except:
            pass
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Album du Jour - Music Discovery</title>
    <meta name="description" content="Personal music library showcase featuring currently listening, recently added, and recently finished albums.">
    <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Host+Grotesk:wght@400;500;600;700&family=Public+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <!-- Sticky Header -->
    <div class="sticky-header" id="sticky-header">
        <div class="header-content">
            <a href="#top" class="logo-link" id="logo-top">
                <div class="logo">{favicon_svg}</div>
            </a>
            <div class="header-text">
                <h1>Album du Jour</h1>
                <p>LUFS Audio</p>
            </div>
        </div>
    </div>

    <!-- Animated Background -->
    <div class="animated-background" id="animated-background"></div>

    <div class="container">
        <!-- Main Header -->
        <div class="main-header" id="top">
            <div class="header-content">
                <div class="logo-section">
                    <a href="#top" class="logo-link">
                        <div class="logo">{favicon_svg}</div>
                    </a>
                    <div class="header-text">
                        <h1>Album du Jour</h1>
                        <p>Music Discovery</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Stats Section -->
        <div class="stats-section">
            <div class="stats-badges">
                <span class="badge current">{len(current_listening)} Current</span>
                <span class="badge added">{len(recently_added)} Recently Added</span>
                <span class="badge finished">{len(recently_finished)} Recently Finished</span>
                <span class="badge total">{total_albums} Total</span>
            </div>
            <p class="generation-time">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>

        <!-- Main Content -->
        <main class="content">
            {self.generate_currently_listening_section(current_listening, is_fallback)}
            {self.generate_collapsible_section("recently-added", "📀 Recently Added", recently_added)}
            {self.generate_collapsible_section("recently-finished", "✅ Recently Finished", recently_finished)}
        </main>

        <!-- Retro Buttons Section -->
        <div class="retro-buttons">
            <div class="buttons-container">
                <a href="https://docs.google.com/spreadsheets/d/1p8zTsGuQVV81tvuZswIHq-pIXCyZn9ixhg-2HWD9X10/edit?gid=0#gid=0" 
                   target="_blank" class="webring-button library-button">
                    📊 View Full Library
                </a>
            </div>
        </div>

        <div class="footer">
            <p>&copy; <span id="current-year"></span> LUFS Audio — Built with 🩷</p>
        </div>
    </div>
    
    <script src="scripts.js"></script>
</body>
</html>"""
        
        output_file = self.output_dir / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML generated: {output_file}")
    
    def generate_currently_listening_section(self, current_albums, is_fallback=False):
        """Generate the Currently Listening section with clean titles"""
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
        
        # Determine section title based on whether it's a fallback
        section_title = "🎵 Latest Album" if is_fallback else "🎧 Currently Listening"
        
        return f"""
        <section class="currently-listening">
            <h2>{section_title}</h2>
            <div class="album-du-jour">
                {self.generate_album_card_html(album, is_current=True)}
            </div>
        </section>
        """
    
    def generate_collapsible_section(self, section_id, title, albums):
        """Generate a collapsible section with horizontal carousel layout"""
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
            album_cards += self.generate_album_card_html(album, is_current=False, section=section_id)
        
        return f"""
        <section class="collapsible-section" data-section="{section_id}">
            <button class="section-toggle" aria-expanded="false">
                <h2>{title} <span class="count">({len(albums)})</span></h2>
                <span class="toggle-icon">▼</span>
            </button>
            <div class="section-content">
                <div class="album-carousel">
                    {album_cards}
                </div>
            </div>
        </section>
        """
    
    def generate_album_card_html(self, album, is_current=False, section=None):
        """Generate HTML for a single album card with Apple Music embeds only"""
        # Apple Music only - Spotify deprecated as of Feb 2026 (requires Premium for Developer Mode API)
        embed_html = ""
        if is_current:
            # For current music (album du jour), show embeds prominently
            if album['apple_embed']:
                embed_html = f"""
                <div class="embed-container current-embed-container">
                    <iframe src="{album['apple_embed']}" 
                            width="100%" 
                            height="450"
                            class="dynamic-embed current-embed apple-embed" 
                            frameborder="0" 
                            allow="autoplay *; encrypted-media *; fullscreen *; clipboard-write" 
                            style="width:100%;max-width:660px;overflow:hidden;border-radius:0;"
                            sandbox="allow-forms allow-popups allow-same-origin allow-scripts allow-storage-access-by-user-activation allow-top-navigation-by-user-activation"
                            title="Apple Music - {album['album']}"></iframe>
                </div>
                """
            else:
                embed_html = '<div class="embed-container current-embed-container"><p class="no-embed">No embed available</p></div>'
        else:
            # For other sections (Recently Added/Finished), use only links (no embeds for cleaner look)
            embed_html = ""
        
        # Build links - Apple Music only (Spotify deprecated)
        links_html = ""
        if album['apple_link']:
            links_html += f'<a href="{album["apple_link"]}" target="_blank" class="music-link apple">🍎 Apple Music</a>'
        # Spotify links retained in sheet for reference but no longer displayed or used
        
        # Format dates - show appropriate date based on section context
        date_display = ""
        if section == 'recently-finished' and album['date_finished']:
            date_display = f'<span class="date">Finished: {self.format_date_display(album["date_finished"])}</span>'
        elif section == 'recently-added' and album['date_added']:
            date_display = f'<span class="date">Added: {self.format_date_display(album["date_added"])}</span>'
        elif album['date_added']:
            date_display = f'<span class="date">Added: {self.format_date_display(album["date_added"])}</span>'
        elif album['date_finished']:
            date_display = f'<span class="date">Finished: {self.format_date_display(album["date_finished"])}</span>'
        
        rating_display = f'<span class="rating">{album["rating"]}</span>' if album['rating'] else ""
        
        # Add special styling class for current music
        card_class = "album-card current-card" if is_current else "album-card compact-card"
        
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
        """Generate CSS with retro brutalist styling"""
        print("🎨 Generating CSS with retro brutalist styling...")
        
        # Read CSS from template file
        template_path = self.script_dir / "retro_styles.css"
        
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            print(f"📄 Read retro styles from {template_path}")
        else:
            raise FileNotFoundError(f"CSS template not found: {template_path}")
        
        output_file = self.output_dir / "styles.css"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print(f"✅ CSS generated: {output_file}")
    
    def generate_javascript(self):
        """Generate JavaScript with retro brutalist styling"""
        print("⚡ Generating JavaScript with retro brutalist styling...")
        
        # Read JS from template file
        template_path = self.script_dir / "retro_scripts.js"
        
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                js_content = f.read()
            print(f"📄 Read retro scripts from {template_path}")
        else:
            raise FileNotFoundError(f"JS template not found: {template_path}")
        
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


