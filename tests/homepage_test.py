# homepage_test.py
import json, re, time
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def make_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    return webdriver.Chrome(options=opts)

BASE = "https://markj351.github.io/pcHopkinsWebsite/"

def test_hero_and_ctas():
    d = make_driver()
    try:
        d.get(BASE)
        assert "Progressive Church" in d.title

        # Buttons exist
        ctas = d.find_elements(By.CSS_SELECTOR, "a.btn")
        assert any("Plan Your Visit" in e.text for e in ctas)
        assert any("Watch a Sermon" in e.text for e in ctas)

        # YouTube iframe appears when scrolling to #media
        d.find_element(By.CSS_SELECTOR, 'a[href="#media"]').click()
        time.sleep(0.5)
        iframe = d.find_element(By.CSS_SELECTOR, "#media iframe")
        assert "youtube.com" in iframe.get_attribute("src")
    finally:
        d.quit()

def test_dark_mode_persists():
    d = make_driver()
    try:
        d.get(BASE)
        btn = d.find_element(By.ID, "contrastBtn")
        btn.click()
        time.sleep(0.2)
        # reload and confirm persistence via aria-pressed
        d.refresh()
        time.sleep(0.2)
        pressed = d.find_element(By.ID, "contrastBtn").get_attribute("aria-pressed")
        assert pressed == "true"
    finally:
        d.quit()

def test_contact_mailto_builds_query():
    d = make_driver()
    try:
        d.get(BASE + "#contact")
        # If the form is not on page yet, skip or adapt selectors to your actual form IDs.
        name = d.find_element(By.ID, "name")
        email = d.find_element(By.ID, "email")
        msg = d.find_element(By.ID, "message")
        name.send_keys("QA Bot")
        email.send_keys("qa@example.com")
        msg.send_keys("Hello from automation")

        # Hijack window.location to capture URL instead of navigating
        d.execute_script("window._navs=[]; const _set=Object.getOwnPropertyDescriptor(Window.prototype,'location').set; Object.defineProperty(window,'location',{set:(v)=>window._navs.push(v)});")
        d.find_element(By.CSS_SELECTOR, "form").submit()
        time.sleep(0.2)
        url = d.execute_script("return window._navs[0] || ''")
        assert url.startswith("mailto:info@progressivechurch.org")
        assert "Website%20Inquiry%20from%20QA%20Bot" in url
        assert "Email:%20qa%40example.com" in unquote(url)
        assert "Hello%20from%20automation" in url
    finally:
        d.quit()

def test_jsonld_contract():
    import requests, bs4
    html = requests.get(BASE).text
    soup = bs4.BeautifulSoup(html, "html.parser")
    tag = soup.find("script", {"type":"application/ld+json"})
    data = json.loads(tag.text)
    assert data["@type"] == "Church"
    assert re.match(r"https://markj351.github.io/pcHopkinsWebsite/?", data["url"])
    addr = data["address"]
    for k in ["streetAddress","addressLocality","addressRegion","postalCode","addressCountry"]:
        assert addr.get(k)
