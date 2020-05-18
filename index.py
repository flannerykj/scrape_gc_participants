import csv
import requests
import socket
from bs4 import BeautifulSoup


initiative_codes = [
    '2', # Caring for Climate
    '244', # Science based targets (Approved)
    '246', # " (Committed)
    '250', # Business Ambition for 1.5°C — Our Only Future
    '19', # Global Compact LEAD
    '241', # Sustainable Stock Exchanges
    '191', # Carbon Pricing Champions
    '243', # Responsible Climate Policy Engagement
]


class Participant:
    def __init__(self, name, p_type, sector, country, joined_on, profile_url, details):
       self.name = name
       self.p_type = p_type
       self.sector = sector
       self.country = country
       self.joined_on = joined_on
       self.profile_url = profile_url
       self.details = details

    def toString(self):
        return self.name

def get_participant_details_dict(path):
    root_url = 'https://www.unglobalcompact.org'
    url = root_url + path
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, features="html.parser")

    detailsDiv = soup.find("dl")
    labels = [tag.get_text() for tag in detailsDiv.find_all("dt")]
    keys = map(lambda x: x.replace(" ", "_").replace(":", "").lower(), labels)
    values = [tag.get_text().strip() for tag in detailsDiv.find_all("dd")]
    dictionary = dict(zip(keys, values))
    try:
        engagementsDiv = soup.find("div", class_="engagements")
        engagementLinks = engagementsDiv.find_all("a", href=True)
        dictionary["engagements"] = ', '.join(map(lambda x: x.text.strip(), engagementLinks))
    except Exception as e:
        print("")
    return dictionary

def get_safe_details(unsafe_dict):
    safe_details = { 'engagement_tier': '', 'engagements': [], 'global_compact_status': '', 'engagements': ''}
    for key in safe_details.keys():
        try:
            safe_details[key] = unsafe_dict[key]
        except Exception as e:
           print("")
    return safe_details

def get_participants_for_page(page_index):
    participants = []
    try:
        url = 'https://www.unglobalcompact.org/what-is-gc/participants?page=%s' % page
        for i in initiative_codes:
            url += """&search%5Binitiatives%5D%5B%5D=""" + i
        print(url)
        response = requests.get(url)
        html = response.content
        soup = BeautifulSoup(html, features="html.parser")

        # get total page count
        page = page_index + 1
        total_pages = 0
        pagination = soup.find("div", class_="pagination")
        last_pagination_div = None
        for last_pagination_div in pagination:pass
        if last_pagination_div:
            total_pages = last_pagination_div.getText()

        print("fetching for page %s" % page)

        if page == 1:
            results = soup.find("p", class_="results-count").text
            print("TOTAL RESULTS: %s" % results)

        row_list = soup.findAll('tr')
        for item in row_list:
            header = item.find('th')
            link = header.find('a', href=True)
            if link:
                profile_url = link['href']
                name = link.text
                if name:
                    cells = item.findAll('td')
                    print(name)
                    p_type = cells[0].text
                    sector = cells[1].text
                    country = cells[2].text
                    joined_on = cells[3].text
                    details = {}
                    try:
                        details = get_participant_details_dict(profile_url)
                    except Exception as e:
                        print(e)
                    p = Participant(name, p_type, sector, country, joined_on, profile_url, get_safe_details(details))
                    participants.append(p)
                else:
                    print("none for link: " + link)
        return participants
    except Exception as e:
        print("ERROR fetching participants for page: ", page)
        print (e)
        return codes


def write_participant_rows(wr, participants):
    for p in participants:
        wr.writerow([p.name, p.p_type, p.sector, p.country, p.joined_on, p.profile_url, p.details['engagement_tier'], p.details['global_compact_status'], p.details['engagements']])

should_get_next_page = True
i = 0


with open("./participants.csv",'w') as resultFile:
    wr = csv.writer(resultFile, dialect='excel')
    wr.writerow(['name', 'type', 'sector', 'country', 'joined_on', 'detail_url', 'engagement_tier', 'global_compact_status', 'engagements'])


    while should_get_next_page:
        result = get_participants_for_page(i)

        if len(result) > 0:
            write_participant_rows(wr, result)
            print("Fetched ", len(result), " participants for page ", i+1)
            i += 1
        else:
            should_get_next_page = False


