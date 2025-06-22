#!/usr/bin/env python3
"""
Music Library Website Builder
Reads from Google Sheets and generates a static website with embedded music players
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
        self.website_dir = Path(__file__).parent  # Current directory (v3)
        
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
            
            entry = {
                'id': i + 1,
                'album': album,
                'artist': artist,
                'apple_link': apple_link,
                'spotify_link': spotify_link,
                'status': record.get('Status', 'Open').strip(),
                'date_added': record.get('Date Added', '').strip(),
                'date_finished': record.get('Date Finished', '').strip(),
                'rating': record.get('🌞', '').strip()
            }
            
            # Generate embed URLs
            entry['apple_embed'] = self.get_apple_embed_url(apple_link)
            entry['spotify_embed'] = self.get_spotify_embed_url(spotify_link)
            
            music_data.append(entry)
        
        print(f"✅ Processed {len(music_data)} music entries")
        return music_data
    
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
    
    def generate_html(self, music_data):
        """Generate the main HTML file"""
        print("🎨 Generating HTML...")
        
        # Group data by status for better organization
        current_music = [m for m in music_data if m['status'] == 'Current']
        open_music = [m for m in music_data if m['status'] == 'Open']
        done_music = [m for m in music_data if m['status'] == 'Done']
        
        # Sort by date added (newest first)
        current_music.sort(key=lambda x: x['date_added'], reverse=True)
        open_music.sort(key=lambda x: x['date_added'], reverse=True)
        done_music.sort(key=lambda x: x['date_added'], reverse=True)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Album du Jour - Music Library</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="icon" href="assets/lufs-LOGO-04.png" />
</head>
<body>
    <div class="lufs-container">
        <header class="lufs-header">
            <h1>🎵 Album du Jour</h1>
            <p class="lufs-subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <div class="lufs-stats">
                <span class="stat-badge current">{len(current_music)} Current</span>
                <span class="stat-badge open">{len(open_music)} Open</span>
                <span class="stat-badge done">{len(done_music)} Done</span>
                <span class="stat-badge total">{len(music_data)} Total</span>
            </div>
        </header>

        <main class="lufs-main">
            {self.generate_section_html("🎧 Currently Listening", current_music, "current")}
            {self.generate_section_html("📖 Up Next", open_music[:20], "open")}  
            {self.generate_section_html("✅ Recently Finished", done_music[:20], "done")}
        </main>

        <footer class="lufs-footer">
            <div class="lufs-logo-container">
                <img src="assets/lufs-LOGO-04.png" alt="LUFS Logo" class="lufs-logo" />
            </div>
            <p>Album du Jour • Built with ❤️</p>
        </footer>
    </div>

    <script src="scripts.js"></script>
</body>
</html>"""
        
        output_file = self.output_dir / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML generated: {output_file}")
    
    def generate_section_html(self, title, music_list, section_class):
        """Generate HTML for a section of music"""
        if not music_list:
            return f"""
            <section class="lufs-section {section_class}">
                <h2>{title}</h2>
                <p class="empty-section">No music in this section yet.</p>
            </section>
            """
        
        music_cards = ""
        for music in music_list:
            music_cards += self.generate_music_card_html(music)
        
        return f"""
        <section class="lufs-section {section_class}">
            <h2>{title}</h2>
            <div class="music-grid">
                {music_cards}
            </div>
        </section>
        """
    
    def generate_music_card_html(self, music):
        """Generate HTML for a single music card"""
        # For "Currently Listening" section, always show embeds prominently
        is_current = music['status'] == 'Current'
        
        # Debug: Print what we have for current music
        if is_current:
            print(f"🎧 Current music debug:")
            print(f"  Album: {music['album']}")
            print(f"  Apple link: {music['apple_link']}")
            print(f"  Spotify link: {music['spotify_link']}")
            print(f"  Apple embed: {music['apple_embed']}")
            print(f"  Spotify embed: {music['spotify_embed']}")
        
        # Determine which embed to show (prefer Spotify, fallback to Apple)
        embed_html = ""
        if is_current:
            # For current music, show embeds prominently
            if music['spotify_embed']:
                embed_html = f"""
                <iframe src="{music['spotify_embed']}" 
                        width="100%" height="380" frameborder="0" 
                        allowtransparency="true" allow="encrypted-media"
                        title="Spotify - {music['album']}"
                        style="border-radius: 10px;"></iframe>
                """
                print(f"  ✅ Using Spotify embed: {music['spotify_embed']}")
            elif music['apple_embed']:
                embed_html = f"""
                <iframe src="{music['apple_embed']}" 
                        width="100%" height="450" frameborder="0" 
                        allow="autoplay *; encrypted-media *; fullscreen *; clipboard-write" 
                        style="width:100%;max-width:660px;overflow:hidden;border-radius:10px;"
                        sandbox="allow-forms allow-popups allow-same-origin allow-scripts allow-storage-access-by-user-activation allow-top-navigation-by-user-activation"
                        title="Apple Music - {music['album']}"></iframe>
                """
                print(f"  ✅ Using Apple embed: {music['apple_embed']}")
            else:
                print(f"  ⚠️  No embeds available for current music")
        else:
            # For other sections, use smaller embeds or no embeds
            if music['spotify_embed']:
                embed_html = f"""
                <iframe src="{music['spotify_embed']}" 
                        width="100%" height="152" frameborder="0" 
                        allowtransparency="true" allow="encrypted-media"
                        title="Spotify - {music['album']}"
                        style="border-radius: 10px;"></iframe>
                """
            elif music['apple_embed']:
                embed_html = f"""
                <iframe src="{music['apple_embed']}" 
                        width="100%" height="175" frameborder="0" 
                        allow="autoplay *; encrypted-media *" 
                        style="overflow: hidden; border-radius: 10px;"
                        title="Apple Music - {music['album']}"></iframe>
                """
        
        # Build links
        links_html = ""
        if music['apple_link']:
            links_html += f'<a href="{music["apple_link"]}" target="_blank" class="music-link apple">🍎 Apple Music</a>'
        if music['spotify_link']:
            links_html += f'<a href="{music["spotify_link"]}" target="_blank" class="music-link spotify">🎵 Spotify</a>'
        
        # Format date
        date_display = ""
        if music['date_added']:
            try:
                # Parse ISO date and format nicely
                date_obj = datetime.fromisoformat(music['date_added'].replace('Z', '+00:00'))
                date_display = date_obj.strftime('%b %d, %Y')
            except:
                date_display = music['date_added'][:10]  # Just take the date part
        
        rating_display = music['rating'] if music['rating'] else ""
        
        # Add special styling class for current music
        card_class = f"music-card {music['status'].lower()}-card" if is_current else "music-card"
        
        return f"""
        <div class="{card_class}" data-status="{music['status'].lower()}">
            <div class="card-header">
                <h3 class="album-title">{music['album']}</h3>
                <p class="artist-name">{music['artist']}</p>
                <div class="card-meta">
                    {f'<span class="date">{date_display}</span>' if date_display else ''}
                    {f'<span class="rating">{rating_display}</span>' if rating_display else ''}
                </div>
            </div>
            
            {f'<div class="embed-container">{embed_html}</div>' if embed_html else '<div class="embed-container"><p style="text-align:center;color:var(--lufs-light-gray);padding:20px;">No embed available</p></div>'}
            
            <div class="card-links">
                {links_html}
            </div>
        </div>
        """
    
    def generate_css(self):
        """Generate the CSS file"""
        print("🎨 Generating CSS...")
        
        css_content = """/* LUFS Color Palette */
:root {
    --lufs-teal: #78BEBA;
    --lufs-red: #D35233;
    --lufs-yellow: #E7B225;
    --lufs-blue: #2C5AA0;
    --lufs-white: #FFFFFF;
    --lufs-off-white: #E0E0E0;
    --lufs-light-gray: #B0B0B0;
    --lufs-dark-gray: #333333;
    --lufs-darker-gray: #222222;
    --lufs-almost-black: #121212;
    --lufs-black: #000000;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Host Grotesk', Public Sans, Inter, Manrope, sans-serif;
    background-color: var(--lufs-almost-black);
    color: var(--lufs-off-white);
    line-height: 1.6;
}

.lufs-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 40px 20px;
}

/* Header */
.lufs-header {
    text-align: center;
    margin-bottom: 50px;
}

.lufs-header h1 {
    color: var(--lufs-blue);
    font-size: 3rem;
    margin-bottom: 10px;
    font-weight: 700;
}

.lufs-subtitle {
    color: var(--lufs-teal);
    font-size: 1.1rem;
    margin-bottom: 20px;
}

.lufs-stats {
    display: flex;
    justify-content: center;
    gap: 15px;
    flex-wrap: wrap;
}

.stat-badge {
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9rem;
}

.stat-badge.current { background-color: var(--lufs-yellow); color: var(--lufs-almost-black); }
.stat-badge.open { background-color: var(--lufs-blue); color: var(--lufs-white); }
.stat-badge.done { background-color: var(--lufs-teal); color: var(--lufs-almost-black); }
.stat-badge.total { background-color: var(--lufs-dark-gray); color: var(--lufs-off-white); }

/* Sections */
.lufs-section {
    margin-bottom: 60px;
}

.lufs-section h2 {
    color: var(--lufs-white);
    font-size: 2rem;
    margin-bottom: 30px;
    font-weight: 600;
}

.empty-section {
    text-align: center;
    color: var(--lufs-light-gray);
    font-style: italic;
    padding: 40px;
}

/* Music Grid */
.music-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 30px;
}

/* Special grid for currently listening section */
.lufs-section.current .music-grid {
    grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
    gap: 40px;
}

/* Music Cards */
.music-card {
    background-color: var(--lufs-darker-gray);
    border-radius: 16px;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: 1px solid var(--lufs-dark-gray);
}

.music-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

/* Special styling for current music cards */
.current-card {
    background-color: var(--lufs-darker-gray);
    border: 2px solid var(--lufs-yellow);
    box-shadow: 0 5px 20px rgba(231, 178, 37, 0.2);
}

.current-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 40px rgba(231, 178, 37, 0.3);
}

.card-header {
    padding: 20px 20px 15px;
}

.album-title {
    color: var(--lufs-white);
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 5px;
    line-height: 1.3;
}

.current-card .album-title {
    font-size: 1.4rem;
    color: var(--lufs-yellow);
}

.artist-name {
    color: var(--lufs-teal);
    font-size: 1rem;
    font-weight: 500;
    margin-bottom: 10px;
}

.current-card .artist-name {
    font-size: 1.1rem;
}

.card-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
    color: var(--lufs-light-gray);
}

.rating {
    font-size: 1rem;
}

.embed-container {
    margin: 0;
}

.embed-container iframe {
    width: 100%;
    border: none;
    background-color: var(--lufs-dark-gray);
}

.card-links {
    padding: 15px 20px 20px;
    display: flex;
    gap: 10px;
}

.music-link {
    flex: 1;
    text-align: center;
    padding: 10px 15px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.2s ease;
}

.music-link.apple {
    background-color: var(--lufs-red);
    color: var(--lufs-white);
    border: 1px solid var(--lufs-red);
}

.music-link.spotify {
    background-color: #1DB954;
    color: var(--lufs-white);
}

.music-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.music-link.apple:hover {
    background-color: #e85a42;
}

.music-link.spotify:hover {
    background-color: #1ed760;
}

/* Footer */
.lufs-footer {
    text-align: center;
    margin-top: 80px;
    padding-top: 40px;
    border-top: 1px solid var(--lufs-dark-gray);
    color: var(--lufs-light-gray);
}

.lufs-logo-container {
    margin-bottom: 15px;
    opacity: 0.6;
}

.lufs-logo {
    width: 40px;
    height: auto;
}

/* Mobile Responsive */
@media (max-width: 768px) {
    .lufs-container {
        padding: 30px 15px;
    }
    
    .lufs-header h1 {
        font-size: 2.5rem;
    }
    
    .music-grid {
        grid-template-columns: 1fr;
        gap: 20px;
    }
    
    .lufs-section.current .music-grid {
        grid-template-columns: 1fr;
        gap: 30px;
    }
    
    .lufs-stats {
        gap: 10px;
    }
    
    .stat-badge {
        font-size: 0.8rem;
        padding: 6px 12px;
    }
}

@media (max-width: 480px) {
    .card-links {
        flex-direction: column;
    }
    
    .music-link {
        margin-bottom: 5px;
    }
}
"""
        
        output_file = self.output_dir / "styles.css"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print(f"✅ CSS generated: {output_file}")
    
    def generate_js(self):
        """Generate the JavaScript file"""
        print("🎨 Generating JavaScript...")
        
        js_content = """// Music Library Website JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎵 Music Library loaded');
    
    // Add any interactive functionality here
    // For now, this is mainly for future enhancements
    
    // Smooth scrolling for any internal links
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
    
    // Add loading states for iframes
    const iframes = document.querySelectorAll('iframe');
    iframes.forEach(iframe => {
        iframe.addEventListener('load', function() {
            this.style.opacity = '1';
        });
        iframe.style.opacity = '0.8';
        iframe.style.transition = 'opacity 0.3s ease';
    });
});
"""
        
        output_file = self.output_dir / "scripts.js"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"✅ JavaScript generated: {output_file}")
    
    def build(self):
        """Main build process"""
        print("🚀 Starting Music Library website build...\n")
        
        try:
            # Setup
            sheet = self.setup_google_sheets()
            music_data = self.fetch_music_data(sheet)
            
            # Create output structure
            self.create_output_directory()
            
            # Generate files
            self.generate_html(music_data)
            self.generate_css()
            self.generate_js()
            
            print(f"\n🎉 Build complete! Generated website in: {self.output_dir}")
            print(f"📂 Open {self.output_dir / 'index.html'} in your browser")
            
        except Exception as e:
            print(f"\n❌ Build failed: {str(e)}")
            raise

