# Album du Jour - Enhanced Music Discovery Website

A static site generator that creates a beautiful, responsive website showcasing your personal music library with embedded Apple Music and Spotify players. Features enhanced visual design with LUFS branding, collapsible sections, and timestamp-based album categorization.

## ✨ Features

### 🎨 Enhanced Visual Design
- **LUFS Brand Integration**: Custom color palette with teal, red, yellow, and blue accents
- **Animated Background**: Floating gradient elements that create dynamic visual interest
- **Custom Favicon**: Skeumorphic vinyl record design representing "album du jour"
- **Gradient Borders**: Inspired by echobridge.lufs.audio design language
- **Responsive Design**: Optimized for smartphone, tablet, and desktop devices

### 📱 Content Organization
- **Currently Listening**: Prominently displayed "album du jour" section
- **Recently Added**: Last 20 albums added to your library (collapsible)
- **Recently Finished**: Last 20 albums you've completed (collapsible)
- **Smart Categorization**: Timestamp-based sorting with newest items first
- **Collapsible Sections**: User-friendly interface with localStorage persistence

### 🎵 Music Integration
- **Apple Music Embeds**: Full-featured embedded players
- **Spotify Embeds**: Rich preview players with track listings
- **Direct Links**: Quick access to albums on both platforms
- **Lazy Loading**: Performance-optimized embed loading
- **Responsive Embeds**: Optimized sizes for different screen sizes

