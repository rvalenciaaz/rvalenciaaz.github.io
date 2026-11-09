# Ricardo Valencia Albornoz

A personal academic website built with Jekyll, inspired by the original AcademicPages layout: a profile sidebar, clear navigation and readable content. It uses locally served Roboto and 18px body text. The main About me homepage shows a small portrait with a navy role panel, a personal biography and contrasting apricot and pale-blue achievement panels. Other pages show only the profile links in the sidebar; the portrait and navy panel appear on the homepage only. The name is the only wordmark: there is no monogram or decorative logo. Archive entries respond to hover and keyboard focus; motion respects the device’s reduced-motion setting. The homepage scrolls as updates are added, including on smaller viewports and zoomed pages, to preserve readable text.

## Run locally

From this directory:

```sh
npm run dev
```

Open **http://localhost:4000**. Jekyll watches for edits and rebuilds the pages; refresh the browser to see changes. Restart the server after changing `_config.yml`.

The dependencies are already installed locally in this workspace. On a fresh checkout, install Ruby 3.2 or newer, Bundler and the Ruby development headers, then run:

```sh
bundle install
npm run dev
```

The npm commands are shortcuts; there are no npm packages to install. The KaTeX browser distribution is vendored in the repository. `bin/site` accepts either `bundle` or Ubuntu’s `bundle3.2`. You can also run `bundle exec jekyll serve --config _config.yml,_config.dev.yml` directly.

## Build and check

```sh
npm run build
npm run check
```

The production command sets `JEKYLL_ENV=production` and generates the website in `_site/`. The check uses Python’s standard library to verify local links and anchors, responsive image sources, CSS font URLs, image descriptions and dimensions, page landmarks, current navigation, required content, and the removal of obsolete files. All content pages must be reachable from the homepage, and published assets must be referenced by HTML or CSS; the custom 404 page and required font license are exempt. PDFs and unused public files are rejected. The check also enforces image loading priorities, keeps each displayed portrait below 35 KB and the main font below 40 KB, and validates the saved Planck draft’s LaTeX expressions using the vendored KaTeX renderer. `_site/`, local dependencies and preview screenshots are ignored by Git.

Desktop and mobile layouts were reviewed in Chrome. Browser checks covered the main pages, project details, the now-unpublished Planck blog post and profile/contact pages at desktop and mobile sizes, WCAG A/AA checks with axe, image loading, JavaScript errors and keyboard operation of the mobile menu. Display equations can be scrolled with the keyboard when they are wider than the screen. Additional layout checks cover widths from 320 to 1920 pixels, plus navigation with JavaScript disabled. Review screenshots are in the local `previews/` directory.

The security checks in `npm run check` enforce the current static-site boundaries: local active resources, HTTPS links, fixed internal redirects, no inline event handlers, forms or embedded content, and an allowlist of published file types. Negative controls verify that unsafe protocols, obfuscated resource URLs, unexpected scripts and CSS imports are rejected. TeX tests cover blocked HTML/link/image commands and the recursive-macro limit; the browser renderer explicitly keeps trusted TeX features disabled. Changes that introduce new active content or public file types need a review of this policy. Browser probes, credential scans, dependency advisories and GitHub settings are checked separately.

Every page, including historical aliases, receives the shared Content Security Policy in `_includes/security-policy.html`. It restricts scripts to this origin and blocks inline JavaScript, evaluation, outgoing connections, plugins and form submissions. Inline CSS remains available for KaTeX. Aliases use the plugin's supported custom redirect layout with a fixed meta-refresh and fallback link, without JavaScript. This HTML policy cannot prevent other sites from framing the page; that protection requires an HTTP response header. These local changes take effect on the public website only after deployment.

## Edit content

| Content | Location |
| --- | --- |
| Homepage / About me | `_pages/home.html` |
| Publications | `_publications/` |
| Projects | `_portfolio/` |
| Talks | `_talks/` |
| Hidden Planck draft | `_posts/2025-08-26-blog-post-4.md` |
| Navigation | `_data/navigation.yml` |
| Profile and site settings | `_config.yml` |
| Profile photographs | `assets/images/profilepic-{desktop,mobile}.webp` |
| Shared layouts | `_layouts/` |
| Design | `assets/css/site.css` |
| Mobile menu | `assets/js/site.js` |

