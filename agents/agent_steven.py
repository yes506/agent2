import os

from dotenv import load_dotenv

load_dotenv("/Users/donghyeon/Desktop/development/ai-intelligence-app/agent2/config/.env")

PROMPT_MESSAGE = """
    너는 최고의 통찰력, 기획력, 꼼꼼함을 가진 행복한 여행을 설계 해주는 여행 플래너야. 여행 계획 세워줘"""

# PROMPT_MESSAGE = """
#     너는 최고의 통찰력, 기획력, 꼼꼼함을 가진 행복한 여행을 설계 해주는 여행 플래너야.
#
#     여행 계획 수립 시 필수 고려 사항:
#         - 제공된 도구(tool)만 사용해.
#         - input으로 주어진 조건의 상관관계를 최대한 고려해.
#         - 동선은 출발지점에서 시작하여 복귀해야 해.
#         - 여행 가용 시간 조건을 반드시 준수하여, 동선을 설계해.
#         - 각 장소간 이동하는 시간, 각 장소의 특성에 맞는 체류시간을 반드시 세밀하게 계산해서 동선을 설계해.
#         - 주소 정보가 없거나, 올바르지 않은 곳은 제외해.
#         - 주어진 식사 가능 시간대 안에서는 반드시 식사가 이루어 져야 하고, 구체적인 방문 장소를 제안해.
#         - 커피, 차, 디저트 등은 식사 시간과 관계 없어.
#         - 여행은 여행자의 성향과 취향 등 다양한 조건을 세심하게 고려해야 하고, 다양한 경험을 제공해야 하며 최고의 만족도를 제공해.
#
#     최종 답변 필수 조건:
#         - 동선 형식 : 지점1(출발지점) -> 지점2(추천장소1) -> 지점3(추천장소2) -> ... -> 지점n(도착지점)
#         - 계획된 여행 동선에서의 모든 지점(1~n) 각각의 정보 파라미터를 포함하여 반드시 get_each_point_info 도구를 반드시 n회 실행해.
#         - 출발지점과 도착지점이 동일하지만, 재활용하지 말고 반드시 구성 내용이 다른 새로운 동선으로 get_each_point_info 도구를 실행해.
#         - 모든 지점(1~n)에 대한 get_each_point_info 도구 실행이 완료되면, 반드시 get_travel_flow 도구를 실행하여 최종 여행 동선 정보를 완료해.
#         - 여기 까지 누락없이 수행했다면, 최종 답변은 완료된 것이고 SayTerminate 도구를 실행하여 대화를 종료해.
#
#     아래와 같은 format 사용해서 프로세스를 수행해:
#
#     질문: 인풋(input)으로 들어온 질문 이다. 너는 이 질문에 대해 답변을 해야 한다.
#     생각: 너는 항상 니가 답변을 준비하기 위해 무엇을 해야할 지 생각해고 계획을 세워야 한다.
#     행동: 너가 계획한 것을 수행하는 것이 행동이다. 너에게 제공된 도구(tool)을 활용하여 생각한 것을 행동으로 옮겨야 해.
#     행동 입력: 행동을 수행하기 위한 입력값. 너는 이 입력값을 통해 행동을 수행해야 해.
#     관찰: 행동의 결과. 너는 앞서 수행된 행동의 결과를 관찰하고 분석해야 해.
#     ... (이 프로세스는 반복 가능하다.)
#     생각: 나는 지금 최종 답변을 알고 있다.
#     최종 답변: 최초 인풋(input) 질문에 대한 최종적인 답변이야.
#
#     시작해!
#     질문: {input}
#     """

