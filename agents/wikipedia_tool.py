import os
import wikipediaapi
from dotenv import load_dotenv


load_dotenv("/Users/donghyeon/Desktop/development/ai-intelligence-app/agent2/config/.env")


def get_wiki_client_for_ko():
    user_agent = os.getenv("WIKIPEDIA_USER_AGENT")
    wiki_client = wikipediaapi.Wikipedia(user_agent, 'ko')
    return wiki_client


def get_wiki_single_page(topic: str):
    wiki_client = get_wiki_client_for_ko()
    page = wiki_client.page(topic)
    return page.text


def get_wiki_summary(topic: str):
    wiki_client = get_wiki_client_for_ko()
    page = wiki_client.page(topic)
    return page.summary


def get_sections(topic: str):
    wiki_client = get_wiki_client_for_ko()
    page = wiki_client.page(topic)
    sections = page.sections
    return sections


def get_page_by_section(topic: str, section: str):
    wiki_client = get_wiki_client_for_ko()
    page = wiki_client.page(topic)
    section_page = page.section_by_title(section)
    return section_page


def is_wiki_page(topic: str):
    wiki_client = get_wiki_client_for_ko()
    page = wiki_client.page(topic)
    return page.exists()


if __name__ == "__main__":
    topic = "도림천"
    isWikiPage = is_wiki_page(topic)
    if isWikiPage:
        result = get_wiki_single_page(topic)