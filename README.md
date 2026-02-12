# IMDb-List-Bulk-Export

Bulk download public IMDb lists using Chrome, Selenium & Python.
No interaction needed after running the script.
All tools except Chrome browser is portable.

> Workflow = Python script  →  Selenium →  ChromeDriver  →  Chrome Browser

After running the script, it will open the first IMDb list page > Auto click the 'Export' button > Wait a few seconds for the export to finish > Go to 'https://www.imdb.com/exports/' > Auto click the 'Ready' button > Download CSV file > Rename the CSV to list's name > Move on to the next list.
After downloading all the lists, it will show a summary & generate a log file.

---

### 🔹 1st Step : Download these tools (Portable) = 

https://winpython.github.io/	(0dot.zip File)

https://googlechromelabs.github.io/chrome-for-testing/	(Chromedriver win64)

https://github.com/Cenb9/IMDb-List-Bulk-Export/releases

Chrome driver version must be the same as your chrome browser version. Check version in chrome://settings/help.
If your browser versions driver is not available, replace the version number in the URL 
(Example: Replace 145.0.7632.26 with 144.0.7559.110 in https://storage.googleapis.com/chrome-for-testing-public/145.0.7632.26/win64/chromedriver-win64.zip)


### 🔹 2nd Step : Get all IMDb list IDs = 

● Go to your IMDb profile (Example - https://www.imdb.com/user/ur123456789/lists)

● Save this bookmarklet in browser & click it - 
```
javascript:(function() {
    let links = document.querySelectorAll('a[href*="/list/ls"]');
    let ids = Array.from(links)
        .map(link => link.href.match(/ls\d+/)?.[0])
        .filter(Boolean);
    if (!ids.length) {
        alert("No IMDb list IDs found on this page.");
        return;
    }
    prompt("Copy these IMDb list IDs:", [...new Set(ids)].join('\n'));
})();
```

● All IMDb list IDs will be shown (Example - ls123456789).
Copy & paste them in lists.txt file.


### 🔹 3rd Step : Running the script = 

● Extract the WinPython zip file.
Copy bulk_imdb_export.py , chrome_settings.py , chromedriver.exe & lists.txt inside 'notebooks' folder of WinPython.

● Run 'WinPython Powershell Prompt'
Enter
```
python -m pip install selenium
```

● After Selenium is installed, Enter
```
python chrome_settings.py
```
It will auto open IMDb & a few seconds later chrome://settings/content/all. 
Click on www.imdb.com > Set 'Automatic downloads' to 'Allow'.
Then go to chrome://settings/downloads > Disable 'Ask where to save each file before downloading'

● Run command of your choice - 
```
python bulk_imdb_export.py lists.txt
```
→ Default mode, 15s delay, default output folder (D:\exports)

```
python bulk_imdb_export.py lists.txt --delay=25
```
→ Custom delay

```
python bulk_imdb_export.py lists.txt --outdir=D:\exports
```
→ Custom output folder

```
python bulk_imdb_export.py lists.txt --delay=25 --outdir=E:\imdb_exports
```
→ Custom delay & folder

● Wait for all downloads to finish.
For big lists (2000+ Titles) set Delay to 30s.

---
---

## 🔹 Extras = 

Using this chrome extension (https://github.com/Dhruv-Techapps/auto-clicker-auto-fill) i found 'Absolute XPath selectors' for Export and Ready buttons in IMDb’s HTML DOM.

'Absolute XPath selector' for clicking 'Export' in https://www.imdb.com/list/ID - 

//*[@id="__next"]/main/div/section/section/div[3]/section/div[1]/div/div[2]/div[1]/button/span

'Absolute XPath selector' for clicking 'Ready' in https://www.imdb.com/exports/ - 

//*[@id="__next"]/main/div/section/div/section/div/div[1]/section/div[2]/ul/li[1]/div[3]/button/span/span


● If the script doesn't work, that means IMDb has changed it's UI. In that case

1. Install the extension, go to an IMDb list page > Right click > Auto Clicker - AutoFill > Side panel > Recording > Start > Click on the IMDb 'Export' button > Stop.

2. Open the extensions configuration page > On the left side panel click on IMDb > Under 'Element Finder' you will find the code for 'absolute XPath selector'. Replace the old 'Absolute XPath selector' code in bulk_imdb_export.py file with the new one.



