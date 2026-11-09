"""Check the static site's publication and active-content boundaries."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1] / "_site"
HOST = "rvalenciaaz.github.io"

def check_csp(value):
    assert value, "Missing Content Security Policy"
    directives = {}
    for part in value.split(";"):
        fields = part.split()
        if fields:
            assert fields[0] not in directives, "Duplicate CSP directive"
            directives[fields[0]] = set(fields[1:])
    expected = {
        "default-src": {"'self'"},
        "script-src": {"'self'"},
        "style-src": {"'self'", "'unsafe-inline'"},
        "img-src": {"'self'", "data:"},
        "object-src": {"'none'"},
        "base-uri": {"'none'"},
        "form-action": {"'none'"},
        "connect-src": {"'none'"},
    }
    assert directives == expected, "Changed Content Security Policy requires review"


def check_url(value, resource=False):
    value = re.sub(r"[\x00-\x20\x7f]", "", value)
    assert "\\" not in value, "Backslashes can change a browser URL's origin"
    if value == "data:," and resource:
        return
    parsed = urlsplit(value)
    allowed = ("", "https") if resource else ("", "https", "mailto", "tel")
    assert parsed.scheme in allowed, "Unsafe URL protocol"
    assert parsed.scheme != "https" or parsed.netloc, "HTTPS URLs must include a host"
    assert not value.startswith("//"), "Use explicit HTTPS URLs"
    assert parsed.username is None and parsed.password is None, "Credentials in URL"
    if resource:
        assert parsed.netloc in ("", HOST), "Unexpected third-party resource"


class SecurityPage(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.csp = None
        self.in_head = False
        self.head_started = False
        self.body_started = False
        self.in_title = False
        self.resources_started = False
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        assert not self.in_title, "Markup in the title can conceal an ineffective CSP"
        names = [name for name, _ in attrs]
        assert len(names) == len(set(names)), "Duplicate HTML attributes"
        attrs = dict(attrs)
        if tag == "head":
            assert not self.head_started and not self.body_started, "Unexpected document head"
            self.head_started = True
            self.in_head = True
        elif tag == "body":
            self.body_started = True
            self.in_head = False
        if self.in_head:
            assert tag in ("head", "meta", "title", "link", "script"), "Unexpected element in document head"
        if tag == "title":
            self.in_title = True
        assert tag not in ("base", "style", "form", "iframe", "frame", "frameset", "object", "embed"), "Unexpected active content"
        assert not any(name.startswith("on") or name in ("srcdoc", "style") for name in attrs), "Inline handler, style or embedded HTML"
        for name in ("href", "xlink:href", "src", "poster"):
            if attrs.get(name):
                check_url(attrs[name], resource=tag != "a")
        for candidate in attrs.get("srcset", "").split(","):
            if candidate.strip():
                check_url(candidate.strip().split()[0], resource=True)
        if tag == "meta" and attrs.get("property") == "og:image":
            check_url(attrs["content"], resource=True)
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh":
            raise AssertionError("Unexpected redirect")
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "content-security-policy":
            assert self.in_head and not self.resources_started, "CSP must precede resources inside the head"
            assert self.csp is None, "Duplicate Content Security Policy"
            self.csp = attrs.get("content")
        if tag == "script":
            assert attrs.get("src"), "Inline JavaScript is disabled"
        if tag in ("script", "link", "img", "source"):
            self.resources_started = True

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        elif tag == "title":
            self.in_title = False


def check_css(css):
    assert "\\" not in css, "Escaped CSS requires security review"
    assert not re.search(r"@import\b|expression\s*\(", css, re.I), "Unexpected CSS import or executable expression"
    for value in re.findall(r"url\(([^)]+)\)", css, re.I):
        assert "\\" not in value, "Use plain asset URLs"
        check_url(value.strip(" \"'"), resource=True)


def rejected(check, value):
    try:
        check(value)
    except (AssertionError, ValueError):
        return
    raise AssertionError("A negative security control was accepted")


SecurityPage('<script src="/assets/js/site.js"></script><a href="https://example.org/">Link</a>')
check_css("@font-face{src:url(../fonts/roboto/roboto-normal-latin.woff2)}")
controls = 0
for html in (
    '<link rel="canonical" href="https://rvalenciaaz.github.io/"><meta http-equiv="refresh" content="0; URL=https://rvalenciaaz.github.io/">',
    '<script src="https://example.invalid/payload.js"></script>',
    '<script>alert(1)</script>',
    '<img src="/image.webp" onerror="alert(1)">',
    '<a href="JaVaScRiPt:alert(1)">Link</a>',
    '<a href="java&#x09;script:alert(1)">Link</a>',
    '<a href="data:text/html,payload">Link</a>',
    '<img src="http://rvalenciaaz.github.io/image.webp">',
    '<img src="//example.invalid/image.webp">',
    r'<img src="https:\example.invalid/image.webp">',
    '<script src="https:example.invalid/probe.js"></script>',
    '<base href="https://example.invalid/">',
    '<iframe srcdoc="payload"></iframe>',
    '<form action="/submit"></form>',
    '<style>@import "https://example.invalid/style.css";</style>',
    '<p style="background:url(https://example.invalid/pixel)">Text</p>',
    '<meta http-equiv="refresh" content="0; URL=https://example.invalid/">',
    '<a href="javascript:alert(1)" href="/safe/">Link</a>',
    '<link rel="canonical" href="https://rvalenciaaz.github.io/"><meta http-equiv="refresh" content="0; url=https://example.invalid/" content="0; url=https://rvalenciaaz.github.io/">',
    '<svg><image xlink:href="https://example.invalid/pixel"></image></svg>',
    '<body><meta http-equiv="Content-Security-Policy" content="default-src \'self\'"></body>',
    '<head><script src="/assets/js/site.js"></script><meta http-equiv="Content-Security-Policy" content="default-src \'self\'"></head>',
    '<head><div>Text</div><meta http-equiv="Content-Security-Policy" content="default-src \'self\'"></head>',
    '<body><head><meta http-equiv="Content-Security-Policy" content="default-src \'self\'"></head></body>',
):
    rejected(SecurityPage, html)
    controls += 1
# A policy inside a title is text, not an effective document policy.
rejected(lambda html: check_csp(SecurityPage(html).csp), '<head><title><meta http-equiv="Content-Security-Policy" content="default-src \'self\'"></title></head>')
controls += 1
for css in ('@import "https://example.invalid/style.css";', 'a{background:url(https://example.invalid/pixel)}', 'a{background:URL(https://example.invalid/pixel)}', r'a{background:url(\68 ttps://example.invalid/pixel)}', r'@\69mport "https://example.invalid/style.css";'):
    rejected(check_css, css)
    controls += 1

assert ROOT.is_dir(), "Build the site first: npm run build"
pages = 0
files = 0
for path in ROOT.rglob("*"):
    relative = path.relative_to(ROOT)
    assert not path.is_symlink(), f"Published symlink: {relative}"
    assert not any(part.startswith((".", "_")) for part in relative.parts), f"Published hidden/source path: {relative}"
    assert relative.parts[0] not in ("tests", "bin", "previews", "vendor", "node_modules", "files", "images"), f"Published non-site directory: {relative}"
    if not path.is_file():
        continue
    files += 1
    if relative.parts[0] == "assets":
        assert path.suffix in (".css", ".js", ".webp", ".woff2", ".woff", ".ttf", ".txt") or path.name == "LICENSE", f"Unexpected asset type: {relative}"
    else:
        assert path.suffix == ".html" or str(relative) in ("sitemap.xml", "robots.txt"), f"Unexpected published file: {relative}"
    if path.suffix == ".html":
        try:
            page = SecurityPage(path.read_text())
            check_csp(page.csp)
        except (AssertionError, ValueError) as error:
            raise AssertionError(f"{relative}: {error}") from error
        pages += 1
    elif path.suffix == ".css":
        check_css(path.read_text())
print(f"Passed: {pages} pages, {files} published files, local resource boundaries, no redirects and {controls} negative security controls.")