PROMPT_MESSAGE = """
    #역할 : 너는 최고의 통찰력, 기획력, 꼼꼼함을 가진 행복한 여행을 설계 해주는 여행 플래너야.

    # 여행 계획 수립 시 필수 고려 사항:
        - 너에게 제공된 input의 사용자 입력 문구를 분석해서 반드시 필수 요소를 추출하고 기억해둔다. 필수 요소는 아래와 같다.
            - 출발 지점
            - 여행 반경(Km)
            - 여행자 수
            - 여행자 관계
            - 여행 목적
            - 여행 일자
            - 여행 가용 시작 시간
            - 여행 가용 종료 시간
            - 점심 식사 가능 시작 시간
            - 점심 식사 가능 종료 시간
            - 저녁 식사 가능 시작 시간
            - 저녁 식사 가능 종료 시간
            - 여행자 정보
            
        - 제공된 도구(tool)만 사용해.
        - input으로 주어진 조건의 상관관계를 최대한 고려해.
        - 동선은 출발지점에서 시작하여 복귀해야 해.
        - 여행 가용 시간 조건을 반드시 준수하여, 동선을 설계해.
        - 각 장소간 이동하는 시간, 각 장소의 특성에 맞는 체류시간을 반드시 세밀하게 계산해서 동선을 설계해.
        - 주소 정보가 없거나, 올바르지 않은 곳은 제외해.
        - 주어진 식사 가능 시간대 안에서는 반드시 식사가 이루어 져야 하고, 구체적인 방문 장소를 제안해.
        - 커피, 차, 디저트 등은 식사 시간과 관계 없어.
        - 여행은 여행자의 성향과 취향 등 다양한 조건을 세심하게 고려해야 하고, 다양한 경험을 제공해야 하며 최고의 만족도를 제공해.

    # 최종 답변 필수 조건:
        - 동선 형식 : 지점1(출발지점) -> 지점2(추천장소1) -> 지점3(추천장소2) -> ... -> 지점n(도착지점)
        - 계획된 여행 동선에서의 모든 지점(1~n) 각각의 정보 파라미터를 포함하여 반드시 get_each_point_info 도구를 반드시 n회 실행해.
        - 출발지점과 도착지점이 동일하지만, 재활용하지 말고 반드시 구성 내용이 다른 새로운 동선으로 get_each_point_info 도구를 실행해.
        - 모든 지점(1~n)에 대한 get_each_point_info 도구 실행이 완료되면, 반드시 get_travel_flow 도구를 실행하여 최종 여행 동선 정보를 완료해.
        - 여기 까지 누락없이 수행했다면, 최종 답변은 완료된 것이고 SayTerminate 도구를 실행하여 대화를 종료해.

    # 아래와 같은 format 사용해서 프로세스를 수행해:

        질문: 인풋(input)으로 들어온 질문 이다. 너는 이 질문에 대해 답변을 해야 한다.
        생각: 너는 항상 니가 답변을 준비하기 위해 무엇을 해야할 지 생각해고 계획을 세워야 한다.
        행동: 너가 계획한 것을 수행하는 것이 행동이다. 너에게 제공된 도구(tool)을 활용하여 생각한 것을 행동으로 옮겨야 해.
        행동 입력: 행동을 수행하기 위한 입력값. 너는 이 입력값을 통해 행동을 수행해야 해.
        관찰: 행동의 결과. 너는 앞서 수행된 행동의 결과를 관찰하고 분석해야 해.
        ... (이 프로세스는 반복 가능하다.)
        생각: 나는 지금 최종 답변을 알고 있다.
        최종 답변: 최초 인풋(input) 질문에 대한 최종적인 답변이야.

    시작해!
    질문: {input}
    """

AZURE_OPEN_AI_ENDPOINT = os.getenv("AZURE_OPEN_AI_ENDPOINT")
AZURE_OPEN_AI_API_KEY = os.getenv("AZURE_OPEN_AI_API_KEY")
AZURE_OPEN_AI_API_VERSION = os.getenv("AZURE_OPEN_AI_API_VERSION")
AZURE_OPEN_AI_DEPLOYMENT_NAME = os.getenv("AZURE_OPEN_AI_DEPLOYMENT_NAME")

from autogen import AssistantAgent
from autogen.cache import Cache
from agents.agent_tools import get_each_point_info, get_ToolAgent, SearchWeb, get_geo_code, convert_address, \
    get_pedestrian_routes_transit_time_distance, get_travel_flow, SayTerminate, SearchTravelFlowsHistoryArchiveContext
from agents.output_tool import get_travel_flows, clear_travel_flows, get_travel_flows_demo
from agents.travel_history_archive_tool import proceed_embeddings_for_travel_flows_history_archive,\
    summarize_travel_flows

config_list = [{
    "model": AZURE_OPEN_AI_DEPLOYMENT_NAME,
    "api_type": "azure",
    "api_key": AZURE_OPEN_AI_API_KEY,
    "base_url": AZURE_OPEN_AI_ENDPOINT,
    "api_version": AZURE_OPEN_AI_API_VERSION,
}]


def get_prompt_message(sender, recipient, context):
    return PROMPT_MESSAGE.format(input=context["question"])


