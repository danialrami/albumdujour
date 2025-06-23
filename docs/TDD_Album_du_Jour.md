# Technical Design Document (TDD)
## Album du Jour Website Enhancement

### Document Overview

**Project:** Album du Jour Website Enhancement  
**Version:** 2.0  
**Date:** June 23, 2025  
**Author:** Technical Implementation Team  
**Status:** Draft - Pending Approval  

### Architecture Overview

The Album du Jour website follows a static site generation architecture with the following components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Google        │    │    Python        │    │   Static        │
│   Sheets API    │───▶│   Build Script   │───▶│   Website       │
│                 │    │                  │    │   (HTML/CSS/JS) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Git Deployment │
                       │   (main/build)   │
                       └──────────────────┘
```

### System Components

#### 1. Data Layer

**Google Sheets Integration**
- **API**: Google Sheets API v4
- **Authentication**: Service Account JSON credentials
- **Spreadsheet**: "2025-media" with Music worksheet
- **Data Format**: CSV with columns:
  - Music (Album - Artist format)
  - Apple Music Link
  - Spotify Link
  - Status (Current/Open/Done)
  - Date Added (ISO 8601 format)
  - Date Finished (ISO 8601 format)
  - Rating (🌞 emoji)

**Data Processing Logic**
```python
def parse_timestamp(timestamp_str):
    """Parse timestamp, ignore placeholders like '20XX-XX-XXTXX:XX:XXZ'"""
    if not timestamp_str or 'XX' in timestamp_str:
        return None
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        return None

def categorize_albums(records):
    """Categorize albums based on status and timestamps"""
    current = []
    recently_added = []
    recently_finished = []
    
    for record in records:
        if record['status'] == 'Current':
            current.append(record)
        elif record['date_finished'] and parse_timestamp(record['date_finished']):
            recently_finished.append(record)
        elif record['date_added'] and parse_timestamp(record['date_added']):
            recently_added.append(record)
    
    # Sort by timestamps (newest first)
    recently_added.sort(key=lambda x: parse_timestamp(x['date_added']), reverse=True)
    recently_finished.sort(key=lambda x: parse_timestamp(x['date_finished']), reverse=True)
    
    return {
        'current': current,
        'recently_added': recently_added[:20],
        'recently_finished': recently_finished[:20]
    }
```

#### 2. Build System

**Python Build Script Enhancement**
```python
class MusicSiteBuilder:
    def __init__(self):
        self.website_dir = Path(__file__).parent
        self.credentials_path = self.website_dir / 'concrete-spider-446700-f9-4646496845d1.json'
        self.output_dir = self.website_dir / "build"
        
    def generate_collapsible_sections(self, albums_data):
        """Generate HTML with collapsible sections"""
        sections = {
            'current': {
                'title': '🎧 Currently Listening',
                'albums': albums_data['current'],
                'collapsible': False,
                'default_open': True
            },
            'recently_added': {
                'title': '📀 Recently Added',
                'albums': albums_data['recently_added'],
                'collapsible': True,
                'default_open': False
            },
            'recently_finished': {
                'title': '✅ Recently Finished',
                'albums': albums_data['recently_finished'],
                'collapsible': True,
                'default_open': False
            }
        }
        return self.render_sections(sections)
        
    def generate_build_readme(self):
        """Generate README for build folder"""
        readme_content = f"""
# Album du Jour - Build Files

This directory contains the generated static website files for Album du Jour.

## Generated Files
- `index.html` - Main website page
- `styles.css` - Stylesheet with LUFS branding
- `scripts.js` - Interactive functionality
- `assets/` - Images and static assets
- `favicon.svg` - Custom Album du Jour favicon

## Deployment
These files are ready for deployment to any static hosting service.

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source: https://github.com/[username]/albumdujour (main branch)
"""
        with open(self.output_dir / 'README.md', 'w') as f:
            f.write(readme_content)
```

**Build Script Improvements**
```bash
#!/bin/bash
# Enhanced build script with proper Git branch management

