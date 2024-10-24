import os
from gremlin_python.driver import client, serializer
from dotenv import load_dotenv

load_dotenv("/Users/donghyeon/Desktop/development/ai-intelligence-app/agent2/config/.env")


def get_gremlin_client():
    endpoint = os.getenv("AZURE_COSMOS_GREMLIN_DB_ENDPOINT")
    api_key = os.getenv("AZURE_COSMOS_GREMLIN_DB_KEY")

    client_gremlin = client.Client(url=endpoint,
                                   traversal_source='g',
                                   username="/dbs/ai-agent/colls/relationship",
                                   password=api_key,
                                   message_serializer=serializer.GraphSONSerializersV2d0())

    return client_gremlin


def create_vertices(message: str, bindings: dict):
    client = get_gremlin_client()

    client.submit(message=message, bindings=bindings)


def create_edges(message: str, bindings: dict):
    client = get_gremlin_client()

    client.submit(message=message, bindings=bindings)


if __name__ == "__main__":

    # message = "g.addV('person').property('id', id).property('type', type).property('phoneNumber', phone_number).property('gender', gender).property('age', age)"
    # bindings = {
    #     "id": "2",
    #     "type": "0001",
    #     "phone_number": "01065462340",
    #     "gender": "female",
    #     "age": "30"
    # }

    edges_message = "g.V([type, from_phone_number]).addE('knows').to(g.V([type, to_phone_number]))"
    edges_bindings = {
        "type": "0001",
        "from_phone_number": "01073337601",
        "to_phone_number": "01065462340",
    }

    # create_vertices(message, bindings)

    create_edges(edges_message, edges_bindings)
