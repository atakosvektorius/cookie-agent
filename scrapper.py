import json
import requests
import os
import sys
import socket
import dns.resolver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

API_KEY = os.getenv("API_KEY")
GET_WORK_URL = os.getenv("GET_WORK_URL")
PUSH_RESULTS_URL = os.getenv("PUSH_RESULTS_URL")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
LIMIT = os.getenv("LIMIT")

def get_work():
    try:
        payload = {"api_key": API_KEY, "limit": LIMIT}
        response = requests.post(GET_WORK_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return [item["domain_name"] for item in data.get("domains", [])]
    except Exception as e:
        print(f"[ERROR] Failed to get work: {e}")
        return None

def push_cookies(domain, cookies):    
    data = {
        "action": "update",
        "api_key": API_KEY,
        "domain_name": domain,
        "cookies": cookies
    }
  
    try:
        response = requests.post(PUSH_RESULTS_URL, json=data)
        response.raise_for_status()
        print(f"[OK] Pushed cookies for {domain}")
    except Exception as e:
        print(f"[WARN] Push failed for {domain}: {e}")

def delete_domain(domain):
    data = {"action": "delete", "api_key": API_KEY, "domain_name": domain}
    try:
        response = requests.post(PUSH_RESULTS_URL, json=data)
        if response.status_code == 200:
            print(f"[INFO] Deleted domain {domain} from backend.")
    except Exception as e:
        print(f"[ERROR] Delete request failed for {domain}: {e}")

def has_a_record(domain):
    if not domain or not domain.strip():
        return False
    try:
        answers = dns.resolver.resolve(domain, 'A')
        if answers.rrset is not None:
            return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.resolver.NoNameservers, dns.name.EmptyLabel):
        pass
    return False


def is_port_open(domain, port, timeout=3):
    try:
        with socket.create_connection((domain, port), timeout=timeout):
            return True
    except Exception:
        return False

def main():
    print("[INFO] Fetching domains...")
    while(True):
        domains = get_work()
        if not domains:
            print("[WARN] No domains received from API.")
            return

        options = Options()
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
      
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
        driver.execute_cdp_cmd("Network.enable", {})

        for domain in domains:
            print(f"[INFO] Processing: {domain}")

            # DNS A record check
            if not has_a_record(domain):
                print(f"[DNS] {domain} has no A record. Deleting.")
                delete_domain(domain)
                continue

            protocols = []
            if is_port_open(domain, 443):
                protocols.append("https://")
            if is_port_open(domain, 80):
                protocols.append("http://")
            if not protocols:
                print(f"[DELETE] {domain} has no open HTTP/HTTPS port → deleting.")
                delete_domain(domain)
                continue

            for prefix in protocols:
                url = f"{prefix}{domain}"
                try:
                    driver.set_page_load_timeout(5)
                    driver.get(url)
                    WebDriverWait(driver, 5).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                    entries = driver.execute_cdp_cmd("Network.getAllCookies", {})
                    print(f"[STATUS] {url} loaded successfully via browser -> 200 OK")
                    cookies = driver.get_cookies()
                    cookie_names = [cookie["name"] for cookie in cookies]
                    push_cookies(domain, cookie_names)
                    break
                except Exception as e:
                    print(f"[WARN] Failed {url}: {e}")
            else:
                print(f"[DELETE] {domain} failed all attempted protocols → deleting.")
                delete_domain(domain)

        driver.quit()

if __name__ == "__main__":
    main()