def main():
    builder = MusicSiteBuilder()
    builder.build()

if __name__ == "__main__":
    main()

    
    def fetch_music_data(self, sheet):
        """Fetch and process music data from the sheet"""
        print("📊 Fetching music data...")
        records = sheet.get_all_records()
        
        music_data = []
        for i, record in enumerate(records):
            # Skip entries without both Apple Music and Spotify links
            apple_link = record.get('Apple Music Link', '').strip()
            spotify_link = record.get('Spotify Link', '').strip()
            
            if not apple_link and not spotify_link:
                continue
                
            music_entry = record.get('Music', '').strip()
            if not music_entry:
                continue
                
            # Parse album and artist
            album, artist = self.parse_album_artist(music_entry)
            
            entry = {
                'id': i + 1,
                'album': album,
                'artist': artist,
                'apple_link': apple_link,
                'spotify_link': spotify_link,
                'status': record.get('Status', 'Open').strip(),
                'date_added': record.get('Date Added', '').strip(),
                'date_finished': record.get('Date Finished', '').strip(),
                'rating': record.get('🌞', '').strip()
            }
            
            # Generate embed URLs
            entry['apple_embed'] = self.get_apple_embed_url(apple_link)
            entry['spotify_embed'] = self.get_spotify_embed_url(spotify_link)
            
            music_data.append(entry)
        
        print(f"✅ Processed {len(music_data)} music entries")
        return music_data
    
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
        
        # Copy assets if they exist
        source_assets = Path("./assets")
        if source_assets.exists():
            import shutil
            for asset_file in source_assets.glob("*"):
                if asset_file.is_file():
                    shutil.copy2(asset_file, assets_dir / asset_file.name)
    
    def generate_html(self, music_data):
        """Generate the main HTML file"""
        print("🎨 Generating HTML...")
        
        # Group data by status for better organization
        current_music = [m for m in music_data if m['status'] == 'Current']
        open_music = [m for m in music_data if m['status'] == 'Open']
        done_music = [m for m in music_data if m['status'] == 'Done']
        
        # Sort by date added (newest first)
        current_music.sort(key=lambda x: x['date_added'], reverse=True)
        open_music.sort(key=lambda x: x['date_added'], reverse=True)
        done_music.sort(key=lambda x: x['date_added'], reverse=True)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Music Library - Album du Jour</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="icon" href="assets/lufs-LOGO-04.png" />
