# Leafland App — Prototype

Phone app prototype for Leafland: promotions, tree catalogue with specs and grades, Tree Finder, favourites and a quote list.
**Ordering is disabled.** "Request quote", call, email and booking only show a "Prototype only" message. Tree details, grades, stock and prices are a copy from leafland.co.nz (Nov 2026). Promotions, discounts and freight rates are sample data.

## Build the APK with GitHub (no Android Studio needed)

1. Create a new repository on GitHub (e.g. `leafland-app`).
2. Upload **everything in this folder**, including the hidden `.github` folder.
   - Easiest way: on the repo page click **Add file → Upload files** and drag the folder contents in.
   - If the `.github` folder doesn't upload by drag-and-drop, create the file by hand:
     **Add file → Create new file**, name it `.github/workflows/build-apk.yml`, and paste in the contents of that file.
3. Go to the **Actions** tab. The "Build Android APK" job starts automatically (or click **Run workflow**).
4. When it finishes (about 5 minutes), open the run and download **leafland-prototype-apk** under *Artifacts*.
5. Unzip it to get `app-debug.apk`, copy it to an Android phone and open it (allow "Install unknown apps" when asked).

## Editing the app

- `www/index.html`: the app (layout, promotions list `PROMOS`, freight rates `REGIONS`, colours in `:root`).
- `www/data.js`: the 22 trees. Photos, sizes, descriptions, plant details, seasonal colour, grades, stock and prices
  all come from the tree pages on leafland.co.nz (prices exclude GST). `cats`, `special` (sample discount %) and `best`
  are prototype settings you can change.
- `www/img.zip`: logo, photos and tree-size drawings (unpacked automatically during the build, so the app works offline). To preview on a computer, unzip it inside `www` and open `www/index.html`.
- `tools/scrape_leafland.py`: the script used to pull tree data and photos from the website.

Push a change and GitHub builds a new APK.

## Files
- `www/index.html` — the whole app
- `capacitor.config.json` — app name and ID (`nz.co.leafland.prototype`)
- `assets/` — app icon and splash screen
- `.github/workflows/build-apk.yml` — the GitHub build
