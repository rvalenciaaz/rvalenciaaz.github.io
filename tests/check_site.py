"""Check the built site's pages, accessibility basics and local navigation."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1] / "_site"


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.ids = set()
        self.links = []
        self.h1 = 0
        self.main = 0
        self.redirect = False
        self.title = False
        self.lang = False
        self.portraits = 0
        self.current_navigation = []
        self.images = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate id in {self.path}: {attrs['id']}"
            self.ids.add(attrs["id"])
        self.h1 += tag == "h1"
        self.main += tag == "main"
        self.title |= tag == "title"
        self.lang |= tag == "html" and attrs.get("lang") == "en"
        self.redirect |= tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh"
        if tag == "a" and attrs.get("aria-current") == "page":
            self.current_navigation.append(attrs.get("href"))
        if tag == "meta" and attrs.get("property") == "og:image":
            self.links.append(attrs["content"])
        if tag == "img":
            self.images.append(attrs)
            self.portraits += urlsplit(attrs.get("src", "")).path.endswith("/assets/images/profilepic-desktop.webp")
            assert "alt" in attrs, f"Missing image alt in {self.path}"
            assert attrs.get("width") and attrs.get("height"), f"Image dimensions missing in {self.path}"
        if attrs.get("srcset"):
            if tag == "img":
                assert attrs.get("sizes"), f"Responsive image sizes missing in {self.path}"
            self.links.extend(candidate.strip().split()[0] for candidate in attrs["srcset"].split(","))
        for attr in ("href", "src"):
            if attrs.get(attr):
                self.links.append(attrs[attr])


def resolve(url, source):
    path = unquote(urlsplit(url).path)
    target = ROOT / path.lstrip("/") if path.startswith("/") else source.parent / path
    if not path:
        return source
    if target.is_dir():
        target /= "index.html"
    if not target.exists() and target.with_suffix(".html").exists():
        target = target.with_suffix(".html")
    assert target.exists(), f"Broken local link in {source.relative_to(ROOT)}: {url}"
    return target


assert ROOT.exists(), "Build the site first: npm run build"
required = ["index.html", "publications/index.html", "portfolio/index.html",
            "talks/index.html", "year-archive/index.html", "sitemap/index.html", "cv/index.html",
            "404.html", "feed.xml", "sitemap.xml"]
for path in required:
    assert (ROOT / path).is_file(), f"Missing required page: {path}"
assert not (ROOT / "terms/index.html").exists(), "Removed Privacy & credits page is still published"
for path in ("files", "images", "markdown_generator", "talkmap", "assets/js/plugins"):
    assert not (ROOT / path).exists(), f"Obsolete content is still published: {path}"
assert {path.name for path in (ROOT / "assets/css").iterdir()} == {"site.css"}, "Unused stylesheets are still published"
assert {path.name for path in (ROOT / "assets/js").iterdir()} == {"site.js", "math.js"}, "Unused scripts are still published"
assert {path.name for path in (ROOT / "assets/fonts").iterdir()} == {"roboto"}, "Unused icon fonts are still published"
assert (ROOT / "assets/images/profilepic.webp").stat().st_size < 150_000, "The small portrait exceeds 150 KB"
for kind in ("desktop", "mobile"):
    assert (ROOT / f"assets/images/profilepic-{kind}.webp").stat().st_size < 35_000, f"The {kind} portrait exceeds 35 KB"
assert (ROOT / "assets/fonts/roboto/roboto-normal-latin.woff2").stat().st_size < 40_000, "The main font exceeds 40 KB"

pages = {}
for path in ROOT.rglob("*.html"):
    page = Page(path)
    pages[path] = page
    assert page.portraits == int(path == ROOT / "index.html"), f"Portrait must appear only on the homepage: {path}"
    assert page.title, f"Missing page title in {path}"
    if not page.redirect:
        assert page.lang, f"Missing page language in {path}"
        assert page.h1 == 1 and page.main == 1, f"Missing/duplicate landmark in {path}"
        assert "site-nav" in page.ids, f"Missing site navigation in {path}"
        expected_navigation = {
            "index.html": "/", "cv": "/", "publications": "/publications/",
            "publication": "/publications/", "talks": "/talks/",
            "portfolio": "/portfolio/", "year-archive": "/year-archive/", "posts": "/year-archive/"
        }.get(path.relative_to(ROOT).parts[0])
        assert page.current_navigation == ([expected_navigation] if expected_navigation else []), f"Wrong current navigation in {path}"

checked_links = 0
for source, page in pages.items():
    for url in page.links:
        parsed = urlsplit(url)
        if parsed.scheme and parsed.scheme not in ("http", "https"):
            continue
        if parsed.netloc and parsed.netloc not in ("rvalenciaaz.github.io", "localhost:4000"):
            continue
        target = resolve(url, source)
        if parsed.fragment and target in pages:
            assert unquote(parsed.fragment) in pages[target].ids, f"Broken anchor in {source}: {url}"
        checked_links += 1

for stylesheet in ROOT.rglob("*.css"):
    for url in re.findall(r"url\(([^)]+)\)", stylesheet.read_text()):
        url = url.strip(" \"'")
        if not urlsplit(url).scheme and not urlsplit(url).netloc:
            resolve(url, stylesheet)

project_images = pages[ROOT / "portfolio/index.html"].images
assert project_images[0].get("loading") == "eager" and project_images[0].get("fetchpriority") == "high", "Prioritize the first visible project image"
assert all(image.get("loading") == "lazy" for image in project_images[1:]), "Defer later project images"
for path, page in pages.items():
    if path.relative_to(ROOT).parts[0] == "portfolio":
        assert all(image.get("srcset") and image.get("sizes") for image in page.images), f"Project images must be responsive: {path}"

for path in ("cv/index.html", "index.html", "publications/index.html"):
    text = (ROOT / path).read_text()
    for placeholder in ("This paper is about the number 1", "University of Testing", "Upcoming conferences"):
        assert placeholder not in text, f"Template/stale copy remains in {path}"

assert len(list((ROOT / "portfolio").glob("*/index.html"))) == 4, "Expected all four project pages"
for project in (ROOT / "portfolio").glob("*/index.html"):
    assert 'class="article-meta"' not in project.read_text(), f"Undated project acquired a build date: {project}"
for alias in ("resume.html", "resume/index.html", "about.html", "about/index.html", "notes/index.html"):
    assert pages[ROOT / alias].redirect, f"Missing historical redirect: {alias}"
assert not (ROOT / "posts/2026/06/math-1/index.html").exists(), "Removed theorem post is still published"
for removed in ("posts/2015/08/roadmap-qm/index.html", "posts/2025/08/qm-1/index.html"):
    assert not (ROOT / removed).exists(), f"Removed blog post is still published: {removed}"
posts = list((ROOT / "posts").rglob("*.html"))
assert not posts, "Hidden blog posts must not be published"
for path in ("year-archive/index.html", "sitemap/index.html", "feed.xml", "sitemap.xml"):
    assert "/posts/2025/08/plancks-fortunate-guess/" not in (ROOT / path).read_text(), f"Hidden Planck post is listed in {path}"
for page in ("index.html", "cv/index.html"):
    assert "Ellison Institute of Technology" in (ROOT / page).read_text(), f"Outdated role in {page}"
assert "@earlham.ac.uk" not in (ROOT / "index.html").read_text(), "Obsolete contact email remains"
assert not (ROOT / "posts/2025/08/plancks-fortunate-guess/index.html").exists(), "Hidden Planck post is still published"
assert len(list((ROOT / "publication").rglob("*.html"))) == 7, "Missing an updated publication or thesis"
assert (ROOT / "talks/multimodal-ai-2026/index.html").exists(), "Missing 2026 award-winning pitch"
print(f"Passed: {len(pages)} pages, {checked_links} local links, image/landmark checks and content checks.")
