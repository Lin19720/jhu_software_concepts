# Module 2: The GradCafe Data Scraping & LLM Normalization

This repository contains the complete implementation for Module 2, focusing on automated web scraping of The GradCafe graduate admission records, parallelized HTML data parsing, and dataset cleaning/normalization using a local LLM hosting service.

## Checklist
- [x] 1. SSH URL to GitHub Repository
- [x] 2. scrape.py
- [x] 3. clean.py
- [x] 4. llm_hosting/
- [x] 5. applicant_data.json
- [x] 6. llm_extend_applicant_data.json
- [x] 7. robots.txt screenshot
- [x] 8. README.md

## Commands

```bash
pip3 install selenium beautifulsoup4 flask huggingface_hub llama-cpp-python requests
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_dev_session"
python3 capture_pages.py
python3 scrape.py
python3 llm_hosting/app.py > /dev/null 2>&1 &
python3 clean.py
