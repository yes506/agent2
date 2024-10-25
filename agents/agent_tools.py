import json
import os
from typing import Annotated

import urllib3
from autogen import UserProxyAgent
from tavily import TavilyClient

from agents.output_tool import append_travel_flow
from utils.http_util import get_pool_manager
from agents.travel_topic_tool import retrieve_travel_topic_text_by_embeddings_similarity
from agents.travel_history_archive_tool import retrieve_travel_history_archive_context_by_embeddings_similarity


def get_ToolAgent():
    ToolAgent = UserProxyAgent(
        name="tool_agent",
        human_input_mode="NEVER",
        llm_config=False,
        code_execution_config=False,
        description="필요한 도구(tool)를 적시 적소에 실행 시키는 도구 실행 전문 에이전트",
    )

    ToolAgent \
        .register_for_execution(name="get_each_point_info")(get_each_point_info)
    ToolAgent \
        .register_for_execution(name="SearchWeb")(SearchWeb)
    ToolAgent \
        .register_for_execution(name="get_geo_code")(get_geo_code)
    ToolAgent \
        .register_for_execution(name="convert_address")(convert_address)
    ToolAgent \
        .register_for_execution(name="get_pedestrian_routes_transit_time_distance")(get_pedestrian_routes_transit_time_distance)
    ToolAgent \
        .register_for_execution(name="get_travel_flow")(get_travel_flow)
    ToolAgent \
        .register_for_execution(name="SearchTravelTopicContext")(SearchTravelTopicContext)
    ToolAgent \
        .register_for_execution(name="SearchTravelFlowsHistoryArchiveContext")(SearchTravelFlowsHistoryArchiveContext)

    ToolAgent \
        .register_for_execution(name="SayTerminate")(SayTerminate)

    return ToolAgent


# 각 추천 장소 정보 조회
# point_type_code: 장소(포인트) 유형 코드
# 0001 : 음식점, 주점, 카페, 커피숍, 베이커리
# 0002 : 박물관, 미술관
# 0003 : 공원, 산책로, 고궁, 동물원, 식물원, 테마 파크
# 0004 : 쇼핑몰, 백화점, 마트
# 0005 : 영화관, 극장, 공연장, 도서관, 서점
# 9998 : 출발 지점
# 9999 : 도착 지점
def get_each_point_info(order: int,
                        point_type_code: str,
                        point_name: str,
                        travel_date: str,
                        members: list,
                        pros: str,
                        cons: str,
                        recommended: str,
                        old_address: str,
                        new_address: str,
                        latitude: str,
                        longitude: str,
                        admission_fee_kid: str,
                        admission_fee_teenager: str,
                        admission_fee_adult: str,
                        operating_hours_on_monday: str,
                        break_time_on_monday: str,
                        operating_hours_on_tuesday: str,
                        break_time_on_tuesday: str,
                        operating_hours_on_wednesday: str,
                        break_time_on_wednesday: str,
                        operating_hours_on_thursday: str,
                        break_time_on_thursday: str,
                        operating_hours_on_friday: str,
                        break_time_on_friday: str,
                        operating_hours_on_saturday: str,
                        break_time_on_saturday: str,
                        operating_hours_on_sunday: str,
                        break_time_on_sunday: str,
                        expected_arrival_time: str,
                        expected_stay_time: int,
                        expected_departure_time: str) -> dict:
    point_info = {
        "order": order,
        "point_name": point_name,
        "point_type_code": point_type_code,
        "travel_date": travel_date,
        "members": members,
        "pros": pros,
        "cons": cons,
        "recommended": recommended,
        "old_address": old_address,
        "new_address": new_address,
        "latitude": latitude,
        "longitude": longitude,
        "admission_fee_kid": admission_fee_kid,
        "admission_fee_teenager": admission_fee_teenager,
        "admission_fee_adult": admission_fee_adult,
        "operating_hours_on_monday": operating_hours_on_monday,
        "break_time_on_monday": break_time_on_monday,
        "operating_hours_on_tuesday": operating_hours_on_tuesday,
        "break_time_on_tuesday": break_time_on_tuesday,
        "operating_hours_on_wednesday": operating_hours_on_wednesday,
        "break_time_on_wednesday": break_time_on_wednesday,
        "operating_hours_on_thursday": operating_hours_on_thursday,
        "break_time_on_thursday": break_time_on_thursday,
        "operating_hours_on_friday": operating_hours_on_friday,
        "break_time_on_friday": break_time_on_friday,
        "operating_hours_on_saturday": operating_hours_on_saturday,
        "break_time_on_saturday": break_time_on_saturday,
        "operating_hours_on_sunday": operating_hours_on_sunday,
        "break_time_on_sunday": break_time_on_sunday,
        "expected_arrival_time": expected_arrival_time,
        "expected_stay_time": expected_stay_time,
        "expected_departure_time": expected_departure_time
    }

    return point_info