create_clean_build_branch() {
    log_info "Creating clean build branch..."
    
    # Delete existing build branch completely
    git branch -D build 2>/dev/null || true
    git push origin --delete build 2>/dev/null || true
    
    # Create fresh orphan branch
    git checkout --orphan build
    git rm -rf . 2>/dev/null || true
    git clean -fd
    
    # Copy only web files (security whitelist)
    cp "$TEMP_BACKUP_DIR/build/index.html" .
    cp "$TEMP_BACKUP_DIR/build/styles.css" .
    cp "$TEMP_BACKUP_DIR/build/scripts.js" . 2>/dev/null || true
    cp -r "$TEMP_BACKUP_DIR/build/assets" . 2>/dev/null || true
    cp "$TEMP_BACKUP_DIR/build/favicon.svg" . 2>/dev/null || true
    cp "$TEMP_BACKUP_DIR/build/README.md" . 2>/dev/null || true
    
    # Create security-focused .gitignore
    cat > .gitignore << 'EOF'
# Credentials - NEVER commit
concrete-spider-446700-f9-*.json
musickit/
*.key
*.pem
*.p8
.env*

# Build tools
build_music_site.py
build.sh
venv/
__pycache__/
EOF
    
    git add .
    git commit -m "Deploy website build - $(date '+%Y-%m-%d %H:%M:%S')"
    git push --force-with-lease origin build
}
```

#### 3. Frontend Architecture

**HTML Structure**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Album du Jour - Music Discovery</title>
    <link rel="icon" href="favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="styles.css">
    <meta name="description" content="Personal music library showcase featuring currently listening, recently added, and recently finished albums.">
</head>
<body>
    <div class="animated-background"></div>
    <div class="container">
        <header class="site-header">
            <h1>🎵 Album du Jour</h1>
            <p class="subtitle">Personal Music Discovery</p>
            <div class="stats-badges">
                <span class="badge current">1 Current</span>
                <span class="badge added">20 Recently Added</span>
                <span class="badge finished">20 Recently Finished</span>
            </div>
        </header>
        
        <main class="content">
            <section class="currently-listening">
                <!-- Always visible, prominently displayed -->
            </section>
            
            <section class="collapsible-section" data-section="recently-added">
                <button class="section-toggle" aria-expanded="false">
                    <h2>📀 Recently Added</h2>
                    <span class="toggle-icon">▼</span>
                </button>
                <div class="section-content">
                    <!-- Collapsible content -->
                </div>
            </section>
            
            <section class="collapsible-section" data-section="recently-finished">
                <button class="section-toggle" aria-expanded="false">
                    <h2>✅ Recently Finished</h2>
                    <span class="toggle-icon">▼</span>
                </button>
                <div class="section-content">
                    <!-- Collapsible content -->
                </div>
            </section>
        </main>
        
        <footer class="site-footer">
            <a href="https://docs.google.com/spreadsheets/d/1p8zTsGuQVV81tvuZswIHq-pIXCyZn9ixhg-2HWD9X10/edit?gid=0#gid=0" 
               target="_blank" class="sheets-link">
                📊 View Full Library
            </a>
            <p>Built with ❤️ by LUFS Audio</p>
        </footer>
    </div>
    
    <script src="scripts.js"></script>
</body>
</html>
```

**CSS Architecture**
```css
/* CSS Custom Properties for LUFS Brand Colors */
:root {
    --lufs-teal: #78BEBA;
    --lufs-red: #D35233;
    --lufs-yellow: #E7B225;
    --lufs-blue: #2069af;
    --lufs-black: #111111;
    --lufs-white: #fbf9e2;
    
    /* Derived colors */
    --lufs-teal-alpha: rgba(120, 190, 186, 0.1);
    --lufs-gradient: linear-gradient(135deg, var(--lufs-teal), var(--lufs-blue));
    --lufs-border-gradient: linear-gradient(90deg, var(--lufs-teal), var(--lufs-yellow), var(--lufs-red), var(--lufs-blue));
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
        radial-gradient(circle at 80% 20%, rgba(208, 82, 51, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 40% 40%, rgba(231, 178, 37, 0.05) 0%, transparent 50%);
    animation: float 20s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    33% { transform: translate(30px, -30px) rotate(120deg); }
    66% { transform: translate(-20px, 20px) rotate(240deg); }
}

/* Responsive Grid System */
.album-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    padding: 2rem 0;
}

@media (max-width: 768px) {
    .album-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
        padding: 1rem 0;
    }
}

/* Album Card Design */
.album-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid transparent;
    background-image: var(--lufs-border-gradient);
    background-origin: border-box;
    background-clip: padding-box, border-box;
    transition: all 0.3s ease;
}

.album-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(120, 190, 186, 0.2);
}

/* Currently Listening Special Styling */
.currently-listening .album-card {
    background: var(--lufs-gradient);
    color: var(--lufs-white);
    border: 2px solid var(--lufs-yellow);
    box-shadow: 0 0 20px rgba(231, 178, 37, 0.3);
}
```

