# Album du Jour - Music Discovery Website

A static site generator that creates a beautiful, responsive website showcasing your personal music library with embedded Apple Music and Spotify players.

## ✨ Features

### 🎨 Minimal Visual Design
- **LUFS Brand Integration**: Subtle background animation with brand colors
- **Clean Album Cards**: Simplified design that lets Spotify embeds provide color
- **Minimal Abstract Favicon**: Clean, simple design inspired by LUFS brand sites
- **Responsive Design**: Optimized for smartphone, tablet, and desktop devices
- **Natural Color Accents**: Spotify embeds provide vibrant, natural color

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
- **Master Build Pipeline**: Single command for complete automation
- **Safe Git Deployment**: Uses git subtree split (no repo deletion risk)
- **External Credentials**: Uses only alternative credential paths (never in repo)
- **Enhanced Security**: Multiple verification layers prevent credential leaks
- **Modular Scripts**: Separate build.sh, deploy.sh, and master-build.sh
- **Repeatable Process**: Safe to run multiple times without issues

## 🚀 Quick Start

### Prerequisites
- Python 3.13 or higher (matching NextCloud Docker container)
- Git with push access to your repository
- Google Sheets API credentials at alternative path
- Apple Music and/or Spotify links in your music library

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/danialrami/albumdujour
   cd albumdujour
   ```

2. **Complete build and deployment**
   ```bash
   ./master-build.sh
   ```

## 🛠️ Build Process v3

### Master Pipeline (Recommended)
```bash
./master-build.sh
```
- Runs complete build and deployment process
- Creates website and deploys to Git in one command
- Safe to run repeatedly

### Individual Steps (For Development)

#### Step 1: Build Website
```bash
./build.sh
```
- Creates Python virtual environment
- Fetches data from Google Sheets using external credentials
- Generates enhanced website with simplified design
- Creates build/ directory with all website files
- No Git operations performed

#### Step 2: Deploy to Git
```bash
./deploy.sh
```
- Commits source changes to main branch
- Uses git subtree split to create build branch safely
- Pushes both branches to remote repository

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
| 🌞 | Rating (optional) | `🌞` |

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

### Minimal Design Philosophy
- **Abstract Favicon**: Simple vinyl record inspired by LUFS brand sites
- **Clean Album Cards**: Minimal design that doesn't compete with embeds
- **Spotify Color Integration**: Let music embeds provide natural color accents
- **Subtle Background**: Gentle floating animation using brand colors

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px (single column, touch-optimized)
- **Tablet**: 768px - 1024px (two columns, hybrid interactions)
- **Desktop**: > 1024px (multi-column, hover effects)

### Performance
- **Lazy Loading**: Embeds load only when visible
- **Reduced Motion**: Respects user preferences for animations
- **External Credentials**: No credential processing during build
- **Safe Git Operations**: Subtree split prevents repository issues

## 🔧 Development

### File Structure
```
albumdujour/
├── master-build.sh             # Master pipeline script
├── build.sh                    # Website build script (no Git)
├── deploy.sh                   # Git deployment script (subtree split)
├── build_music_site.py         # Python build script
├── concrete-spider-*.json      # Google Sheets credentials (gitignored)
├── .gitignore                  # Comprehensive credential protection
├── assets/
│   ├── favicon.svg             # Minimal abstract favicon
│   └── [other assets]          # Additional images and graphics
├── fonts/                      # Custom fonts
├── venv/                       # Python virtual environment (gitignored)
├── build/                      # Generated website files
├── docs/                       # Implementation documentation
│   └── IMPLEMENTATION.md       # Detailed technical documentation
└── README.md                   # This documentation
```

### Git Workflow
1. **Main Branch**: Source code and development files
2. **Build Branch**: Generated using `git subtree split --prefix build`
3. **Safe Deployment**: No risk of repository deletion
4. **Repeatable**: Can be run multiple times safely

## 🚀 Deployment

### Master Pipeline (Recommended)
```bash
# Complete build and deployment
./master-build.sh

# Build only (for testing)
./master-build.sh --build-only
```

### Local Testing
```bash
# Build website
./build.sh

# Open in browser
open build/index.html
```

### Git Deployment
```bash
# Deploy to repository (after build)
./deploy.sh
```

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

## 🔒 Security

### Enhanced Credential Protection
- **External Storage**: Credentials never stored in repository
- **Build Verification**: Automated security scanning before deployment
- **Gitignore Protection**: Comprehensive patterns prevent accidental commits
- **Safe Git Operations**: Subtree split prevents repository corruption

### Content Security
- **Static Generation**: No server-side vulnerabilities
- **Embed Security**: Sandboxed iframes for music players
- **XSS Prevention**: Proper HTML escaping and sanitization

## 🧪 Testing

### Manual Testing Checklist
- [ ] All sections display correctly
- [ ] Collapsible sections work on all devices
- [ ] Music embeds load and play properly
- [ ] Responsive design works across screen sizes
- [ ] Master build process completes successfully
- [ ] Deploy process creates proper Git branches
- [ ] No credentials in build branch
- [ ] Page loads in under 3 seconds
- [ ] Accessibility features work with keyboard navigation

### Build Testing
```bash
# Test master pipeline
./master-build.sh --build-only

# Verify no credentials in build
grep -r "concrete-spider" build/ || echo "✅ No credentials found"

# Test individual components
./build.sh
./deploy.sh

# Check Git branches
git branch -a
```

## 🐛 Troubleshooting

### Common Issues

#### Master Build Fails
```bash
# Check script permissions
ls -la *.sh

# Run individual steps for debugging
./build.sh
./deploy.sh
```

#### Git Deployment Fails
```bash
# Check Git configuration
git remote -v
git status

# Verify build directory exists
ls -la build/

# Test subtree split manually
git subtree split --prefix build -b test-build
git branch -D test-build
```

### Script Options
```bash
# Master pipeline options
./master-build.sh --help
./master-build.sh --build-only

# Individual scripts
./build.sh    # Build only
./deploy.sh   # Deploy only (requires existing build)
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Test with `./master-build.sh --build-only`
4. Submit a pull request

### Code Style
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use modern ES6+ features
- **CSS**: Use CSS custom properties for theming
- **Shell**: Follow shellcheck recommendations

## 🔗 Related Projects

### obsidian-scripts (~/repos/obsidian-scripts)

This project is closely related to [obsidian-scripts](https://github.com/danialrami/obsidian-scripts), which also reads from the same Google Sheets ("2025-media"):

- **media.py**: Generates the "Du Jour" section in daily notes showing current music/TV
- **sync.py**: Syncs music library between Apple Music and Google Sheets
- **mark_music_done.py**: Marks current album as "Done" when finished

**Key Difference**:
- **albumdujour**: Creates a **public** static website showcasing your music library
- **obsidian-scripts**: Creates **private** daily notes in Obsidian Vault

### Python Version Parity

Both projects use Python 3.13.2 (via pyenv) to match the NextCloud Docker container's Python version. This ensures consistency when running scripts inside the container.

See [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md) for detailed technical documentation.

## 🙏 Acknowledgments

- **Google Sheets API**: Data source integration
- **Apple Music**: Embedded player functionality
- **Spotify**: Rich preview embeds
- **Git Subtree**: Safe deployment methodology

---

**Built with 🩷**