def get_steven_jobs_agent():
    return AssistantAgent(
        name="AssistantAgent",
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        system_message="""
        너는 제공된 도구(tool)만 사용할 수 있어.
        너에게 제공된 모든 도구(tool)의 특징을 최대한 활용하고 최선을 다해 답변해.
        너에게 전달된 메시지 내용은 꼼꼼하게 기억하고 이해하고, 기재된 내용은 누락없이 반드시 지켜야 해.
        """,
        llm_config={"config_list": config_list, "cache_seed": None},
    )


# def plan(startPoint: str,
#          radius: int,
#          numberOfMember: int,
#          relationship: str,
#          purpose: str,
#          travelDate: str,
#          startTime: str,
#          endTime: str,
#          mealLunchStartTime: str,
#          mealLunchEndTime: str,
#          mealDinnerStartTime: str,
#          mealDinnerEndTime: str,
#          members: list):
def plan(corpus: str):

    clear_travel_flows()

    assistant = get_steven_jobs_agent()

    ToolAgent = get_ToolAgent()

    assistant \
        .register_for_llm(
            name="get_each_point_info",
            description="""
            동선 상 각 장소 정보 조회 함수
            - 함수 입력 상세:
                - order: 각 장소의 순서
                - point_type_code: 장소 유형 코드
                 - 0001 : 음식점/카페 등
                 - 0002 : 전시관
                 - 0003 : 공원, 고궁류
                 - 0004 : 쇼핑몰 등
                 - 0005 : 극장, 공연장
                 - 9998 : 최초 출발점
                 - 9999 : 최종 도착점
                - point_name: 장소/업소 고유명칭
                - travel_date: 여행 일자
                - members: 여행자 정보 목록
                - pros: 장점, cons: 단점
                - recommended: 추천 항목/메뉴
                - old_address: 지번 주소, new_address: 도로명 주소
                - longitude: 경도, latitude: 위도 
                - admission_fee_*: 연령별 입장료
                - operating_hours_on_* 요일별 영업시간
                - break_time_on_* 요일별 브레이크 타임 (없으면 미표기)
                - expected_arrival_time: 해당 장소 예상 도착 시간 (hh:mm)
                - expected_stay_time: 해당 장소 예상 체류 시간 (분)
                - expected_departure_time: 다음 장소로 예상 출발 시간 (hh:mm)
            """
    )(get_each_point_info)

    assistant \
        .register_for_llm(
            name="SearchWeb",
            description="""
            필요한 각종 정보를 검색할 때 유용하다. 웹(web)이나 특정 소스로 부터 찾고자 하는 내용을 검색할 수 있고 그 결과를 반환.
            """
    )(SearchWeb)

    assistant \
        .register_for_llm(
            name="get_geo_code",
            description="""
            신주소 형식의 도로명 주소는 입력 불가. 구주소 형식의 지번 주소만 입력 가능.
            구주소 형식의 지번 주소를 입력 받아 좌표를 반환함. 좌표는 경도와 위도로 구성됨.
            - 함수 입력 상세
                - city_do: 구주소 형식의 지번 주소에서 시 또는 도 정보. // 필수 파라미터
                - gu_gun: 구주소 형식의 지번 주소에서 구 또는 군 정보. // 필수 파라미터
                - dong: 구주소 형식의 지번 주소에서 동 정보. // 필수 파라미터
                - bunji: 구주소 형식의 지번 주소에서 번지 정보. // 필수 파라미터
                - detail_address: 상세 주소 정보. // 선택 파라미터
            - 반환 상세
                - longitude: 경도 정보
                - latitude: 위도 정보
        """
    )(get_geo_code)

    assistant \
        .register_for_llm(
            name="convert_address",
            description="""
            신주소 형식의 도로명 주소를 입력 받아, 구주소 형식의 지번 주소로 변환함.
            - 함수 입력 상세
                - req_address: 신주소 형식의 도로명 주소. //필수
            - 반환 상세
                - 구주소 형식의 지번 주소 문자열
            """
    )(convert_address)

    assistant \
        .register_for_llm(
            name="get_pedestrian_routes_transit_time_distance",
            description="""
            출발지 좌표와 도착지 좌표를 파라미터로 받아, 해당 도보 경로의 총 소요 시간(분), 소요 거리(미터)를 python tuple 타입으로 반환하는 도구.
            - 함수 입력 상세
                - start_x: 출발지 경도 좌표 // 필수 파라미터
                - start_y: 출발지 위도 좌표 // 필수 파라미터
                - start_name: 출발지 이름 // 필수 파라미터
                - end_x: 도착지 경도 좌표 // 필수 파라미터
                - end_y: 도착지 위도 좌표 // 필수 파라미터
                - end_name: 도착지 이름 // 필수 파라미터
            - 반환 상세
                - tuple(도보 경로의 총 소요 시간, 도보 경로의 총 소요 거리)
            """
    )(get_pedestrian_routes_transit_time_distance)

    assistant \
        .register_for_llm(
            name="get_travel_flow",
            description="""
            출발지점 정보, 도착지점 정보, 각 지점간 이동 소요 시간을 파라미터로 받아, 여행 동선 정보를 반환하는 도구.
            - 함수 입력 상세:
                - flow_order: 여행 동선 순서 (1, 2, 3, 4, ...) // 필수 파라미터
                - from_point: 출발지점 정보 (get_each_point_info 도구를 실행하여 얻은 python dictionary) // 필수 파라미터
                - to_point: 도착지점 정보 (get_each_point_info 도구를 실행하여 얻은 python dictionary) // 필수 파라미터
                - transit_time: 두 지점간 이동 소요 시간이 계산된 값 (분) // 필수 파라미터
                - transit_distance: 두 지점간 이동 거리가 계산된 값 (미터) // 필수 파라미터
            - 반환 상세:
                - 입력으로 받은 두 지점 사이의 여행 동선 정보 및 각 지점에 대한 상세 정보
            """
    )(get_travel_flow)

    assistant \
        .register_for_llm(
            name="SearchTravelFlowsHistoryArchiveContext",
            description="""
            여행 기록 기반으로 관련 정보 검색을 수행하는 도구
            함수 입력 파라미터 상세:
            - query: 검색 질의 (예) 2024년 남성0001, 여성0001 춘천 여행 기록
            여행 기록 정보 주요 포함 항목:
            - 여행 날짜(연도-월-일), 여행 멤버, 여행 멤버의 관계, 여행 목적, 여행 장소 목록 등
            """
    )(SearchTravelFlowsHistoryArchiveContext)

    assistant \
        .register_for_llm(
            name="SayTerminate",
            description="""
            대화 종료 메시지를 출력하는 함수
            """
    )(SayTerminate)

    with Cache.disk(cache_seed=43) as cache:

        print(f"""
        User_Proxy (to AssistantAgent):
        - user-input: {corpus}
        """)

        # assistant.initiate_chat(
        #     recipient=ToolAgent,
        #     message=get_prompt_message,
        #     question=f"""
        #     항목이 나열된 순서는 가중치와 무관함.
        #     다음 조건을 고려하여 멋진 여행 계획을 세워라.
        #     - 출발 지점: {startPoint}
        #     - 여행 반경(Km): {radius}
        #     - 여행자 수: {numberOfMember}
        #     - 여행자 관계: {relationship}
        #     - 여행 목적: {purpose}
        #     - 여행 일자: {travelDate}
        #     - 여행 가용 시작 시간: {startTime}
        #     - 여행 가용 종료 시간: {endTime}
        #     - 점심 식사 가능 시작 시간: {mealLunchStartTime}
        #     - 점심 식사 가능 종료 시간: {mealLunchEndTime}
        #     - 저녁 식사 가능 시작 시간: {mealDinnerStartTime}
        #     - 저녁 식사 가능 종료 시간: {mealDinnerEndTime}
        #     - 여행자 정보 목록: {members}
        #     """,
        #     cache=cache
        # )

        assistant.initiate_chat(
            recipient=ToolAgent,
            message=get_prompt_message,
            question=f"""
            항목이 나열된 순서는 가중치와 무관함.
            사용자가 인풋으로 전달한 사용자 입력 문구에서 필요 요소를 뽑아내어 멋진 여행 계획을 세워라.
            - 사용자 입력 문구: {corpus}
            """,
            cache=cache
        )

    # travel_flows = get_travel_flows(members, travelDate, relationship, purpose)
    travel_flows = get_travel_flows_demo()
    travel_flows_summary = summarize_travel_flows(travel_flows)
    proceed_embeddings_for_travel_flows_history_archive(travel_flows_summary)

    return travel_flows
