# Princesse Lara — AI Agent Context Document

This document provides comprehensive context for any AI agent working on the **Princesse Lara** project. Read this carefully to understand the architecture, design systems, and pending tasks before making any modifications.

## 1. Project Overview
**Princesse Lara** is a luxury editorial and booking website focused on heels, legs, and nylon content. It features a 5-page core structure plus legal pages, emphasizing direct booking, strict content protection, and a premium aesthetic.

- **Stack**: Plain HTML, CSS, Vanilla JavaScript.
- **Build System**: No modern build step (e.g., Webpack, Vite). Pages are generated via Python scripts (`build.py`, `pages.py`, `legal_pages.py`) which output the static HTML. The resulting HTML files are fully functional and require no server-side rendering or complex deployment pipelines.
- **Hosting Target**: Designed to be deployed as static files to GitHub Pages, Netlify, or Cloudflare Pages.

## 2. Directory & File Structure
The project consists of 14 static HTML pages and a simple `assets` directory.
- `index.html`, `rules.html`, `services.html`, `gallery.html`, `brands.html`, `book.html`, `about.html`, `reviews.html`, `faq.html`, `journal.html`, `contact.html`
- Legal pages: `privacy.html`, `terms.html`, `cookies.html`, `content-notice.html`
- `assets/css/styles.css`: Contains the entire design system and the 3-theme engine.
- `assets/js/main.js`: Contains all interactivity (Vanilla JS, no dependencies).
- `assets/img/`: Contains SVG marks, logos, and OG share images.

## 3. Core Features & Interactivity (`main.js`)
The site avoids heavy frameworks, relying on a robust `main.js` for key interactions:
- **Theme Engine ("The Sheen")**: A three-theme system (Verre, Peau, Écailles). Users can toggle themes, and the selection is saved to `localStorage` (`vq_theme`).
- **Age Gate**: An 18+ verification overlay. Approval is stored in `localStorage` (`vq_age_verified`) with a 30-day expiry.
- **Cookie Consent**: A basic categorised consent banner saving preferences to `localStorage`.
- **Navigation Drawer**: Mobile-first sticky bottom bar with a slide-in drawer.
- **Content Protection**: Strict anti-right-click, anti-drag, and anti-save (Ctrl+S) listeners to protect imagery.
- **Other UI**: Intersection Observer-based scroll animations, stats counter animation, gallery tabs/lightbox, and a reviews carousel.

## 4. Design System & Aesthetics
- **Typography**: 
  - Display: **Fraunces** (Google Fonts)
  - Body: **Manrope**
  - Data/Labels: **JetBrains Mono**
- **Themes**: The CSS architecture uses data attributes on the `<html>` tag (`data-theme="verre|peau|ecailles"`) to switch CSS variables for colors, backgrounds, and "The Sheen" light-sweep effects.
- **Current State of Media**: Currently, the site uses gradient placeholder tiles. No real or AI-generated photography is in the repository. 

## 5. Pending "Production Note" Items (Phase 1-4 Build)
When working on this project, look for `PRODUCTION NOTE` comments in the HTML. The following elements are deliberately stubbed and represent the remaining work:
1. **Tally Forms**: Replace demo `<form>` elements with actual embedded Tally forms in `rules.html`, `services.html`, `brands.html`, and `contact.html`.
2. **Live Stats**: Currently hardcoded (e.g., 128K followers). Needs to be wired to Airtable via a GitHub Actions build step.
3. **Real Photography**: Drop in real, watermarked photos and remove the gradient placeholders in `gallery.html` and the homepage.
4. **Watermarking Pipeline**: Add a `sharp`-based GitHub Actions step once real photos exist.
5. **Instagram Handle**: Update all generic `https://instagram.com/` links to the actual handle.
6. **Domain Update**: Update the `BASE_URL` in the Python build scripts and regenerate the pages once a domain is selected.
7. **Legal Review**: Legal pages (`privacy.html`, `terms.html`, etc.) are drafts and MUST be reviewed by a lawyer before publishing.
8. **Phase 2 Add-ons**: Session-unique watermarking and certified age verification via Cloudflare Workers.

## 6. How to Edit
- **Minor Copy/HTML Tweaks**: You can edit the `.html` files directly for speed.
- **Global Changes (Header, Footer, Nav)**: Must be edited in the Python generator scripts (`build.py`, `pages.py`, `legal_pages.py`) and regenerated:
  ```bash
  python3 build.py
  python3 pages.py
  python3 legal_pages.py
  ```
*(Note: If the Python scripts are missing from the immediate directory, it means you are working with the static export. Request the generator files if global structural changes are required).*

## 7. SEO & GEO
The site includes fundamental SEO structures: `sitemap.xml`, `robots.txt`, `llms.txt`, Open Graph (OG) / Twitter cards, and Schema.org JSON-LD (Person/FAQPage). Ensure these remain intact and updated as content changes.
