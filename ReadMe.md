# Playwright Asset Extractor

This Python script extracts asset paths (e.g., `/content/dam/...`) from a list of URLs by scanning HTML elements with `src` and `srcset` attributes.
---

## ✅ Features

- Reads multiple URLs from `urls.txt`
- Automatically clicks cookie consent button
- Extracts paths from `src` and `srcset` attributes that start with `/content/dam`
- Saves all results to a single file: `output/results.txt`
- Works with **Python 3.7+**

---

## 📁 Project Structure

- extract_dam_assets.py # Main script
─ urls.txt # Input: list of URLs (one per line)
─ output/
|─ results.txt # Output: extracted asset paths

---

## 🚀 How to Set Up and Run

### 1. ✅ Install Python (3.7 or higher)

 Make sure Python is installed:
 python --version

### 2. 📦 Install Dependencies

 Open a terminal or command prompt and run:
  pip install playwright

 Then install the required browser binaries:
  playwright install
 
 This step is required the first time to download Chromium for browser automation.

### 3. ✏️ Prepare Input File
 Create a file called urls.txt in the same directory and add one URL per line:
 https://www.example.com/page1
 https://www.example.com/page2

### 4. ▶️ Run the Script
 Run the script using Python:
  python extract_dam_assets.py

The script will:

- Visit each URL

- Accept cookies

- Extract all paths that begin with /content/dam

- Write them to output/results.txt


### 📄 Example Output
 Sample content of output/results.txt:

 https://www.example.com/page1:
  /content/dam/assets/image1.jpg
  /content/dam/assets/image2.jpg

 https://www.example.com/page2:
  /content/dam/assets/doc1.pdf
