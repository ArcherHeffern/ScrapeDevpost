from bs4 import BeautifulSoup, NavigableString
import io
from typing import List, Optional
from dataclasses import dataclass
import requests
import csv

class Logger:
    def __init__(self, active: bool):
        self.active = active
    
    def log(self, msg: str):
        if self.active:
            print(f'[LOG] {msg}')

logger = Logger(True)

@dataclass
class DevpostProject:
  title: str
  headline: str
  media: Optional[List[str]]
  inspiration: Optional[str]
  what_it_does: Optional[str]
  how_we_built_it: Optional[str]
  challenges: Optional[str]
  accomplishments: Optional[str]
  lessons: Optional[str]
  whats_next: Optional[str]
  built_with: Optional[List[str]]
  demos: Optional[List[str]]


sources = ['https://deishacks2021.devpost.com/project-gallery',
'https://deishacks2022.devpost.com/project-gallery',
'https://deis-hacks-2020.devpost.com/project-gallery'
]

def get_projects(source: str) -> List[str]:
    logger.log('Getting project urls')
    projects: List[DevpostProject] = []
    source += '?page='
    i = 1
    while 1:
        soup = BeautifulSoup(requests.get(source + str(i)).text, 'html.parser')
        urls = [e.get('href') for e in soup.find_all('a', class_='link-to-software')]
        _projects = [get_project_details(url) for url in urls]
        projects.extend(_projects)
        if len(_projects) == 0:
            break
        i += 1
    logger.log(f'Urls: {urls}') 
    return projects

def get_project_details(source: str) -> DevpostProject: 
    def read_all_paragraphs(soup: NavigableString|None) -> str:
        if soup is None:
            return None
        sb = io.StringIO()
        while soup.findNext().name == 'p':
            sb.write(soup.findNext().text)
            soup = soup.findNext()
        return sb.getvalue()

    soup = BeautifulSoup(requests.get(source).text, 'html.parser')
    title_element = soup.find('h1', id='app-title')
    title = title_element.text
    headline = title_element.find_next_sibling('p').text
    gallery = soup.find('div', id='gallery')
    if gallery is not None:
        media = [e.get('src') for e in gallery.find_all('img')] + [e.get('src') for e in gallery.find_all('video')] + [e.get('src') for e in gallery.find_all('iframe')] + [e.get('href') for e in gallery.find_all('a')] 
        main_section = gallery.find_next_sibling('div')

        inspiration = main_section.find('h2', text='Inspiration')
        inspiration = read_all_paragraphs(inspiration) 

        what_it_does = main_section.find('h2', text='What it does') 
        what_it_does = read_all_paragraphs(what_it_does)

        how_we_built_it = main_section.find('h2', text='How we built it')
        how_we_built_it = read_all_paragraphs(how_we_built_it)

        challenges = main_section.find('h2', text='Challenges we ran into')
        challenges = read_all_paragraphs(challenges)

        accomplishments = main_section.find('h2', text='Accomplishments that we\'re proud of')
        accomplishments = read_all_paragraphs(accomplishments)

        lessons = main_section.find('h2', text='What we learned')
        lessons = read_all_paragraphs(lessons)

        whats_next = main_section.find('h2', text=f'What\'s next for {title}')
        whats_next = read_all_paragraphs(whats_next)
    else:
        media = None
        inspiration = None
        what_it_does = None
        how_we_built_it = None
        challenges = None
        accomplishments = None
        lessons = None
        whats_next = None

    built_with_list = soup.find('div', id='built-with')
    if built_with_list is not None:
        built_with_list = built_with_list.find_all('span', class_='cp-tag')
        built_with = []
        for result in built_with_list:
            built_with.append(result.text)
    else:
        built_with = None

    demos = soup.find('nav', class_='app-links')
    if demos is not None:
        demos = [l.get('href') for l in demos.findAll('a')]

    project = DevpostProject(
        title=title,
        headline=headline,
        media=media,
        how_we_built_it=how_we_built_it,
        inspiration=inspiration,
        what_it_does=what_it_does,
        built_with=built_with,
        challenges=challenges,
        accomplishments=accomplishments,
        lessons=lessons,
        whats_next=whats_next,
        demos=demos
    )
    logger.log(f'Project: {source}')
    return project

if __name__ == '__main__':
    for source in sources:
        name = source.split('.')[0].split('//')[1]
        with open(f'{name}.csv', 'w') as f:
            logger.log(f'File: {f}')
            csv_file = csv.DictWriter(f, fieldnames=DevpostProject.__annotations__.keys())
            csv_file.writeheader()
            projects = get_projects(source)
            logger.log('Writing projects')
            for project in projects:
                csv_file.writerow(project.__dict__)