**JavaScript Functionality**
```javascript
// Collapsible sections functionality
class AlbumSections {
    constructor() {
        this.initializeCollapsibleSections();
        this.initializeIntersectionObserver();
    }
    
    initializeCollapsibleSections() {
        const toggleButtons = document.querySelectorAll('.section-toggle');
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const section = e.currentTarget.closest('.collapsible-section');
                const content = section.querySelector('.section-content');
                const icon = section.querySelector('.toggle-icon');
                const isExpanded = button.getAttribute('aria-expanded') === 'true';
                
                // Toggle expanded state
                button.setAttribute('aria-expanded', !isExpanded);
                content.style.maxHeight = isExpanded ? '0' : content.scrollHeight + 'px';
                icon.style.transform = isExpanded ? 'rotate(0deg)' : 'rotate(180deg)';
                
                // Save state to localStorage
                localStorage.setItem(`section-${section.dataset.section}`, !isExpanded);
            });
        });
        
        // Restore saved states
        this.restoreSectionStates();
    }
    
    restoreSectionStates() {
        const sections = document.querySelectorAll('.collapsible-section');
        sections.forEach(section => {
            const savedState = localStorage.getItem(`section-${section.dataset.section}`);
            if (savedState === 'true') {
                const button = section.querySelector('.section-toggle');
                button.click();
            }
        });
    }
    
    initializeIntersectionObserver() {
        // Lazy load album embeds for performance
        const embedObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const iframe = entry.target;
                    if (iframe.dataset.src) {
                        iframe.src = iframe.dataset.src;
                        iframe.removeAttribute('data-src');
                        embedObserver.unobserve(iframe);
                    }
                }
            });
        }, { rootMargin: '100px' });
        
        document.querySelectorAll('iframe[data-src]').forEach(iframe => {
            embedObserver.observe(iframe);
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AlbumSections();
});
```

#### 4. Asset Creation

**Favicon SVG Design**
```svg
<!-- favicon.svg - Album du Jour icon -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
    <defs>
        <linearGradient id="vinyl" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#78BEBA"/>
            <stop offset="100%" style="stop-color:#2069af"/>
        </linearGradient>
        <radialGradient id="label" cx="50%" cy="50%" r="30%">
            <stop offset="0%" style="stop-color:#E7B225"/>
            <stop offset="100%" style="stop-color:#D35233"/>
        </radialGradient>
    </defs>
    
    <!-- Vinyl record -->
    <circle cx="32" cy="32" r="28" fill="url(#vinyl)" stroke="#111111" stroke-width="2"/>
    
    <!-- Record grooves -->
    <circle cx="32" cy="32" r="24" fill="none" stroke="#111111" stroke-width="0.5" opacity="0.3"/>
    <circle cx="32" cy="32" r="20" fill="none" stroke="#111111" stroke-width="0.5" opacity="0.3"/>
    <circle cx="32" cy="32" r="16" fill="none" stroke="#111111" stroke-width="0.5" opacity="0.3"/>
    
    <!-- Center label -->
    <circle cx="32" cy="32" r="8" fill="url(#label)"/>
    <circle cx="32" cy="32" r="2" fill="#111111"/>
    
    <!-- "du Jour" text curve -->
    <path id="textcircle" d="M 32,12 A 20,20 0 0,1 52,32" fill="none"/>
    <text font-family="Arial, sans-serif" font-size="6" font-weight="bold" fill="#fbf9e2">
        <textPath href="#textcircle" startOffset="0%">du Jour</textPath>
    </text>
</svg>
```

#### 5. Responsive Design Strategy

