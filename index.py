import csv
import requests
import socket
from bs4 import BeautifulSoup


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
    return dict(zip(keys, values))

def get_safe_details(unsafe_dict):
    safe_details = { 'engagement_tier': '', 'engagements': [], 'global_compact_status': '' }
    for key in safe_details.keys():
        try:
            safe_details[key] = unsafe_dict[key]
        except Exception as e:
           print("")
    return safe_details

def get_participants_for_page(page):
    participants = []
    try:
        url = 'https://www.unglobalcompact.org/what-is-gc/participants?page=_%s' % page
        response = requests.get(url)
        html = response.content
        soup = BeautifulSoup(html, features="html.parser")
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
        wr.writerow([p.name, p.p_type, p.sector, p.country, p.joined_on, p.profile_url, p.details['engagement_tier'], p.details['global_compact_status']])


should_get_next_page = True
i = 0


with open("./participants.csv",'w') as resultFile:
    wr = csv.writer(resultFile, dialect='excel')
    wr.writerow(['name', 'type', 'sector', 'country', 'joined_on', 'detail_url', 'engagement_tier', 'global_compact_status'])


    while should_get_next_page:
        result = get_participants_for_page(i)

        if len(result) > 0:
            write_participant_rows(wr, result)
            print("Fetched ", len(result), " participants for page ", i+1)
            i += 1
        else:
            should_get_next_page = False