</head>
<body>
    <div class="lufs-container">
        <header class="lufs-header">
            <h1>🎵 Music Library</h1>
            <p class="lufs-subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <div class="lufs-stats">
                <span class="stat-badge current">{len(current_music)} Current</span>
                <span class="stat-badge open">{len(open_music)} Open</span>
                <span class="stat-badge done">{len(done_music)} Done</span>
                <span class="stat-badge total">{len(music_data)} Total</span>
            </div>
        </header>

        <main class="lufs-main">
            {self.generate_section_html("🎧 Currently Listening", current_music, "current")}
            {self.generate_section_html("📖 Up Next", open_music[:20], "open")}  
            {self.generate_section_html("✅ Recently Finished", done_music[:20], "done")}
        </main>

        <footer class="lufs-footer">
            <div class="lufs-logo-container">
                <img src="assets/lufs-LOGO-04.png" alt="LUFS Logo" class="lufs-logo" />
            </div>
            <p>Music Library • Built with ❤️</p>
        </footer>
    </div>

    <script src="scripts.js"></script>
</body>
</html>"""
        
        output_file = self.output_dir / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML generated: {output_file}")
    
    def generate_section_html(self, title, music_list, section_class):
        """Generate HTML for a section of music"""
        if not music_list:
            return f"""
            <section class="lufs-section {section_class}">
                <h2>{title}</h2>
                <p class="empty-section">No music in this section yet.</p>
            </section>
            """
        
        music_cards = ""
        for music in music_list:
            music_cards += self.generate_music_card_html(music)
        
        return f"""
        <section class="lufs-section {section_class}">
            <h2>{title}</h2>
            <div class="music-grid">
                {music_cards}
            </div>
        </section>
        """
    
    def generate_music_card_html(self, music):
        """Generate HTML for a single music card"""
        # Determine which embed to show (prefer Spotify, fallback to Apple)
        embed_html = ""
        if music['spotify_embed']:
            embed_html = f"""
            <iframe src="{music['spotify_embed']}" 
                    width="100%" height="152" frameborder="0" 
                    allowtransparency="true" allow="encrypted-media"
                    title="Spotify - {music['album']}"></iframe>
            """
        elif music['apple_embed']:
            embed_html = f"""
            <iframe src="{music['apple_embed']}" 
                    width="100%" height="175" frameborder="0" 
                    allow="autoplay *; encrypted-media *" 
                    style="overflow: hidden;"
                    title="Apple Music - {music['album']}"></iframe>
            """
        
        # Build links
        links_html = ""
        if music['apple_link']:
            links_html += f'<a href="{music["apple_link"]}" target="_blank" class="music-link apple">🍎 Apple Music</a>'
        if music['spotify_link']:
            links_html += f'<a href="{music["spotify_link"]}" target="_blank" class="music-link spotify">🎵 Spotify</a>'
        
        # Format date
        date_display = ""
        if music['date_added']:
            try:
                # Parse ISO date and format nicely
                date_obj = datetime.fromisoformat(music['date_added'].replace('Z', '+00:00'))
                date_display = date_obj.strftime('%b %d, %Y')
            except:
                date_display = music['date_added'][:10]  # Just take the date part
        
        rating_display = music['rating'] if music['rating'] else ""
        
        return f"""
        <div class="music-card" data-status="{music['status'].lower()}">
            <div class="card-header">
                <h3 class="album-title">{music['album']}</h3>
                <p class="artist-name">{music['artist']}</p>
                <div class="card-meta">
                    {f'<span class="date">{date_display}</span>' if date_display else ''}
                    {f'<span class="rating">{rating_display}</span>' if rating_display else ''}
                </div>
            </div>
            
            {f'<div class="embed-container">{embed_html}</div>' if embed_html else ''}
            
            <div class="card-links">
                {links_html}
            </div>
        </div>
        """
    
    def generate_css(self):
        """Generate the CSS file"""
        print("🎨 Generating CSS...")
        
        css_content = """/* LUFS Color Palette */