**Breakpoint System**
```css
/* Mobile First Approach */
:root {
    --container-padding: 1rem;
    --grid-columns: 1;
    --embed-height: 152px;
}

@media (min-width: 768px) {
    :root {
        --container-padding: 2rem;
        --grid-columns: 2;
        --embed-height: 200px;
    }
}

@media (min-width: 1024px) {
    :root {
        --container-padding: 3rem;
        --grid-columns: 3;
        --embed-height: 250px;
    }
}

@media (min-width: 1440px) {
    :root {
        --container-padding: 4rem;
        --grid-columns: 4;
        --embed-height: 300px;
    }
}
```

**Touch Interactions**
```css
/* Touch-friendly interactions */
.section-toggle {
    min-height: 44px; /* iOS minimum touch target */
    padding: 1rem;
    touch-action: manipulation;
}

@media (hover: hover) {
    .album-card:hover {
        transform: translateY(-4px);
    }
}

@media (hover: none) {
    .album-card:active {
        transform: scale(0.98);
    }
}
```

#### 6. Performance Optimization

**Image Optimization**
- SVG favicon for scalability
- Lazy loading for music embeds
- Optimized asset delivery

**JavaScript Optimization**
- Minimal JavaScript footprint
- Event delegation for better performance
- Local storage for user preferences

**CSS Optimization**
- CSS custom properties for maintainability
- Efficient animations using transform and opacity
- Mobile-first responsive design

#### 7. Security Implementation

**Credential Protection**
```bash
# .gitignore entries (both main and build branches)
concrete-spider-446700-f9-*.json
musickit/
*.key
*.pem
*.p8
.env*
```

**Build Process Security**
- Whitelist approach for build files
- Automated security verification
- Separate credential storage options

#### 8. Testing Strategy

**Cross-Device Testing**
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Mobile devices (iOS Safari, Chrome Mobile)
- Tablet devices (iPad, Android tablets)

**Functionality Testing**
- Music embed functionality
- Collapsible sections
- Responsive design
- Build process validation

**Performance Testing**
- Page load speed
- Animation performance
- Memory usage
- Network requests

#### 9. Deployment Architecture

**Git Branch Strategy**
```
main branch:
├── source code
├── build scripts
├── documentation
└── assets (original)

build branch (orphan):
├── index.html
├── styles.css
├── scripts.js
├── favicon.svg
├── assets/ (optimized)
└── README.md
```

**Build Process Flow**
1. Fetch data from Google Sheets
2. Process and categorize albums
3. Generate HTML with embedded players
4. Create optimized CSS and JS
5. Generate favicon and assets
6. Create build README
7. Commit to main branch
8. Create clean build branch
9. Deploy build files
10. Push both branches to remote

#### 10. Monitoring and Maintenance

**Build Monitoring**
- Automated build success/failure notifications
- Git commit verification
- Credential security checks

**Performance Monitoring**
- Page load time tracking
- User interaction analytics
- Error logging and reporting

### Implementation Timeline

**Phase 1: Backend Enhancement (2-3 days)**
- Implement timestamp parsing
- Add album categorization logic
- Update data processing pipeline

**Phase 2: Frontend Development (3-4 days)**
- Create new HTML structure
- Implement CSS design system
- Add JavaScript interactions
- Create responsive layouts

**Phase 3: Asset Creation (1-2 days)**
- Design and create favicon
- Optimize images and graphics
- Create brand-consistent elements

**Phase 4: Build Process (2-3 days)**
- Enhance build script
- Implement Git workflow
- Add security measures
- Create documentation

**Phase 5: Testing and Deployment (2-3 days)**
- Cross-device testing
- Performance optimization
- Final integration testing
- Deployment and verification

### Risk Mitigation

**Technical Risks**
- API rate limiting: Implement caching and retry logic
- Build failures: Add comprehensive error handling
- Git conflicts: Use force-with-lease for safer force pushes

**Design Risks**
- Browser compatibility: Progressive enhancement approach
- Performance issues: Lazy loading and optimization
- Accessibility concerns: Semantic HTML and ARIA labels

### Success Criteria

1. **Functional Requirements Met**: All PRD requirements implemented
2. **Performance Targets**: Page load < 3 seconds, responsive design score 95+
3. **Security Validated**: No credentials in build branch, security checks pass
4. **Cross-Device Compatibility**: Works on all target devices and browsers
5. **Documentation Complete**: Comprehensive README files and technical docs

---

*Document Version: 1.0*  
*Last Updated: June 23, 2025*  
*Status: Draft - Pending Approval*