# Tavily에서 제공하는 search API를 사용하여 웹 검색을 수행하는 함수
def SearchWeb(query: Annotated[str, "The search query"]) -> Annotated[str, "The search results"]:
    api_key = os.getenv("TAVILY_API_KEY")
    tavily = TavilyClient(api_key=api_key)
    return tavily.get_search_context(query=query, search_depth="advanced")


# 티맵의 좌표획득 API를 사용하여 주소를 입력받아 좌표를 반환하는 함수
def get_geo_code(city_do: str, gu_gun: str, dong: str, bunji: str, detail_address: str) -> dict:

    if detail_address is None:
        detail_address = ""

    http = get_pool_manager()
    api_key = os.getenv("TMAP_API_KEY")
    api_url = os.getenv("TMAP_GEOCODING_ENDPOINT")
    request_params = {}
    version = "1"
    city_do_utf8 = city_do.encode("utf-8")
    gu_gun_utf8 = gu_gun.encode("utf-8")
    dong_utf8 = dong.encode("utf-8")

    request_params["version"] = version
    request_params["city_do"] = city_do_utf8
    request_params["gu_gun"] = gu_gun_utf8
    request_params["dong"] = dong_utf8

    if bunji is not None:
        bunji_utf8 = bunji.encode("utf-8")
        request_params["bunji"] = bunji_utf8

    if detail_address != "":
        detail_address_utf8 = detail_address.encode("utf-8")
        request_params["detailAddress"] = detail_address_utf8

    request_params["appKey"] = api_key

    response = http.request(
        method="GET",
        url=api_url,
        fields=request_params,
    )

    response_str = response.data.decode("utf-8")
    response_str_for_json = response_str.replace("'", "\"")
    response_json = json.loads(response_str_for_json)["coordinateInfo"]

    latitude = response_json["lat"]
    longitude = response_json["lon"]

    return {"longitude": longitude, "latitude": latitude}


# 티맵의 주소변환 API를 사용하여 도로명 형식의 주소를 입력받아 변환된 구주소(지번) 형식의 주소를 반환하는 함수
def convert_address(req_address: str) -> str:
    http = get_pool_manager()
    api_key = os.getenv("TMAP_API_KEY")
    api_url = os.getenv("TMAP_CONVERT_ADDRESS_ENDPOINT")
    request_params = {}
    version = "1"
    search_type_code = "NtoO"

    request_params["version"] = version
    request_params["searchTypCd"] = search_type_code
    request_params["reqAdd"] = req_address
    request_params["appKey"] = api_key

    response = http.request(
        method="GET",
        url=api_url,
        fields=request_params,
    )

    response_str = response.data.decode("utf-8")
    response_str_for_json = response_str.replace("'", "\"")
    response_json = json.loads(response_str_for_json)["ConvertAdd"]

    upper_district_name = response_json["upperDistName"]
    middle_district_name = response_json["middleDistName"]
    legal_lower_district_name = response_json["legalLowerDistName"]
    primary = response_json["primary"]
    secondary = response_json["secondary"]

    if secondary != "0":
        return f"{upper_district_name} {middle_district_name} {legal_lower_district_name} {primary}-{secondary}"
    else:
        return f"{upper_district_name} {middle_district_name} {legal_lower_district_name} {primary}"


