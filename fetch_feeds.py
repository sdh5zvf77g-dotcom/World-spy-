import json, urllib.request, urllib.parse, datetime as dt
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

KEY = " (leaked OR secret OR classified OR declassified OR whistleblower OR revealed)"
FEEDS = {
  "Declassified": "declassified documents released",
  "Leaks": "leaked documents reveal",
  "Files released": "FOIA documents released reveal",
  "Whistleblowers": "whistleblower reveals",
  "Government": "secret government program revealed",
  "Military & spies": "classified intelligence military revealed",
  "Tech & AI": "leaked unreleased AI model OR leaked unreleased device",
  "Business": "internal memo leaked company",
  "Science & health": "secret research hidden study revealed",
  "Money & crime": "leaked financial records investigation reveals",
}

def url(q):
    return "https://news.google.com/rss/search?q=" + urllib.parse.quote(q + " when:7d") + "&hl=en-US&gl=US&ceid=US:en"

def parse(xml_bytes, cat):
    out = []
    for it in ET.fromstring(xml_bytes).iter("item"):
        raw = (it.findtext("title") or "").strip()
        p = raw.rfind(" - ")
        title, src = (raw[:p], raw[p+3:]) if p > 0 else (raw, it.findtext("source") or "News")
        link = (it.findtext("link") or "").strip()
        try:
            d = parsedate_to_datetime(it.findtext("pubDate")).astimezone(dt.timezone.utc)
        except Exception:
            d = dt.datetime.now(dt.timezone.utc)
        if title and link:
            out.append({"cat": cat, "title": title, "src": src, "link": link, "date": d.isoformat()})
    return out

def main():
    seen, items = set(), []
    for cat, q in FEEDS.items():
        try:
            req = urllib.request.Request(url(q), headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=30).read()
            for i in parse(data, cat):
                if i["link"] not in seen:
                    seen.add(i["link"]); items.append(i)
        except Exception as e:
            print("failed", cat, e)
    items.sort(key=lambda i: i["date"], reverse=True)
    if not items:
        raise SystemExit("no items fetched; keeping old data.json")
    json.dump({"updated": dt.datetime.now(dt.timezone.utc).isoformat(), "items": items},
              open("data.json", "w"), ensure_ascii=False)
    print("saved", len(items))

if __name__ == "__main__":
    main()
