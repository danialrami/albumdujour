# Album du Jour - Build Files

This directory contains the generated static website files for Album du Jour.

## Generated Files

- `index.html` - Main website page with simplified design and responsive embeds
- `styles.css` - Stylesheet with LUFS branding and responsive embed sizing
- `scripts.js` - Interactive functionality for collapsible sections and embed management
- `assets/` - Images and static assets including simplified favicon
- `favicon.svg` - Clean, abstract vinyl record favicon

## Features

### Content Organization
- **Currently Listening**: Prominently displayed "album du jour" with large embed
- **Recently Added**: Last 20 albums added (collapsible)
- **Recently Finished**: Last 20 albums completed (collapsible)

### Responsive Embed Sizing
- **Mobile (< 768px)**: Optimized heights for small screens
  - Current listening: 350px (320px on very small screens)
  - Grid embeds: 200px (180px on very small screens)
- **Tablet (768px+)**: Balanced sizing for medium screens
  - Current listening: 420px
  - Grid embeds: 220px
- **Desktop (1024px+)**: Larger embeds for desktop viewing
  - Current listening: 450px
  - Grid embeds: 240px
- **Large Desktop (1440px+)**: Maximum sizing for large screens
  - Current listening: 480px
  - Grid embeds: 260px

### Design Features
- LUFS brand colors with simplified background animation
- Clean album cards that let Spotify embeds provide color
- Responsive design for all devices with optimized embed containers
- Collapsible sections with localStorage persistence
- Lazy loading for music embeds with performance optimization
- Accessibility features and keyboard navigation

### Music Integration
- Apple Music and Spotify embeds with responsive sizing
- Direct links to music services
- Optimized embed heights for different screen sizes and sections
- Enhanced embed loading with error handling

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
- Responsive design tested across multiple screen sizes

## Performance

- Optimized for fast loading with responsive embeds
- Lazy loading for embeds based on viewport intersection
- Minimal JavaScript footprint with efficient resize handling
- Responsive images and assets
- CSS-based responsive sizing for smooth performance

---

**Generated on:** 2025-06-23 14:19:43  
**Source:** Album du Jour Enhanced Build System v2 with Responsive Embeds  
**Version:** 2.1  
