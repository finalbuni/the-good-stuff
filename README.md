# the good stuff
A simple personal comics reader for https://finalbuni.github.io/the-good-stuff/.

## First upload
1. Create a GitHub repository named `the-good-stuff`, using the `main` branch.
2. Unzip this starter and upload the **contents** of its folder into the repository root. Include `.github/workflows/pages.yml` (hidden folders may need Command+Shift+Period in Finder).
3. Put chapter 1 images into `content/diamond-dust/chapters/1/` and chapter 2 images into `content/diamond-dust/chapters/2/`.
4. Use names such as `dd-ch1-1.webp`, `dd-ch1-2.webp`. Numbers sort numerically, so 10 follows 9. Supported images: WebP, PNG, JPG and JPEG. Filenames must match the series prefix and chapter folder number; malformed names stop the build with an explanation.
5. Add your cover as `content/diamond-dust/cover.webp` (or cover.jpg, cover.jpeg, cover.png). Until then, a title card fills its place.
6. In GitHub: Settings → Pages → Source → **GitHub Actions**. The included workflow builds and publishes on every push to main. Check the Actions tab for progress.

Empty chapter folders show an explicit setup message rather than invented panels. Once you upload images, that message disappears automatically. Remove their `.gitkeep` files if desired.

## Add a chapter
Create `content/diamond-dust/chapters/3/`, upload images named `dd-ch3-1.webp` etc., and commit. Chapter lists, dropdowns, previous/next links, and chapter counts update automatically. Navigation follows available chapters even if chapter numbers have gaps. Numbered chapters only in this first version.

## Add a series
Create `content/your-series/series.json`:
```json
{"title":"Your Series", "prefix":"ys", "completed":false}
```
Add `cover.webp` and numbered chapter folders inside `chapters/`. Use `ys-ch1-1.webp` etc. The homepage sorts titles alphabetically without regard to capitalization. Set `completed` to true to show “End of series” at the final chapter; otherwise it shows “Next chapter unavailable”.

## Preview on your computer
Python 3 is required. From this folder:
```sh
python3 build.py
python3 -m http.server 8000 --directory dist
```
Open http://localhost:8000. Stop with Control+C.

## Layout
Homepage → series → chapter. Navigation and chapter dropdowns appear above and below the panels. Phone images fill the screen; desktop images are centered, up to 800px wide. Covers use a 2:3 thumbnail frame; reading images retain their proportions. No tracking or external fonts. Edit `assets/style.css` to adjust appearance.

The source and deployed panels are public. This package has no uploaded panels yet and has not been deployed to your GitHub account.
