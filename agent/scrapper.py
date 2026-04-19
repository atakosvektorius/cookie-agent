import json
import requests
import os
import sys
import socket
import dns.resolver
from datetime import datetime
from seleniumwire import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

import db

# Environment variables
API_KEY = os.getenv("API_KEY")
GET_WORK_URL = os.getenv("GET_WORK_URL")
PUSH_RESULTS_URL = os.getenv("PUSH_RESULTS_URL")
GECKODRIVER_PATH = os.getenv("GECKODRIVER_PATH")
HEALTHCHECK_FILE = os.getenv("HEALTHCHECK_FILE")
LIMIT = os.getenv("LIMIT")

# Functions
def write_healthcheck(domain):
    try:
        timestamp = datetime.now().isoformat()
        with open(HEALTHCHECK_FILE, "a") as f:
            f.write(f"{timestamp} {domain}\n")
    except Exception as e:
        print(f"[WARN] Failed to write healthcheck: {e}")

def get_work():
    payload = {"api_key": API_KEY, "limit": LIMIT}
    # Add timeout to prevent hanging when network is down
    response = requests.post(GET_WORK_URL, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    return [item["domain_name"] for item in data.get("domains", [])]

def push_cookies(domain, cookies, headers=None):
    data = {
        "action": "update",
        "api_key": API_KEY,
        "domain_name": domain,
        "cookies": cookies,
        "headers": headers or {}
    }

    response = requests.post(PUSH_RESULTS_URL, json=data)
    response.raise_for_status()
    write_healthcheck(domain)
    print(f"[OK] Pushed cookies for {domain}")

def delete_domain(domain):
    data = {"action": "delete", "api_key": API_KEY, "domain_name": domain}
    response = requests.post(PUSH_RESULTS_URL, json=data)
    response.raise_for_status()
    # If we get here, status is 200-299
    write_healthcheck(domain)
    print(f"[INFO] Deleted domain {domain} from backend.")

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

# Main function

def extract_main_headers(driver):
    for req in driver.requests:
        if req.response is None:
            continue
        ct = req.response.headers.get("content-type", "") or ""
        if "html" in ct.lower():
            return dict(req.response.headers)
    return {}


def main():
    db.init_db()
    print("[INFO] Fetching domains...")
    import time
    while(True):
        api_failed = False
        try:
            domains = get_work()
        except requests.exceptions.HTTPError as e:
            api_failed = True
            if e.response.status_code >= 500:
                print(f"[WARN] Server error {e.response.status_code}. Falling back to local DB queue...")
            else:
                print(f"[ERROR] Failed to get work: {e}")
            domains = None
        except Exception as e:
            api_failed = True
            print(f"[ERROR] Failed to get work (network issue?): {e}")
            domains = None

        if not domains and api_failed:
            domains = db.fetch_fallback_domains(LIMIT)
            if domains:
                print(f"[INFO] Using {len(domains)} domain(s) from local DB fallback.")

        if not domains:
            print("[WARN] No domains received from API or local DB.")
            time.sleep(10)
            continue

        options = Options()
        options.accept_insecure_certs = True
        options.set_preference("security.tls.version.min", 1)
        options.set_preference("security.tls.version.enable-deprecated", True)
        options.set_preference("security.ssl.enable_ocsp_stapling", False)

        if GECKODRIVER_PATH:
            service = Service(executable_path=GECKODRIVER_PATH)
        else:
            service = Service()
            
        driver = webdriver.Firefox(service=service, options=options)

        for domain in domains:
            try:
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
                        del driver.requests
                        driver.set_page_load_timeout(10)
                        driver.get(url)
                        WebDriverWait(driver, 5).until(
                            lambda d: d.execute_script("return document.readyState") == "complete"
                        )
                        print(f"[STATUS] {url} loaded successfully via browser -> 200 OK")
                        cookies = driver.get_cookies()
                        cookie_names = [cookie["name"] for cookie in cookies]
                        headers = extract_main_headers(driver)
                        db.upsert_result(domain, cookie_names, headers)
                        push_cookies(domain, cookie_names, headers)
                        break
                    except requests.exceptions.HTTPError:
                        raise # Re-raise HTTPError to be caught by the outer loop
                    except Exception as e:
                        # Truncate error message if it's too long (e.g. stack trace)
                        err_msg = str(e).split('\n')[0]
                        print(f"[WARN] Failed {url}: {err_msg}")
                        if prefix == "https://" and "http://" in protocols:
                            print(f"[INFO] Falling back to http:// for {domain}...")
                else:
                    print(f"[DELETE] {domain} failed all attempted protocols → deleting.")
                    delete_domain(domain)
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code >= 500:
                    print(f"[WARN] Backend server error {e.response.status_code} while processing {domain}. Sleeping for 1 minute...")
                    time.sleep(60)
                    break # Stop processing this batch
                else:
                    print(f"[ERROR] Backend failure for {domain}: {e}")
                    # Continue to next domain

        driver.quit()

# Entry point
if __name__ == "__main__":
    main()