### 🔧 Technical Features
- **Static Site Generation**: Fast, secure, and easy to deploy
- **Google Sheets Integration**: Real-time data from your music spreadsheet
- **Git Workflow**: Separate branches for source code and deployment
- **Security First**: Credentials never committed to public repositories
- **Performance Optimized**: Fast loading with minimal JavaScript

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Git with push access to your repository
- Google Sheets API credentials
- Apple Music and/or Spotify links in your music library

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd albumdujour
   ```

2. **Set up credentials**
   ```bash
   # Place your Google Sheets service account JSON file
   cp /path/to/your/credentials.json concrete-spider-446700-f9-4646496845d1.json
   
   # Optional: Add Apple Music developer tokens
   mkdir musickit
   cp /path/to/your/apple-tokens/* musickit/
   ```

3. **Install dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install gspread
   ```

4. **Build and deploy**
   ```bash
   ./build.sh
   ```

## 📊 Data Format

Your Google Sheets spreadsheet should have the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| Music | Album - Artist format | `The Don – Donny Benét` |
| Apple Music Link | Full Apple Music URL | `https://music.apple.com/us/album/...` |
| Spotify Link | Full Spotify URL | `https://open.spotify.com/album/...` |
| Status | Current/Open/Done | `Current` |
| Date Added | ISO 8601 timestamp | `2025-01-15T10:30:00Z` |
| Date Finished | ISO 8601 timestamp | `2025-01-20T15:45:00Z` |
| 🌞 | Rating (optional) | `⭐⭐⭐⭐⭐` |

### Timestamp Format
- **Valid**: `2025-01-15T10:30:00Z` or `2025-01-15T10:30:00`
- **Ignored**: `20XX-XX-XXTXX:XX:XXZ` (placeholder format)
- **Empty**: Blank cells are ignored

### Album Categorization Logic
1. **Currently Listening**: Status = "Current" (displayed prominently)
2. **Recently Added**: Valid Date Added timestamp, sorted newest first (limit 20)
3. **Recently Finished**: Valid Date Finished timestamp, sorted newest first (limit 20)

## 🛠️ Configuration

### Google Sheets Setup
1. Create a Google Cloud Project
2. Enable the Google Sheets API
3. Create a service account and download the JSON credentials
4. Share your spreadsheet with the service account email
5. Name your spreadsheet "2025-media" with music data in the first worksheet

### Credential Paths
The build script supports multiple credential locations:

**Primary paths** (in project directory):
- `concrete-spider-446700-f9-4646496845d1.json`
- `musickit/` directory

**Alternative paths** (external):
- `/Users/danielramirez/Nextcloud/ore/Notes/Life/concrete-spider-446700-f9-4646496845d1.json`
- `/Users/danielramirez/Nextcloud/ore/Notes/Life/utilities/musickit`

### Environment Variables
No environment variables required. All configuration is file-based for security.

## 🏗️ Build Process

The enhanced build process creates two Git branches:

### Main Branch (Source Code)
- Python build script
- Bash deployment script
- Assets and documentation
- Configuration files
- **Excludes**: Credentials and sensitive files

### Build Branch (Deployment)
- `index.html` - Generated website
- `styles.css` - Enhanced CSS with LUFS branding
- `scripts.js` - Interactive functionality
- `assets/` - Optimized images and favicon
- `README.md` - Deployment documentation
- **Excludes**: All source code and credentials

### Build Script Features
- **Security First**: Whitelist approach for build files
- **Credential Protection**: Multiple verification steps
- **Error Handling**: Comprehensive logging and rollback
- **Git Workflow**: Clean orphan branch creation
- **Performance**: Optimized asset copying

## 🎨 Design System

### LUFS Brand Colors
```css
:root {
    --lufs-teal: #78BEBA;
    --lufs-red: #D35233;
    --lufs-yellow: #E7B225;
    --lufs-blue: #2069af;
    --lufs-black: #111111;
    --lufs-white: #fbf9e2;
}
```

### Typography
- **Primary Font**: System font stack for optimal performance
- **Headings**: Bold weights with LUFS color gradients
- **Body Text**: Optimized for readability across devices

### Layout
- **Container**: Max-width 1400px with responsive padding
- **Grid System**: CSS Grid with auto-fit columns
- **Spacing**: Consistent rem-based spacing scale
- **Border Radius**: 12px for modern, friendly appearance

### Animations
- **Background**: Floating gradient elements with 20s animation cycle
- **Interactions**: Smooth hover effects and transitions
- **Performance**: GPU-accelerated transforms and opacity changes

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px (single column, touch-optimized)
- **Tablet**: 768px - 1024px (two columns, hybrid interactions)
- **Desktop**: > 1024px (multi-column, hover effects)

### Touch Optimization
- **Minimum Touch Targets**: 44px for accessibility
- **Touch Actions**: Optimized for mobile interactions
- **Hover Fallbacks**: Alternative interactions for touch devices

### Performance
- **Mobile-First**: CSS written for mobile, enhanced for desktop
- **Lazy Loading**: Embeds load only when visible
- **Reduced Motion**: Respects user preferences for animations

## 🔧 Development

### File Structure
```
albumdujour/
├── build_music_site.py      # Enhanced Python build script
├── build.sh                 # Improved deployment script
├── assets/
│   ├── favicon.svg          # Custom vinyl record favicon
│   └── [other assets]       # Additional images and graphics
├── fonts/                   # Custom fonts (if any)
├── venv/                    # Python virtual environment
├── build/                   # Generated website files
├── README.md                # This documentation
└── [credential files]       # Not committed to Git
```

### Python Dependencies
- **gspread**: Google Sheets API client
- **datetime**: Timestamp parsing and formatting
- **pathlib**: Modern file path handling
- **urllib**: URL parsing for embed generation

### JavaScript Features
- **Collapsible Sections**: Smooth expand/collapse animations
- **Local Storage**: Remembers user section preferences
- **Lazy Loading**: Intersection Observer for performance
- **Accessibility**: Keyboard navigation and ARIA labels
- **Error Handling**: Graceful fallbacks for failed embeds

## 🚀 Deployment

### Static Hosting Options
The build branch is ready for deployment to any static hosting service:

#### Netlify
1. Connect your Git repository
2. Set build branch as deployment branch
3. No build command needed (pre-built)
4. Deploy automatically on push

#### Vercel
1. Import Git repository
2. Configure build branch as source
3. Set framework preset to "Other"
4. Deploy with zero configuration

#### GitHub Pages
1. Go to repository Settings > Pages
2. Select "Deploy from a branch"
3. Choose "build" branch
4. Site will be available at `username.github.io/repository`

#### Traditional Hosting
1. Download build branch files
2. Upload to web server via FTP/SFTP
3. Point domain to uploaded files
4. No server configuration required

### Custom Domain
Add a `CNAME` file to the build branch with your domain name for custom domain support.

### SSL/HTTPS
Most modern hosting providers include free SSL certificates. Ensure your site is served over HTTPS for security and performance.

## 🔒 Security

### Credential Protection
- **Never Committed**: Credentials are never added to Git
- **Gitignore Protection**: Multiple layers of gitignore rules
- **Build Verification**: Automated security scanning
- **Alternative Paths**: Support for external credential storage

### Content Security
- **Static Generation**: No server-side vulnerabilities
- **Embed Security**: Sandboxed iframes for music players
- **XSS Prevention**: Proper HTML escaping and sanitization

### Privacy
- **No Tracking**: No analytics or tracking scripts by default
- **Local Storage**: Only used for user preferences
- **Third-Party**: Only music service embeds (Apple Music, Spotify)

## 🧪 Testing

### Manual Testing Checklist
- [ ] All sections display correctly
- [ ] Collapsible sections work on all devices
- [ ] Music embeds load and play properly
- [ ] Responsive design works across screen sizes
- [ ] Build process creates proper Git branches
- [ ] No credentials in build branch
- [ ] Page loads in under 3 seconds
- [ ] Accessibility features work with keyboard navigation

### Browser Support
- **Modern Browsers**: Chrome, Firefox, Safari, Edge (latest versions)
- **Mobile Browsers**: iOS Safari, Chrome Mobile, Samsung Internet
- **Progressive Enhancement**: Graceful degradation for older browsers

### Performance Targets
- **Page Load**: < 3 seconds on 3G connection
- **First Contentful Paint**: < 1.5 seconds
- **Largest Contentful Paint**: < 2.5 seconds
- **Cumulative Layout Shift**: < 0.1

## 🐛 Troubleshooting

### Common Issues

#### Build Fails with Credentials Error
```bash
# Check credential file exists
ls -la concrete-spider-446700-f9-4646496845d1.json

# Verify Google Sheets access
python3 -c "import gspread; gc = gspread.service_account('concrete-spider-446700-f9-4646496845d1.json'); print('Credentials valid')"
```

#### Git Push Fails
```bash
# Check remote configuration
git remote -v

# Force push build branch (if needed)
git push --force origin build
```

#### Embeds Not Loading
1. Check Apple Music and Spotify URLs are valid
2. Verify embed URL generation in Python script
3. Test embeds in browser developer tools
4. Check for CORS or content security policy issues

#### Responsive Design Issues
1. Test on actual devices, not just browser resize
2. Check CSS media queries in developer tools
3. Verify touch targets are at least 44px
4. Test with different screen orientations

### Debug Mode
Enable verbose logging in the build script:
```bash
# Add debug flag to build script
DEBUG=1 ./build.sh
```

### Log Files
Build logs are output to console. For persistent logging:
```bash
./build.sh 2>&1 | tee build.log
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use modern ES6+ features
- **CSS**: Use CSS custom properties for theming
- **HTML**: Semantic markup with accessibility in mind

### Commit Messages
Use conventional commit format:
```
feat: add new album categorization logic
fix: resolve mobile responsive issues
docs: update installation instructions
style: improve CSS organization
```

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🙏 Acknowledgments

- **LUFS Audio**: Brand design and color palette
- **Google Sheets API**: Data source integration
- **Apple Music**: Embedded player functionality
- **Spotify**: Rich preview embeds
- **Modern Web Standards**: CSS Grid, Intersection Observer, and more

## 📞 Support

For issues, questions, or contributions:

1. **GitHub Issues**: Report bugs and request features
2. **Documentation**: Check this README and inline code comments
3. **Community**: Share your Album du Jour sites and customizations

---

**Built with ❤️ by LUFS Audio**  
*Showcasing music discovery through beautiful, functional design*

