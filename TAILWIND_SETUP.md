# Tailwind CSS Setup for Atelimatch

This project uses Tailwind CSS for styling. The CSS is compiled from `static/css/input.css` to `static/css/output.css` using PostCSS.

## Installation

### 1. Install Node.js dependencies
```bash
npm install
```

### 2. Build Tailwind CSS
```bash
# One-time build
npm run tailwind:build

# Watch mode (for development)
npm run tailwind:watch
```

## Development Workflow

### Option 1: Watch Mode (Recommended)
In a separate terminal, run the watch command to automatically rebuild CSS when you change files:
```bash
npm run tailwind:watch
```

### Option 2: Manual Build
After making HTML changes, manually rebuild:
```bash
npm run tailwind:build
```

## Configuration

- **Tailwind Config**: `tailwind.config.js` - Configure Tailwind theme and plugins
- **PostCSS Config**: `postcss.config.js` - Configure PostCSS processors
- **Input CSS**: `static/css/input.css` - Add custom CSS here
- **Output CSS**: `static/css/output.css` - Auto-generated, do NOT edit manually

## Template Paths Scanned

The Tailwind configuration scans these directories for Tailwind classes:
- `./templates/**/*.html`
- `./atelie/templates/**/*.html`
- `./ia/templates/**/*.html`
- `./usuarios/templates/**/*.html`

Add new template directories to `tailwind.config.js` if needed.

## Production

Before deploying to production:
1. Run `npm run tailwind:build` to generate optimized CSS
2. The CSS file is automatically minified and only includes used classes
3. Commit `static/css/output.css` to version control