Projects use `image`, `topic` and a short `excerpt` in their front matter; their full description and photographs with descriptive `alt` text belong in the HTML body. Project photographs keep a 1400px original plus 640px and 1000px WebP variants. Native `srcset` and `sizes` select the appropriate file; the first card loads with high priority and later cards load lazily. The variants are committed static assets, so GitHub Pages needs no image-processing step. The Planck post remains an unpublished Markdown draft with `published: false` in `_posts/2025-08-26-blog-post-4.md`. No blog posts are currently published, so the empty Blog section and feed have been removed.

Existing publication, talk and project links are retained. The separate biography, research-background, empty Blog and unlinked HTML sitemap pages have been removed. Their old URLs redirect to the homepage with a `noindex` directive. The generated XML sitemap remains at `/sitemap.xml`.

Unused AcademicPages templates, example content, generator notebooks, old downloads and unreferenced photographs have been removed. The homepage contains the research background, with the thesis listed under Publications. LinkedIn is the contact method. A native `<picture>` selects a 400×489 mobile portrait or a 600×391 desktop portrait. These crops preserve the original framing without downloading pixels hidden by CSS zoom; the uncropped `assets/images/profilepic.webp` remains the social-preview image. Project photographs also use WebP files in `assets/images/`.

Roboto is served locally from `assets/fonts/roboto/`, with its font declarations in `assets/css/site.css` to avoid a separate blocking stylesheet request. Its files omit unused light weights below 400 while preserving all Latin and extended-Latin characters and the site's 400–700 weights. The retained upper range preserves the original interpolation and rendering. The font license remains beside the files. Portraits and fonts are committed assets; GitHub Pages needs no image or font processing. KaTeX and its mathematical fonts are retained in `assets/vendor/katex/` for the hidden Planck draft and local checks. That directory and `assets/js/math.js` are excluded from the public build while no math content is published. No font or math CDN is needed at runtime.

## LaTeX equations

The hidden Planck draft and all its math support are preserved. To publish it later, remove its `published: false` flag and the two math-asset exclusions in `_config.yml`, then update the publication checks to allow its route and linked assets.

Add `math: true` to a post’s front matter. The local KaTeX scripts render conventional LaTeX delimiters. To preserve backslashes through Markdown processing, use:

```html
<span class="math" markdown="0">\(E=h\nu\)</span>

<div class="equation" tabindex="0">
\[
u_\nu(T)=\frac{8\pi h\nu^3}{c^3\left(e^{h\nu/(k_{\mathrm B}T)}-1\right)}
\]
</div>
```

The display wrapper lets keyboard users scroll formulas that exceed a narrow screen. KaTeX emits visual HTML and accessible MathML. Typesetting runs in the browser using JavaScript; the source remains readable if JavaScript is disabled. Use `aligned` for long derivations. `npm run check` rejects invalid TeX.

## GitHub Pages

This is a native Jekyll site for the `rvalenciaaz.github.io` user repository, with its production URL and empty `baseurl` in `_config.yml`. Publish the source files from the `main` branch and `/(root)` folder in GitHub Pages settings; keep `_site/` ignored. The explicit `theme: null` prevents GitHub Pages from adding its default theme. All optimizations use static files and browser features supported by the built-in Jekyll build, with no custom plugins, npm dependencies or additional deployment service. The preview configuration is only for local development.

## Credits

The original site used [AcademicPages](https://github.com/academicpages/academicpages.github.io), based on [Minimal Mistakes](https://github.com/mmistakes/minimal-mistakes). Its MIT license is retained in `LICENSE`. Roboto’s SIL Open Font License and KaTeX’s MIT license are retained beside their assets. KaTeX is pinned to version 0.19.1. Individual project pages credit their source designs.
