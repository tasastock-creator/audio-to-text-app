# Static hosting setup

This app is now intended to be hosted as a plain static website.

## What you need

- `index.html`
- `icon-192.png`
- `icon-512.png`

## Best hosting options

1. GitHub Pages
2. Netlify
3. Vercel static site

## GitHub Pages

1. Create a GitHub repository.
2. Upload the files in this folder.
3. In repository settings, turn on GitHub Pages for the main branch.
4. Open the published HTTPS URL on your phone or computer.

## Netlify

1. Drag and drop this folder into Netlify.
2. Netlify will publish a public HTTPS link.
3. Open that link on any device.

## Why static hosting is required

This app uses a browser AI worker. It will not reliably run from `file:///` on disk.
It needs to be opened from `http://` or `https://`.

## Notes

- The first model download still needs internet.
- After that, the browser caches the model and repeat use is faster.
- The transcription runs in the browser after the page loads.