:root {
    --lufs-teal: #78BEBA;
    --lufs-red: #D35233;
    --lufs-yellow: #E7B225;
    --lufs-blue: #2C5AA0;
    --lufs-white: #FFFFFF;
    --lufs-off-white: #E0E0E0;
    --lufs-light-gray: #B0B0B0;
    --lufs-dark-gray: #333333;
    --lufs-darker-gray: #222222;
    --lufs-almost-black: #121212;
    --lufs-black: #000000;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background-color: var(--lufs-almost-black);
    color: var(--lufs-off-white);
    line-height: 1.6;
}

.lufs-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 40px 20px;
}

/* Header */
.lufs-header {
    text-align: center;
    margin-bottom: 50px;
}

.lufs-header h1 {
    color: var(--lufs-blue);
    font-size: 3rem;
    margin-bottom: 10px;
    font-weight: 700;
}

.lufs-subtitle {
    color: var(--lufs-teal);
    font-size: 1.1rem;
    margin-bottom: 20px;
}

.lufs-stats {
    display: flex;
    justify-content: center;
    gap: 15px;
    flex-wrap: wrap;
}

.stat-badge {
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9rem;
}

.stat-badge.current { background-color: var(--lufs-yellow); color: var(--lufs-almost-black); }
.stat-badge.open { background-color: var(--lufs-blue); color: var(--lufs-white); }
.stat-badge.done { background-color: var(--lufs-teal); color: var(--lufs-almost-black); }
.stat-badge.total { background-color: var(--lufs-dark-gray); color: var(--lufs-off-white); }

