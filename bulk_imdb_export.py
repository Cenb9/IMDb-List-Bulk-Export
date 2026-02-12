import time
import sys
import os
import re
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def log_entry(message: str, log_file: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def trigger_export(driver, list_id: str, log_file: str):
    url = f"https://www.imdb.com/list/{list_id}/"
    driver.get(url)
    try:
        try:
            list_title = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="list-header"] h1').text.strip()
        except:
            list_title = driver.title.replace(" - IMDb", "").strip()
        print(f"List title: {list_title}")
        log_entry(f"Triggered export for {list_id} ({list_title})", log_file)

        export_btn = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/main/div/section/section/div[3]/section/div[1]/div/div[2]/div[1]/button/span'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", export_btn)
        driver.execute_script("arguments[0].click();", export_btn)
        print(f"Clicked Export for {list_id}")
        log_entry(f"Clicked Export for {list_id}", log_file)

        return list_title
    except Exception as e:
        print(f"❌ Failed to trigger export for {list_id}: {e}")
        log_entry(f"Failed to trigger export for {list_id}: {e}", log_file)
        return None

def wait_and_download(driver, list_id, list_title, download_dir: str, log_file: str):
    driver.get("https://www.imdb.com/exports/")
    seen_files = set(os.listdir(download_dir))

    while True:
        try:
            ready_btn = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section/div/section/div/div[1]/section/div[2]/ul/li[1]/div[3]/button/span/span')
            if ready_btn.text.strip().lower() == "ready":
                driver.execute_script("arguments[0].scrollIntoView(true);", ready_btn)
                driver.execute_script("arguments[0].click();", ready_btn)
                print(f"Clicked Ready for {list_title}")
                log_entry(f"Clicked Ready for {list_title}", log_file)
                time.sleep(5)

                new_file = None
                for _ in range(60):
                    current_files = set(os.listdir(download_dir))
                    diff = current_files - seen_files
                    if diff:
                        new_file = diff.pop()
                        seen_files.add(new_file)
                        break
                    time.sleep(1)

                if new_file:
                    src = os.path.join(download_dir, new_file)
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    dst = os.path.join(download_dir, f"{sanitize_filename(list_title)}_{timestamp}.csv")
                    os.rename(src, dst)
                    print(f"✅ Renamed {src} → {dst}")
                    log_entry(f"Downloaded {list_id} ({list_title}) → {dst}", log_file)
                    return dst
                else:
                    print(f"⚠️ No new file detected for {list_title}")
                    log_entry(f"No new file detected for {list_title}", log_file)
                    return None
            else:
                print(f"{list_title} still processing, refreshing in 15s...")
                time.sleep(15)
                driver.refresh()
        except Exception as e:
            print(f"Error checking exports page: {e}")
            log_entry(f"Error checking exports page: {e}", log_file)
            time.sleep(15)
            driver.refresh()

def main():
    if len(sys.argv) < 2:
        print("Usage: python bulk_imdb_export.py lists.txt [--delay=N] [--outdir=PATH]")
        sys.exit(1)

    list_file = sys.argv[1]

    delay = 15
    outdir = r"D:\exports"
    for arg in sys.argv[2:]:
        if arg.startswith("--delay="):
            try:
                delay = int(arg.split("=")[1])
            except ValueError:
                print("Invalid delay value, using default 15s.")
        elif arg.startswith("--outdir="):
            outdir = arg.split("=", 1)[1]

    if not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)

    log_file = os.path.join(outdir, "download_log.txt")

    with open(list_file) as f:
        ids = [line.strip() for line in f if line.strip()]

    options = Options()
    prefs = {
        "download.default_directory": outdir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    service = Service(r"chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    successes, failures = [], []

    for imdb_id in ids:
        title = trigger_export(driver, imdb_id, log_file)
        if title:
            print(f"Waiting {delay}s for IMDb to queue export...")
            time.sleep(delay)
            result = wait_and_download(driver, imdb_id, title, outdir, log_file)
            if result:
                successes.append((imdb_id, title, result))
            else:
                failures.append((imdb_id, title, None))
        else:
            failures.append((imdb_id, title or "", None))

        print(f"Waiting {delay}s before next list...")
        time.sleep(delay)

    driver.quit()

    summary_file = os.path.join(outdir, "summary.txt")
    with open(summary_file, "w", encoding="utf-8") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write("=== IMDb Export Summary ===\n")
        f.write(f"Generated at {now}\n\n")

        for sid, title, filepath in successes:
            f.write(f"[{now}] SUCCESS - ID: {sid} | Title: {title} | File: {filepath}\n")

        for sid, title, filepath in failures:
            f.write(f"[{now}] FAILURE - ID: {sid} | Title: {title} | File: (none)\n")

    print(f"\n✅ Summary TXT written to {summary_file}")

    print("\n=== SUMMARY ===")
    print(f"✅ Successful downloads: {len(successes)}")
    for sid, title, filepath in successes:
        print(f"   - {sid} ({title}) → {filepath}")
    print(f"❌ Failed downloads: {len(failures)}")
    for sid, title, filepath in failures:
        print(f"   - {sid} ({title})")

if __name__ == "__main__":
    main()