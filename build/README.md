# Album du Jour - Build Files

This directory contains the generated static website files for Album du Jour.

## Generated Files

- `index.html` - Main website page with dynamic responsive design
- `styles.css` - Stylesheet with LUFS branding and flexible layout system
- `scripts.js` - Interactive functionality with intelligent embed resizing
- `assets/` - Images and static assets including favicon
- `favicon.svg` - Clean, abstract vinyl record favicon

## Features

### Dynamic Responsive Layout
- **Mobile**: Single column layout with touch-optimized embeds
- **Tablet**: Two-column grid with balanced sizing
- **Desktop**: Three-column layout with larger embeds
- **Large Desktop**: Four-column grid maximizing screen real estate
- **Ultra-wide**: Five columns for maximum content density

### Intelligent Embed Sizing
- **CSS Flexbox**: Cards automatically fill available grid space
- **JavaScript Calculation**: Embeds resize based on actual card dimensions
- **Dynamic Heights**: No hardcoded sizes - embeds adapt to content
- **Minimum/Maximum Constraints**: Ensures usability across all screen sizes

### Content Organization
- **Currently Listening**: Prominently displayed with large embed
- **Recently Added**: Last 20 albums (collapsible, sorted by date added)
- **Recently Finished**: Last 20 albums (collapsible, sorted by date finished)

### Interactive Features
- LUFS brand colors with animated background
- Collapsible sections with localStorage persistence
- Lazy loading for performance optimization
- Accessibility features and keyboard navigation
- Touch-friendly interactions on mobile devices

### Music Integration
- Apple Music and Spotify embeds with optimal sizing
- Direct links to music services
- Error handling for failed embeds
- Service-specific height adjustments (Apple Music gets extra space)

## Technical Implementation

### CSS Grid System
```css
/* Mobile: 1 column */
@media (max-width: 767px) {
    .album-grid { grid-template-columns: 1fr; }
}

/* Tablet: 2 columns */
@media (min-width: 768px) and (max-width: 1023px) {
    .album-grid { grid-template-columns: 1fr 1fr; }
}

/* Desktop: 3 columns */
@media (min-width: 1024px) and (max-width: 1439px) {
    .album-grid { grid-template-columns: 1fr 1fr 1fr; }
}

/* Large Desktop: 4 columns */
@media (min-width: 1440px) {
    .album-grid { grid-template-columns: 1fr 1fr 1fr 1fr; }
}
```

### Dynamic Embed Sizing
```javascript
// JavaScript calculates optimal embed height based on:
// - Album card height
// - Header and footer space
// - Minimum/maximum constraints
// - Screen size considerations
```

## Deployment

Ready for deployment to any static hosting service:

- **Netlify**: Direct folder upload or Git integration
- **Vercel**: Connect to repository, automatic deployments
- **GitHub Pages**: Serve from build branch
- **Traditional Hosting**: Upload files via FTP/SFTP

## Performance Features

- **Lazy Loading**: Embeds load only when visible
- **Efficient Resizing**: Debounced resize calculations
- **Minimal JavaScript**: Lightweight interactive enhancements
- **CSS-First Approach**: Layout handled by CSS for best performance

---

**Generated on:** 2025-06-23 14:43:40
**Source:** Album du Jour Dynamic Responsive Build System  
**Version:** 2.2 - Dynamic Responsive Layout  
