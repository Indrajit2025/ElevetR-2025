

import requests
from bs4 import BeautifulSoup
import json
import random
from datetime import datetime
from app import app, db, Student, Company, JobPosting, INDIAN_IT_CITIES, BPUT_COLLEGES
from werkzeug.security import generate_password_hash


SCRAPE_URL = "http://127.0.0.1:8001"

def create_dummy_data():

    #           removed  the csv            and   web SCRAPING
   
    with app.app_context():
        print("Dropping all tables...")
        try:
            db.drop_all()
            print("Tables dropped.")
        except Exception as e:
            print(f"Error dropping tables : {e}")

        print("Creating new tables...")
        try:
            db.create_all()
            print("Tables created.")
        except Exception as e:
            print(f"Error creating tables: {e}")
            return 

        # Start                    🫣🫣  Scraping 
        print(f"Attempting to scrape data from {SCRAPE_URL}...")
        try:
            response = requests.get(SCRAPE_URL)
            
            response.raise_for_status() 
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
         
            job_listings = soup.find_all('div', class_='job-listing')
            
            if not job_listings:
                print("ERROR: Scraped the site, but found no job listings.")
                print("Please ensure the 'create_new_site' app is running and has data.")
                return
                
            print(f"Successfully scraped {len(job_listings)} jobs.")

        except requests.exceptions.ConnectionError:
            print(f"ERROR: Could not connect to {SCRAPE_URL}.")
            print("do make sure the 'create_new_site/app.py' server is running on port 8001.")
            
            return
        except Exception as e:
            print(f"Error during scraping: {e}")
            return

        
        all_skills = set()
        companies_cache = {} 

        print("Processing scraped companies and jobs...")
        
        
        for index, job_div in enumerate(job_listings):
            try:
                # Extract data from the HTML elements
                company_name = job_div.find('h3', class_='company-name').text.strip()
                role = job_div.find('h2', class_='role-name').text.strip()
                skills_str = job_div.find('p', class_='skills-list').text.strip()
                cgpa_str = job_div.find('span', class_='cgpa').text.strip()

                if not company_name or not role or not skills_str or not cgpa_str:
                    print(f"Skipping job {index+1} due to missing data in scraped HTML.")
                    continue
            
            except AttributeError as e:
                print(f"Skipping job {index+1} due to parsing error (HTML structure error?): {e}")
                continue

            if company_name not in companies_cache:
                
                company = Company(
                    company_name=company_name,
                    email=f"{company_name.lower().replace(' ', '').replace('.', '')}@in.com", 
                    password_hash=generate_password_hash('pass1234'),
                    status='approved', 
                    description=f"Description for {company_name}."
                )
                db.session.add(company)
                
                try:
                    db.session.commit()
                    companies_cache[company_name] = company.id
                except Exception as e:
                    db.session.rollback()
                    print(f"Error adding company {company_name} (job {index+1}): {e}. Trying to find existing...")
                    
                    existing_company = Company.query.filter_by(company_name=company_name).first()
                    if existing_company:
                         companies_cache[company_name] = existing_company.id
                         print(f"--- Found existing company ID: {existing_company.id}")
                    else:
                         print(f"--- Could not find or add company {company_name}. Skipping related job.")
                         continue 

            
            if company_name not in companies_cache:
                 print(f"Skipping job for {company_name} as company ID not found in cache.")
                 continue

            company_id = companies_cache[company_name]

            
            try:
                skills_list = [s.strip() for s in skills_str.split(',') if s.strip()]
                all_skills.update(skills_list)
            except Exception as e:
                print(f"Warning: Could not parse skills '{skills_str}' for job {role}: {e}")
                skills_list = ["Skill Parsing Error"]

            try:
                 cgpa_req = float(cgpa_str)
            except (ValueError, TypeError):
                 print(f"Warning: Invalid CGPA '{cgpa_str}' for job {role}. Setting to 6.0.")
                 cgpa_req = 6.0 

            job = JobPosting(
                company_id=company_id,
                job_role=str(role),
                required_skills=json.dumps(skills_list),
                location=random.choice(INDIAN_IT_CITIES), 
                cgpa_required=cgpa_req,
                description=f"Seeking a talented {role} for {company_name}. Key skills include: {', '.join(skills_list)}.",
                
                salary_min=random.choice([None, random.randint(3, 6) * 100000]),
                salary_max=random.choice([None, random.randint(7, 15) * 100000]),
                contact_email=f"hr-{index}@dummy.com",
                contact_mobile=f"99887{10000 + index}"
            )
            db.session.add(job)

        print("Committing all jobs...")
        try:
             db.session.commit()
             print("\nDatabase has been successfully populated with SCRAPED data! ✅")
        except Exception as e:
             db.session.rollback()
             print(f"\nError committing jobs: {e}")

if __name__ == '__main__':
    create_dummy_data()