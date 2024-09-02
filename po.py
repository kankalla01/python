import json
import pandas as pd
import re
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# Define LinkedIn URLs
urls = [
    "https://www.linkedin.com/jobs/search?location=India&geoId=102713980&f_C=1035&position=1&pageNum=0",  # Microsoft
    # "https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_C=1441",  # Google
    # "https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_TPR=r86400&f_C=1586&position=1&pageNum=0"  # Amazon
]

# Initialize the list to hold job data
jobs = []

# Function to parse date string
def parse_date(posted_on):
    date_map = {"today": 0,"hours":0,"hour":0, "day": 1,"days" : 1, "week": 7,"weeks": 7, "month": 30}
    number, unit = re.search(r"(\d+)\s(\w+)", posted_on).groups()
    delta = int(number) * date_map[unit]
    posted_date = datetime.now() - timedelta(days=delta)
    return posted_date.strftime("%d-%m-%Y")
# Loop through URLs
for url in urls:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get(url)
    time.sleep(10)  # Wait for the page to load
    
    try:
        ele = driver.find_element(By.CLASS_NAME,"jobs-search__results-list")

# Close the WebDriver

        for e in ele.find_elements(By.CLASS_NAME,"base-card"):
            str = int(e.find_element(By.TAG_NAME,"a").get_attribute('href').split("?")[0].split("-")[-1])
            e.click()
            time.sleep(2)
            k = e.find_element(By.CLASS_NAME,"base-search-card__info")
            time.sleep(2)
            li = driver.find_element(By.CLASS_NAME,"description__job-criteria-list").find_elements(By.TAG_NAME,"li")
            try:
                company_name = k.find_element(By.CLASS_NAME,"base-search-card__subtitle").text.strip()
                job_title = k.find_element(By.CLASS_NAME, "base-search-card__title").text.strip()
                location = k.find_element(By.CLASS_NAME,  'job-search-card__location').text.strip()
                posted_on = k.find_element(By.TAG_NAME,"time").text.strip()
                seniority_level = li[0].find_element(By.TAG_NAME,'span').text.strip()
                employment_type = li[1].find_element(By.TAG_NAME,'span').text.strip()
                job_info = {
                "company_name": company_name,
                "linkedin_job_id": str,
                "job_title": job_title,
                "location": location,
                "posted_on": posted_on,
                "posted_date": parse_date(posted_on),
                "seniority_level": seniority_level if seniority_level else "null",
                "employment_type": employment_type if employment_type else "null"    
             }
                jobs.append(job_info)
                if(len(jobs)==50):
                    break
            
            
            
            except Exception as e:
                print(f"Error processing job: {e}")
    except Exception as e:
        print(f"Error processing job: {e}")
    
    driver.quit()


# Save the job data in JSON format
with open('linkedin_jobs.json', 'w') as json_file:
    json.dump(jobs, json_file, indent=4)

# Save the job data in CSV format
df = pd.DataFrame(jobs)
df.to_csv('linkedin_jobs.csv', index=False)