# 보행자 경로 탐색 결과를 조회하고 총 소요시간과 거리를 반환하는 함수
def get_pedestrian_routes_transit_time_distance(start_x: str, start_y: str, start_name: str, end_x: str, end_y: str, end_name: str):
    http = get_pool_manager()
    api_key = os.getenv("TMAP_API_KEY")
    api_url = os.getenv("TMAP_PEDESTRIAN_ROUTES_ENDPOINT")

    request_headers = urllib3.HTTPHeaderDict()
    request_body = {}

    request_headers.add("appKey", api_key)

    request_body["startX"] = start_x
    request_body["startY"] = start_y
    request_body["endX"] = end_x
    request_body["endY"] = end_y
    request_body["startName"] = start_name
    request_body["endName"] = end_name

    response = http.request(
        method="POST",
        url=api_url,
        headers=request_headers,
        json=request_body,
    )

    response_str = response.data.decode("utf-8")
    response_str_for_json = response_str.replace("'", "\"")
    features = json.loads(response_str_for_json)["features"]

    pedestrian_routes = []
    total_time = 0
    total_distance = 0
    for feature in features:
        if "time" in feature["properties"]:
            total_time += (feature["properties"]["time"] / 60)
        if "distance" in feature["properties"]:
            total_distance += feature["properties"]["distance"]
    return total_time, total_distance


# 한 지점에서 다른 지점으로의 이동에 관한 정보 및 각 지점에 대한 정보를 반환하는 함수
def get_travel_flow(flow_order: int, from_point: dict, to_point: dict, transit_time: int, transit_distance: int) -> dict:
    travel_flow = {
        "flow_order": flow_order,
        "from_point": from_point,
        "to_point": to_point,
        "transit_time": transit_time,
        "transit_distance": transit_distance,
        "routes_map_file_path": None
    }

    append_travel_flow(travel_flow)

    store_route_static_map_image(travel_flow, flow_order, from_point["longitude"], from_point["latitude"], to_point["longitude"], to_point["latitude"])

    return travel_flow


# 두 쌍의 좌표를 입력 받아, 해당 경로의 지도 이미지를 조회하여 저장하는 함수
def store_route_static_map_image(travel_flow: dict, flow_order: int, start_x: str, start_y: str, end_x: str, end_y: str):
    http = get_pool_manager()
    api_key = os.getenv("TMAP_API_KEY")
    api_url = os.getenv("TMAP_ROUTES_IMAGE_ENDPOINT")
    request_params = {}
    version = "1"

    request_headers = urllib3.HTTPHeaderDict()
    request_headers.add("Content-Type", "image/png")

    request_params["version"] = version
    request_params["appKey"] = api_key
    request_params["startX"] = start_x
    request_params["startY"] = start_y
    request_params["endX"] = end_x
    request_params["endY"] = end_y

    response = http.request(
        method="GET",
        url=api_url,
        fields=request_params,
        headers=request_headers,
        preload_content=False
    )

    file_path = f"/Users/donghyeon/Desktop/development/ai-intelligence-app/agent2/maps/{flow_order}_{start_x}_{start_y}_{end_x}_{end_y}.png"

    with open(file_path, "wb") as out:
        while True:
            data = response.read(1024)
            if not data:
                break
            out.write(data)

    response.release_conn()

    travel_flow["routes_map_file_path"] = file_path


# Vector DB에서 거리 유사도를 기반으로 특정 토픽에 대한 컨텍스트를 추출하는 함수
def SearchTravelTopicContext(query: str) -> str:
    return retrieve_travel_topic_text_by_embeddings_similarity(query)


# Vector DB에서 거리 유사도를 기반으로 특정 여행 계획 기록에 대한 컨텍스트를 추출하는 함수
def SearchTravelFlowsHistoryArchiveContext(query: str) -> str:
    return retrieve_travel_history_archive_context_by_embeddings_similarity(query)


# 대화 종료 발언
def SayTerminate() -> str:
    return "TERMINATE"
