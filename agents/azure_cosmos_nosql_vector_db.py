import json
import os
import datetime
from azure.cosmos import CosmosClient, PartitionKey, ContainerProxy
from dotenv import load_dotenv

load_dotenv()


def get_cosmos_db_container(container_id: str):
    endpoint = os.getenv("AZURE_COSMOS_NOSQL_DB_ENDPOINT")
    db_key = os.getenv("AZURE_COSMOS_NOSQL_DB_KEY")
    db_id = os.getenv("AZURE_COSMOS_NOSQL_DB_DATABASE_ID")

    client = CosmosClient(endpoint, credential=db_key)
    database = client.get_database_client(db_id)
    container = database.get_container_client(container_id)

    return container


def insert_travel_topic_raw(category: str, topic: str, content: str):
    container = get_cosmos_db_container(os.getenv("AZURE_COSMOS_NOSQL_DB_CONTAINER_ID_RAW"))

    id_max_value = retrieve_id_max_value(container)

    body = {
        "id": str(id_max_value + 1),
        "category": category,
        "topic": topic,
        "content": content,
        "isEmbedded": "N"
    }
    insert_result = container.create_item(body=body)
    return insert_result


def update_travel_topic_raw_embedded_value(id: str, category: str) -> dict:
    container = get_cosmos_db_container(os.getenv("AZURE_COSMOS_NOSQL_DB_CONTAINER_ID_RAW"))

    read_item = container.read_item(item=id, partition_key=category)
    read_item["isEmbedded"] = "Y"
    update_result = container.replace_item(item=read_item, body=read_item)
    return update_result


def upsert_travel_topic_with_embeddings(category: str, topic: str, content_text: str, content_vector: list):
    container = get_cosmos_db_container(os.getenv("AZURE_COSMOS_NOSQL_DB_CONTAINER_ID_EMBEDDINGS"))

    id_max_value = retrieve_id_max_value(container)

    body = {
        "id": str(id_max_value + 1),
        "category": category,
        "topic": topic,
        "contentText": content_text,
        "contentVector": content_vector,
        "updatedAt": f"{datetime.datetime.now()}",
        "isAvailable": "Y"
    }
    upsert_result = container.upsert_item(body=body)
    return upsert_result


def upsert_travel_flows_for_history_archive(category: str, topic: str, content_text: str, content_vector: list):
    container = get_cosmos_db_container(os.getenv("AZURE_COSMOS_NOSQL_DB_CONTAINER_ID_TRAVEL_HISTORY_ARCHIVE"))

    id_max_value = retrieve_id_max_value(container)

    body = {
        "id": str(id_max_value + 1),
        "category": category,
        "topic": topic,
        "contentText": content_text,
        "contentVector": content_vector,
        "updatedAt": f"{datetime.datetime.now()}",
        "isAvailable": "Y"
    }
    upsert_result = container.upsert_item(body=body)
    return upsert_result


def retrieve_id_max_value(container: ContainerProxy) -> int:
    query = 'SELECT VALUE MAX(udf.convertToInt(c.id)) FROM c'
    query_result = list(container.query_items(query=query, enable_cross_partition_query=True))

    if len(query_result) == 0 or query_result[0] is None:
        return 0

    return query_result[0]


def is_travel_topics_raw_by_topic(topic: str) -> bool:
    container = get_cosmos_db_container(os.getenv("AZURE_COSMOS_NOSQL_DB_CONTAINER_ID_RAW"))

    query = '''
    SELECT c.id
    FROM c
    WHERE c.topic = @topic
    '''
    query_result = container.query_items(
        query=query,
        parameters=[
            {"name": "@topic", "value": topic}
        ],
        enable_cross_partition_query=True
    )

    if len(list(query_result)) > 0:
        return True

    return False


def retrieve_travel_topics_raw_not_embedded() -> list:
    container = get_cosmos_db_container(os.getenv("AZURE_COSMOS_NOSQL_DB_CONTAINER_ID_RAW"))

    query = '''
    SELECT c.id,
           c.category,
           c.topic, 
           c.content,
           c.isEmbedded
    FROM c
    WHERE c.isEmbedded = "N"
    '''
    query_result = container.query_items(
        query=query,
        parameters=[],
        enable_cross_partition_query=True
    )

    travel_topics_not_embedded = list(query_result)

    return travel_topics_not_embedded