/* Sections */
.lufs-section {
    margin-bottom: 60px;
}

.lufs-section h2 {
    color: var(--lufs-white);
    font-size: 2rem;
    margin-bottom: 30px;
    font-weight: 600;
}

.empty-section {
    text-align: center;
    color: var(--lufs-light-gray);
    font-style: italic;
    padding: 40px;
}

/* Music Grid */
.music-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 30px;
}

/* Music Cards */
.music-card {
    background-color: var(--lufs-darker-gray);
    border-radius: 16px;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: 1px solid var(--lufs-dark-gray);
}

.music-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.card-header {
    padding: 20px 20px 15px;
}

.album-title {
    color: var(--lufs-white);
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 5px;
    line-height: 1.3;
}

.artist-name {
    color: var(--lufs-teal);
    font-size: 1rem;
    font-weight: 500;
    margin-bottom: 10px;
}

.card-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
    color: var(--lufs-light-gray);
}

.rating {
    font-size: 1rem;
}

.embed-container {
    margin: 0;
}

.embed-container iframe {
    width: 100%;
    border: none;
    background-color: var(--lufs-dark-gray);
}

.card-links {
    padding: 15px 20px 20px;
    display: flex;
    gap: 10px;
}

.music-link {
    flex: 1;
    text-align: center;
    padding: 10px 15px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.2s ease;
}

