from agents.azure_cosmos_nosql_vector_db import insert_travel_topic_raw, \
    retrieve_travel_topics_raw_not_embedded, update_travel_topic_raw_embedded_value, upsert_travel_topic_with_embeddings, \
    is_travel_topics_raw_by_topic, retrieve_vector_similarity_of_travel_topics
from agents.azure_text_embedding_tool import generate_embeddings
from agents.wikipedia_tool import get_wiki_single_page, is_wiki_page
from utils.text_splitter import trim_text_source, split_text


# 위키 페이지 조회하여 cosmos db에 저장
def search_wiki_page_and_store_raw(travel_topics: list):
    for travel_topic in travel_topics:
        category = travel_topic["category"]
        topic = travel_topic["topic"]
        if not is_wiki_page(topic):
            continue
        content = get_wiki_single_page(topic)
        if is_travel_topics_raw_by_topic(topic):
            continue
        store_travel_topic(category, topic, content)


def store_travel_topic(category: str, topic: str, content: str):
    insert_travel_topic_raw(category, topic, content)
    proceed_embeddings()


# 텍스트 임베딩 프로세스 진행
def proceed_embeddings():
    not_embedded = retrieve_travel_topics_raw_not_embedded()
    if len(not_embedded) > 0:
        for item in not_embedded:
            trimmed = trim_text_source(item["content"])
            for split in split_text(trimmed):
                embeddings = generate_embeddings(split)
                upsert_travel_topic(item["id"], item["category"], item["topic"], split, embeddings)


def upsert_travel_topic(id: str, category: str, topic: str, content: str, embeddings: list):
    upsert_travel_topic_with_embeddings(category, topic, content, embeddings)
    update_travel_topic_raw_embedded_value(id, category)


def retrieve_travel_topic_text_by_embeddings_similarity(query: str) -> str:
    topic_text = ""
    for split in split_text(query):
        embeddings = generate_embeddings(split)
        topics = retrieve_vector_similarity_of_travel_topics(embeddings)
        for topic in topics:
            topic_text += topic["content_text"]
    return topic_text
