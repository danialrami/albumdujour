# Product Requirements Document (PRD)
## Album du Jour Website Enhancement

### Executive Summary

The Album du Jour website is a static site generator that showcases music albums from a personal listening library. This enhancement project aims to improve the visual design, content organization, and build process while maintaining the core functionality of displaying album information with embedded music players.

### Project Overview

**Project Name:** Album du Jour Website Enhancement  
**Version:** 2.0  
**Date:** June 23, 2025  
**Owner:** Daniel Ramirez / LUFS Audio  

### Current State Analysis

The existing website (https://albumdujour.lufs.audio) features:
- Static site generation from Google Sheets data
- Three sections: Currently Listening, Up Next, Recently Finished
- Embedded Apple Music and Spotify players
- Basic black background with minimal styling
- Build process with Git deployment to separate branches

### Problem Statement

1. **Visual Design**: The current black background is bland and doesn't align with the LUFS brand aesthetic
2. **Content Organization**: Sections need better hierarchy and user interaction (collapsible sections)
3. **Data Logic**: Timestamp-based sorting is not implemented for Recently Added/Recently Finished sections
4. **Build Process**: The current build script has issues creating proper build branches
5. **Mobile Responsiveness**: Design needs optimization across all device types
6. **Branding**: Missing favicon and cohesive brand elements

### Goals and Objectives

#### Primary Goals
1. Enhance visual design with LUFS brand aesthetic and dynamic background elements
2. Improve content organization with collapsible sections and proper data sorting
3. Fix and optimize the build/deployment process
4. Ensure responsive design across all devices
5. Create comprehensive documentation

#### Secondary Goals
1. Maintain existing functionality of music player embeds
2. Preserve Apple Music and Spotify integration
3. Keep the focus on album artwork and music discovery
4. Implement proper SEO and accessibility features

### Target Audience

- **Primary**: Daniel Ramirez (site owner) for personal music library showcase
- **Secondary**: Visitors interested in music discovery and album recommendations
- **Tertiary**: Music enthusiasts and potential collaborators

### Functional Requirements

#### 1. Content Organization
- **Currently Listening**: Single album prominently displayed (album du jour)
- **Recently Added**: Last 20 albums added to the library (collapsible section)
- **Recently Finished**: Last 20 albums completed (collapsible section)
- **Total Display**: 41 album blocks maximum (1 + 20 + 20)

#### 2. Data Processing
- Parse CSV timestamps in format: `20XX-XX-XXTXX:XX:XXZ`
- Ignore blank rows and placeholder timestamps
- Sort albums by Date Added and Date Finished timestamps
- Filter out incomplete entries

#### 3. User Interface
- Collapsible sections for Recently Added and Recently Finished
- Currently Listening always visible and centered
- Responsive design for smartphone, tablet, and desktop
- Link to Google Sheets at bottom of page

#### 4. Music Integration
- Maintain Apple Music and Spotify embed functionality
- Preserve existing link styling (can be restyled for design cohesion)
- Ensure embeds work across all devices

#### 5. Build Process
- Generate build folder with static files
- Create separate Git branches (main for source, build for deployment)
- Maintain credential security (never commit sensitive files)
- Automated timestamped commits
- Generate README files for both source and build

### Non-Functional Requirements

#### 1. Performance
- Fast loading times across all devices
- Optimized images and assets
- Minimal JavaScript for interactions

#### 2. Design
- Implement LUFS brand colors:
  - TEAL: #78BEBA
  - RED: #D35233
  - YELLOW: #E7B225
  - BLUE: #2069af
  - BLACK: #111111
  - WHITE: #fbf9e2
- Dynamic/animated background elements
- Skeumorphic design language
- Clean, minimal aesthetic with focus on album covers

#### 3. Accessibility
- Proper semantic HTML
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance

#### 4. Security
- Credential files never committed to Git
- Secure build process
- No sensitive data in client-side code

### Technical Requirements

#### 1. Technology Stack
- **Backend**: Python 3.11+ with gspread library
- **Frontend**: HTML5, CSS3, JavaScript (minimal)
- **Build**: Bash script with Git integration
- **Deployment**: Static file hosting

#### 2. Dependencies
- Google Sheets API integration
- Apple Music and Spotify embed support
- Git version control
- Python virtual environment

#### 3. Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Responsive design for all screen sizes

### Design Requirements

#### 1. Visual Elements
- Custom favicon SVG representing "album du jour"
- Dynamic background (moving/waving elements)
- Gradient borders inspired by echobridge.lufs.audio
- Consistent typography and spacing

#### 2. Layout
- Header with site title and statistics
- Prominent Currently Listening section
- Collapsible sections for other content
- Footer with LUFS branding and Google Sheets link

#### 3. Responsive Behavior
- Mobile-first design approach
- Flexible grid layouts
- Touch-friendly interactions
- Optimized embed sizes for different screens

### Content Requirements

#### 1. Data Sources
- Google Sheets: "2025-media" spreadsheet
- CSV export with columns: Music, Apple Music Link, Spotify Link, Status, Date Added, Date Finished, Rating
- Real-time data fetching via Google Sheets API

#### 2. Content Display
- Album title and artist name
- Album artwork (from music service embeds)
- Music service links (Apple Music, Spotify)
- Date information where available
- Rating display (🌞 emoji)

### Success Metrics

#### 1. Technical Metrics
- Build process success rate: 100%
- Page load time: < 3 seconds
- Mobile responsiveness score: 95+
- Accessibility score: 90+

#### 2. User Experience Metrics
- Visual appeal improvement (subjective assessment)
- Functional completeness (all requirements met)
- Cross-device compatibility
- Documentation completeness

### Constraints and Assumptions

#### 1. Constraints
- Must maintain existing Google Sheets integration
- Cannot modify credential file locations
- Must preserve Apple Music and Spotify functionality
- Static site generation only (no server-side processing)

#### 2. Assumptions
- Google Sheets API access remains available
- Music service embed APIs remain functional
- Git repository structure can be modified
- User has necessary development environment setup

### Risk Assessment

#### 1. Technical Risks
- **API Changes**: Music service embed formats may change
- **Build Process**: Complex Git operations may fail
- **Data Format**: Google Sheets structure changes

#### 2. Mitigation Strategies
- Comprehensive testing of embed functionality
- Robust error handling in build scripts
- Flexible data parsing with fallback options
- Regular backups of working configurations

### Timeline and Milestones

#### Phase 1: Analysis and Planning (Complete)
- Requirements gathering
- Current state analysis
- Technical planning

#### Phase 2: Design Research and Asset Creation
- Brand research and inspiration gathering
- Favicon design and creation
- Visual mockups and prototypes

#### Phase 3: Backend Logic Enhancement
- CSV parsing and timestamp handling
- Data sorting and filtering logic
- Album categorization improvements

#### Phase 4: Frontend Redesign and Styling
- HTML structure updates
- CSS design implementation
- JavaScript for interactions
- Responsive design optimization

#### Phase 5: Build Process Improvement
- Build script enhancement
- Git workflow optimization
- Credential security improvements

#### Phase 6: Documentation Creation
- Source code documentation
- Build process documentation
- User guide creation

#### Phase 7: Testing and Delivery
- Cross-device testing
- Functionality verification
- Final package delivery

### Deliverables

1. **Enhanced Website**
   - Redesigned HTML/CSS/JS files
   - Improved Python build script
   - Updated build process script

2. **Assets**
   - Custom favicon SVG
   - Brand-consistent visual elements
   - Optimized images and graphics

3. **Documentation**
   - Source code README
   - Build process README
   - Technical documentation

4. **Deployment Package**
   - Complete source code
   - Build artifacts
   - Configuration files
   - Documentation bundle

### Approval and Sign-off

This PRD serves as the foundation for the Album du Jour website enhancement project. All requirements and specifications outlined above have been derived from the user's detailed requirements and analysis of the existing system.

**Next Steps:**
1. Review and approve PRD
2. Proceed with Technical Design Document (TDD)
3. Begin implementation phases

---

*Document Version: 1.0*  
*Last Updated: June 23, 2025*  
*Status: Draft - Pending Approval*