.music-link.apple {
    background-color: var(--lufs-dark-gray);
    color: var(--lufs-white);
    border: 1px solid var(--lufs-light-gray);
}

.music-link.spotify {
    background-color: #1DB954;
    color: var(--lufs-white);
}

.music-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.music-link.apple:hover {
    background-color: var(--lufs-light-gray);
    color: var(--lufs-almost-black);
}

.music-link.spotify:hover {
    background-color: #1ed760;
}

/* Footer */
.lufs-footer {
    text-align: center;
    margin-top: 80px;
    padding-top: 40px;
    border-top: 1px solid var(--lufs-dark-gray);
    color: var(--lufs-light-gray);
}

.lufs-logo-container {
    margin-bottom: 15px;
    opacity: 0.6;
}

.lufs-logo {
    width: 40px;
    height: auto;
}

/* Mobile Responsive */
@media (max-width: 768px) {
    .lufs-container {
        padding: 30px 15px;
    }
    
    .lufs-header h1 {
        font-size: 2.5rem;
    }
    
    .music-grid {
        grid-template-columns: 1fr;
        gap: 20px;
    }
    
    .lufs-stats {
        gap: 10px;
    }
    
    .stat-badge {
        font-size: 0.8rem;
        padding: 6px 12px;
    }
}

@media (max-width: 480px) {
    .card-links {
        flex-direction: column;
    }
    
    .music-link {
        margin-bottom: 5px;
    }
}
"""
        
        output_file = self.output_dir / "styles.css"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print(f"✅ CSS generated: {output_file}")
    
    def generate_js(self):
        """Generate the JavaScript file"""
        print("🎨 Generating JavaScript...")
        
        js_content = """// Music Library Website JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎵 Music Library loaded');
    
    // Add any interactive functionality here
    // For now, this is mainly for future enhancements
    
    // Smooth scrolling for any internal links
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
    
    // Add loading states for iframes
    const iframes = document.querySelectorAll('iframe');
    iframes.forEach(iframe => {
        iframe.addEventListener('load', function() {
            this.style.opacity = '1';
        });
        iframe.style.opacity = '0.8';
        iframe.style.transition = 'opacity 0.3s ease';
    });
});
"""
        
        output_file = self.output_dir / "scripts.js"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"✅ JavaScript generated: {output_file}")
    
    def build(self):
        """Main build process"""
        print("🚀 Starting Music Library website build...\n")
        
        try:
            # Setup
            sheet = self.setup_google_sheets()
            music_data = self.fetch_music_data(sheet)
            
            # Create output structure
            self.create_output_directory()
            
            # Generate files
            self.generate_html(music_data)
            self.generate_css()
            self.generate_js()
            
            print(f"\n🎉 Build complete! Generated website in: {self.output_dir}")
            print(f"📂 Open {self.output_dir / 'index.html'} in your browser")
            
        except Exception as e:
            print(f"\n❌ Build failed: {str(e)}")
            raise

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python build_music_site.py <path_to_credentials.json>")
        sys.exit(1)
    
    credentials_path = sys.argv[1]
    builder = MusicSiteBuilder(credentials_path)
    builder.build()

if __name__ == "__main__":
    main()