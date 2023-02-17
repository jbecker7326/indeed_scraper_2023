import pandas as pd
import requests
from bs4 import BeautifulSoup as Soup
from datetime import datetime


def main(query='Python', location='NY'):

    # send get request, receive html, parse to text
    url_template = f'http://www.indeed.com/jobs?q={query}&l={location}&start='
    user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    soup = Soup(requests.get(url_template+'0', headers=user_agent).text, 'html.parser')

    # initialize list for building job information dataframe
    indeed_data = []

    # find number of listings
    listings = soup.find('div', {'class': 'jobsearch-JobCountAndSortPane-jobCount'}).get_text()
    listings = int(listings.split(' ')[0].replace(',', ''))

    for i in range(0, listings, 10):
        soup = Soup(requests.get(url_template + str(i), headers=user_agent).text, 'html.parser')
        print(i)
        # split html by job
        jobs = soup.findAll('div', {'class':'job_seen_beacon'})

        for job in jobs:
            # job title
            title = job.select('span[id^=jobTitle]')[0].get_text()

            # company
            company = job.find('span', {'class':'companyName'}).get_text()

            # rating
            rating = job.find('span', {'class':'ratingNumber'})
            if rating:
                rating = rating.get_text()
            else:
                rating = 'NaN'

            # location
            job_location = job.find('div', {'class':'companyLocation'}).get_text()

            # salary
            salary = job.find('div', {'class':'metadata salary-snippet-container'})
            if salary:
                salary = salary.get_text()
            else:
                salary = 'NaN'

            # job type and shift
            type_shift = job.findAll('div', {'class': 'attribute_snippet'})
            if len(type_shift) > 1:
                type = type_shift[1].get_text()
            else:
                type = 'NaN'
            if len(type_shift) > 2:
                shift = type_shift[2].get_text()
            else:
                shift = 'NaN'

            # additional benefits
            benefits = job.find('ul', {'class': 'attributes-list'})
            if benefits:
                benefits_list = []
                for benefit in benefits.findAll('li', {'class':'taxoAttribute'}):
                    benefits_list.append(benefit.get_text())
                benefits = ', '.join(benefits_list)
            else:
                benefits = 'NaN'

            # easy apply
            easy_apply = job.find('td', {'class': 'shelfItem indeedApply'})
            if easy_apply:
                easy_apply = 1
            else:
                easy_apply = 0

            # responsive employer
            responsive = job.find('td', {'class': 'shelfItem responsiveEmployer'})
            if responsive:
                responsive = 1
            else:
                responsive = 0

            # urgently hiring
            urgent = job.find('td', {'class': 'shelfItem urgentlyHiring'})
            if urgent:
                urgent = 1
            else:
                urgent = 0

            # hiring multiple candidtates
            hiring_multiple = job.find('td', {'class': 'shelfItem hiringMultipleCandidates'})
            if hiring_multiple:
                hiring_multiple = 1
            else:
                hiring_multiple = 0

            # job description
            description = job.find('div', {'class':'job-snippet'}).get_text()[1:]


            # date listed
            date = job.find('span', {'class':'date'}).get_text()
            date = date.replace('PostedPosted', 'Posted')

            # append job data to list
            job_data = pd.DataFrame([[title, company, rating, job_location, salary, type, shift, benefits, easy_apply, responsive, urgent, hiring_multiple, description, date]])
            indeed_data.append(job_data)

    # concat list to dataframe
    indeed_dataframe = pd.concat(indeed_data, axis=0)
    column_names = ['job_title', 'company', 'rating', 'job_location', 'salary', 'job_type', 'shift', 'benefits', 'easy_apply', 'responsive_employer', 'urgently_hiring', 'hiring_multiple', 'job_description', 'date_posted']
    indeed_dataframe.columns = column_names

    datetime_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    indeed_dataframe.to_csv(f'IndeedScrape_{datetime_now}_{query}_{location}.csv')


if __name__ == '__main__':
    main()