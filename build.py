#!/usr/bin/env python3
"""Static site generator for toolnookz.com.

Usage:  pip install -r requirements.txt && python build.py
Reads src/ (site.json, categories.json, data/apps/*.json, templates/, static/)
and writes the finished site to docs/ (served by GitHub Pages).
"""
import json, shutil, sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
SRC, OUT = ROOT / "src", ROOT / "docs"

# What each permission means, in plain language. Used on the app page and in its privacy policy.
PERMISSIONS = {
    "notifications": ("Notifications and alarms",
        "Used only to show the reminders, timers and alerts you set up in the app. You can turn them off in Android settings at any time."),
    "camera": ("Camera",
        "Used only while you are scanning a code. Camera images are processed on your device and are not saved or sent anywhere by us."),
    "photos": ("Photos and images you choose",
        "The app opens only the images you pick (or, where noted in the app, photos you take). They are processed on your device."),
    "files": ("Files and folders you choose",
        "The app reads or writes only the files and folders you select using the Android file picker. Processing happens on your device."),
}
REQUIRED_FIELDS = ["id", "slug", "name", "category", "tagline", "description", "features", "privacy"]


def load():
    site = json.loads((SRC / "site.json").read_text())
    cats = json.loads((SRC / "categories.json").read_text())
    cat_by = {c["slug"]: c for c in cats}
    apps = []
    for f in sorted((SRC / "data" / "apps").glob("*.json")):
        a = json.loads(f.read_text())
        miss = [k for k in REQUIRED_FIELDS if k not in a]
        if miss: sys.exit(f"{f.name}: missing {miss}")
        if a["category"] not in cat_by: sys.exit(f"{f.name}: unknown category {a['category']}")
        for p in a["privacy"].get("permissions", []):
            if p not in PERMISSIONS: sys.exit(f"{f.name}: unknown permission {p}")
        a["cat"] = cat_by[a["category"]]
        apps.append(a)
    slugs = [a["slug"] for a in apps]
    if len(slugs) != len(set(slugs)): sys.exit("duplicate app slugs")
    return site, cats, apps


def main():
    site, cats, apps = load()
    env = Environment(loader=FileSystemLoader(SRC / "templates"),
                      autoescape=select_autoescape(["html", "xml"]), trim_blocks=True, lstrip_blocks=True)
    used = sorted({a["category"] for a in apps})
    ctx = dict(site=site, cats=[c for c in cats if c["slug"] in used], apps=apps, perms=PERMISSIONS)

    if OUT.exists():
        for p in OUT.iterdir():
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    OUT.mkdir()
    shutil.copytree(SRC / "static", OUT / "assets")
    (OUT / "CNAME").write_text(site["domain"] + "\n")
    (OUT / ".nojekyll").write_text("")

    def write(path, tpl, **kw):
        p = OUT / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(env.get_template(tpl).render(**ctx, **kw), encoding="utf-8")

    write("index.html", "home.html", page="home", title=None,
          featured=[a for a in apps if a.get("featured")][:4])
    write("apps/index.html", "apps.html", page="apps", title="All Apps")
    write("privacy/index.html", "privacy_index.html", page="privacy", title="Privacy Policy")
    write("terms/index.html", "terms.html", page="terms", title="Terms & Conditions")
    write("contact/index.html", "contact.html", page="contact", title="Contact")
    write("404.html", "404.html", page="", title="Page not found")
    for a in apps:
        related = [r for r in apps if r["category"] == a["category"] and r["id"] != a["id"]][:3]
        write(f"apps/{a['slug']}/index.html", "app.html", page="apps", app=a, title=a["name"], related=related)
        write(f"apps/{a['slug']}/privacy/index.html", "app_privacy.html", page="privacy", app=a,
              title=f"{a['name']} Privacy Policy")
    urls = ["", "apps/", "privacy/", "terms/", "contact/"]
    urls += [f"apps/{a['slug']}/" for a in apps] + [f"apps/{a['slug']}/privacy/" for a in apps]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{site['url']}/{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {site['url']}/sitemap.xml\n")
    print(f"Built {len(apps)} apps -> {OUT} ({sum(1 for _ in OUT.rglob('*.html'))} pages)")


if __name__ == "__main__":
    main()
