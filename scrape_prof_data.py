import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd
import os

# Load faculty data from previous step
with open("results/faculty_data.json", "r") as file:
    faculty_list = json.load(file)

# Headers to mimic a real browser
headers = {"User-Agent": "Mozilla/5.0"}

# Create a list to store extracted faculty data
faculty_data = []

# Iterate over each faculty member to scrape their profile page
for faculty in faculty_list:
    profile_url = faculty["profile_link"]
    
    print(f"Scraping {faculty['name']}'s profile...")

    response = requests.get(profile_url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch {faculty['name']}'s profile.")
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract email
    email = "N/A"
    email_tag = soup.find("a", href=lambda href: href and "mailto:" in href)
    if email_tag:
        email = email_tag["href"].replace("mailto:", "").strip()

    # Extract phone number
    phone = "N/A"
    phone_tag = soup.find("a", href=lambda href: href and "tel:" in href)
    if phone_tag:
        phone = phone_tag["href"].replace("tel:", "").strip()

    # Extract research interests
    research_interests = "N/A"
    research_section = soup.find("div", class_="field field-name-field-research-interests") or soup.find("p", string="Research Interests")
    if research_section:
        research_interests = research_section.text.strip()

    # Extract recent projects
    recent_projects = "N/A"
    projects_section = soup.find("div", class_="field field-name-field-research-projects") or soup.find("p", string="Current Projects")
    if projects_section:
        recent_projects = projects_section.text.strip()

    # Extract lab or research group (if available)
    research_lab = "N/A"
    lab_link = soup.find("a", href=True, string=lambda text: text and "Lab" in text)
    if lab_link:
        research_lab = lab_link["href"]

    # Check if faculty is looking for students
    looking_for_students = "No"
    keywords = ["Open Positions", "Prospective Students", "Join My Lab", "Graduate Students Wanted"]
    for keyword in keywords:
        if soup.find(text=lambda text: text and keyword in text):
            looking_for_students = "Yes"
            break

    # Extract full profile description
    profile_description = "N/A"
    profile_text_section = soup.find("div", class_="profile-description") or soup.find("p")
    if profile_text_section:
        profile_description = profile_text_section.text.strip()

    # Append extracted data to list
    faculty_data.append({
        "Name": faculty["name"],
        "Title": faculty["title"],
        "Department": faculty["department"],
        "Profile Link": profile_url,
        "Email": email,
        "Phone": phone,
        "Research Interests": research_interests,
        "Recent Projects": recent_projects,
        "Research Lab": research_lab,
        "Looking for Students": looking_for_students,
        "Profile Description": profile_description
    })

    # Respect website policies: Wait 2 seconds between requests
    time.sleep(2)

# Convert data to Pandas DataFrame
df = pd.DataFrame(faculty_data)

# Ensure results folder exists
os.makedirs("results", exist_ok=True)

# Save DataFrame to Excel
excel_path = "results/faculty_data.xlsx"
df.to_excel(excel_path, index=False)

print(f"✅ Faculty data saved to Excel: {excel_path}")