def retrieve_vector_similarity_of_travel_topics(query_embedding: list) -> list:
    container = get_cosmos_db_container(os.getenv("AZURE_COSMOS_NOSQL_DB_CONTAINER_ID_EMBEDDINGS"))

    query = '''
    SELECT c.id AS id,
           c.category AS category,
           c.topic AS topic, 
           c.contentText AS content_text, 
           c.contentVector AS content_vector,
           c.updatedAt AS updated_at,
           c.isAvailable AS is_available,
           VectorDistance(c.contentVector, @embedding) AS similarity_score
    FROM c
    WHERE c.isAvailable = "Y"
    ORDER BY VectorDistance(c.contentVector, @embedding)
    OFFSET 0
    LIMIT 50
    '''

    query_result = container.query_items(
        query=query,
        parameters=[
            {"name": "@embedding", "value": query_embedding}
        ],
        enable_cross_partition_query=True
    )

    similar_items = list(query_result)

    return similar_items


def retrieve_vector_similarity_of_travel_flows_history_archive(query_embedding: list) -> list:
    container = get_cosmos_db_container(os.getenv("AZURE_COSMOS_NOSQL_DB_CONTAINER_ID_TRAVEL_HISTORY_ARCHIVE"))

    query = '''
    SELECT c.id AS id,
           c.category AS category,
           c.topic AS topic, 
           c.contentText AS content_text, 
           c.contentVector AS content_vector,
           c.updatedAt AS updated_at,
           c.isAvailable AS is_available,
           VectorDistance(c.contentVector, @embedding) AS similarity_score
    FROM c
    WHERE c.isAvailable = "Y"
    ORDER BY VectorDistance(c.contentVector, @embedding)
    OFFSET 0
    LIMIT 20
    '''

    query_result = container.query_items(
        query=query,
        parameters=[
            {"name": "@embedding", "value": query_embedding}
        ],
        enable_cross_partition_query=True
    )

    similar_items = list(query_result)

    return similar_items


def create_container_with_vector_policy(container_id: str, partition_key: str, vector_embedding_policy: dict, indexing_policy: dict):
    endpoint = os.getenv("AZURE_COSMOS_NOSQL_DB_ENDPOINT")
    db_key = os.getenv("AZURE_COSMOS_NOSQL_DB_KEY")
    db_id = os.getenv("AZURE_COSMOS_NOSQL_DB_DATABASE_ID")

    client = CosmosClient(endpoint, credential=db_key)
    database = client.get_database_client(db_id)

    container = database.create_container_if_not_exists(
        id=container_id,
        partition_key=PartitionKey(path=f"/{partition_key}"),
        indexing_policy=indexing_policy,
        vector_embedding_policy=vector_embedding_policy
    )

    return container


# if __name__ == "__main__":
#     upsert_embedding_item({
#         "id": "5",
#         "category": "embedding_test_1",
#         "embedding": [0.1, 0.2, 0.3, 0.39]
#     })
#

# select VALUE {
#     id: c.id,
#     category: c.category,
#     embedding: c.embedding,
#     score: VectorDistance(c.embedding,[0.1, 0.2, 0.3, 0.4])
# }
# from c
# order by VectorDistance(c.embedding,[0.1, 0.2, 0.3, 0.4])
# offset 0
# limit 5

if __name__ == "__main__":

    # container_id = "chat_topic_container"
    # container_id = "chat_topic_raw_container"
    container_id = "travel_history_archive_container"

    partition_key = "category"

    vector_embedding_policy = {
        "vectorEmbeddings": [
            {"path": "/contentVector",
             "dataType": "float32",
             "distanceFunction": "cosine",
             "dimensions": 1536
             },
        ]
    }
    #
    # vector_embedding_policy = {
    #     "vectorEmbeddings": [
    #     ]
    # }

    indexing_policy = {
        "includedPaths": [
            {"path": "/*"}
        ],
        "excludedPaths": [
            {"path": "/\"_etag\"/?",
             "path": "/contentVector/*"}
        ],
        "vectorIndexes": [
            {"path": "/contentVector",
             "type": "quantizedFlat"}
        ]
    }

    # indexing_policy = {
    #     "includedPaths": [
    #         {"path": "/*"}
    #     ],
    #     "excludedPaths": [
    #         {"path": "/\"_etag\"/?"}
    #     ]
    # }

    # travel_topic = {
    #     "id": 1,
    #     "category": "",
    #     "topic": "",
    #     "contentText": "",
    #     "contentVector": [],
    #     "updatedAt": "2021-09-01T00:00:00Z",
    #     "isAvailable": "Y",
    # }

    create_container_with_vector_policy(container_id=container_id,
                                        partition_key=partition_key,
                                        vector_embedding_policy=vector_embedding_policy,
                                        indexing_policy=indexing_policy)
