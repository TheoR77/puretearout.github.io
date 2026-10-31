# Pure Tearout

Add a text: drop a `.md` file into `texts/` and push to `main`. The site rebuilds automatically.

- The page title is the first `# Heading` in the file (or the filename if there is none).
- The timestamp is when the file was first committed.
- The page URL is `texts/<filename>.html`.

Formatting (line spacing, justification, fonts, the grey note at the end of each text) lives in `format.yml`.

Preview locally: `pip install markdown pyyaml && python build.py`, then open `_site/index.html`.

One-time setup on GitHub: **Settings → Pages → Source: GitHub Actions**.
