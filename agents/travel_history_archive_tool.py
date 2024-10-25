from agents.azure_cosmos_nosql_vector_db import upsert_travel_flows_for_history_archive, \
    retrieve_vector_similarity_of_travel_flows_history_archive
from agents.azure_text_embedding_tool import generate_embeddings
from utils.text_splitter import trim_text_source, split_text_for_travel_flows
from autogen import AssistantAgent, GroupChatManager, GroupChat, UserProxyAgent
import os
from dotenv import load_dotenv
from autogen.cache import Cache

load_dotenv()


AZURE_OPEN_AI_ENDPOINT = os.getenv("AZURE_OPEN_AI_ENDPOINT")
AZURE_OPEN_AI_API_KEY = os.getenv("AZURE_OPEN_AI_API_KEY")
AZURE_OPEN_AI_API_VERSION = os.getenv("AZURE_OPEN_AI_API_VERSION")
AZURE_OPEN_AI_DEPLOYMENT_NAME = os.getenv("AZURE_OPEN_AI_DEPLOYMENT_NAME")


PROMPT_MESSAGE = """
input 으로 제공된 여행 기록 정보를 요약해줘.

시작해!
여행 기록 정보 : {input}
"""


# 텍스트 임베딩 프로세스 진행
def proceed_embeddings_for_travel_flows_history_archive(travel_flows_summary: str):

    trimmed = trim_text_source(travel_flows_summary)

    # category : 0001 => travel_flows
    for split in split_text_for_travel_flows(trimmed):
        embeddings = generate_embeddings(split)
        upsert_travel_flows("0001", "여행 기록 요약", split, embeddings)


def upsert_travel_flows(category: str, topic: str, content: str, embeddings: list):
    upsert_result = upsert_travel_flows_for_history_archive(category, topic, content, embeddings)


def retrieve_travel_history_archive_context_by_embeddings_similarity(query: str) -> str:
    topic_text = ""
    for split in split_text_for_travel_flows(query):
        embeddings = generate_embeddings(split)
        topics = retrieve_vector_similarity_of_travel_flows_history_archive(embeddings)
        for topic in topics:
            topic_text += topic["content_text"]
    return topic_text


def get_prompt_message(sender, recipient, context):
    return PROMPT_MESSAGE.format(input=context["question"])


def summarize_travel_flows(travel_flows: dict) -> str:

    config_list = [{
        "model": AZURE_OPEN_AI_DEPLOYMENT_NAME,
        "api_type": "azure",
        "api_key": AZURE_OPEN_AI_API_KEY,
        "base_url": AZURE_OPEN_AI_ENDPOINT,
        "api_version": AZURE_OPEN_AI_API_VERSION,
    }]

    user_agent = UserProxyAgent(
        name="user_agent",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    summary_agent = AssistantAgent(
        name="summary_agent",
        llm_config={"config_list": config_list, "cache_seed": None},
        code_execution_config=False,
        system_message="""
        너는 여행 기록을 요약된 글을 생성하는 여행 기록 요약 전문가야.
        여행 정보를 전달 받으면, 그 정보를 요약된 글로 생성해줘.
        요약글 내용에 반드시 포함 되어야 하는 항목:
        - 여행 날짜(연도-월-일), 여행 멤버, 여행 멤버의 관계, 여행 목적, 여행 장소 목록
        요약글 작성 시 필수 준수 사항:
        - 400자 이내로 작성
        - 소설가 처럼 이야기 하듯이 작성
        - 반드시 현재 시제로 표현해. 과거 시제 사용 금지
        - 순전히 너의 문장 구성 능력으로 작성
        - 요약글 작성이 완료되면 반드시 SayTerminate 도구를 실행하여 대화를 종료해
        요약글 예문:
        - 2024년 8월 2일 여행 멤버 남성0001, 여성0001, 여성0002 3명이 여름휴가 목적으로 여행한다. 장소는 서울 광화문, 경복궁, 맥도날드...(더 상세하게)
        파라미터 travel_flows 구성 주요 속성 의미:
        - members: 여행 멤버 목록
        - travel_date: 여행 날짜
        - relationship: 여행 멤버 간 관계
        - purpose: 여행 목적
        - point_type_code: 여행 장소 유형 코드
        - point_name: 여행 장소명
        """
    )

    ToolAgent = UserProxyAgent(
        name="ToolAgent",
        human_input_mode="NEVER",
        llm_config=False,
        code_execution_config=False,
        description="필요한 도구(tool)를 적시 적소에 실행 시키는 도구 실행 전문 에이전트",
    )

    group_chat = GroupChat(
        max_round=100,
        agents=[user_agent, summary_agent, ToolAgent],
        messages=[]
    )

    group_chat_manager = GroupChatManager(
        name="group_chat_manager",
        is_termination_msg=lambda msg: "terminate" in msg["content"].lower(),
        llm_config={"config_list": config_list, "cache_seed": None},
        groupchat=group_chat,
        description='''
    group_chat_manager 는 그룹 채팅을 관리하는 매니저.
    
    group_chat_manager 가 반드시 준수 해야 할 항목:
    - 도구(tool) 활용 여부는 전적으로 summary_agent 의 판단에 의해 결정 되어야 한다.
    - 절대 user를 speaker로 지정하지 않음.
    - summary_agent 와의 소통과 협업이 매우 중요하다.
    '''
    )

    ToolAgent \
        .register_for_execution(name="SayTerminate")(SayTerminate)

    summary_agent \
        .register_for_llm(
            name="SayTerminate",
            description="""
            대화 종료 함수
            """
    )(SayTerminate)

    with Cache.disk(cache_seed=47) as cache:
        chat_result = user_agent.initiate_chat(
            recipient=group_chat_manager,
            message=get_prompt_message,
            question=f"{travel_flows}",
            cache=cache,
            silent=True
        )

    messages = []
    travel_flows_summary = ""

    chat_list = chat_result.chat_history
    for chat_dict in chat_list:
        if ("name" in chat_dict) and (chat_dict["name"] == "summary_agent"):
            chat_dict["content"] = chat_dict["content"].replace("TERMINATE", "")
            messages.append(chat_dict["content"])

    print("################# 여행 계획 요약 시작 #################")
    for message in messages:
        travel_flows_summary += message
        print(f"{travel_flows_summary}")

    print("################# 여행 계획 요약 끝 #################")

    return travel_flows_summary


# 대화 종료 발언
def SayTerminate() -> str:
    return "TERMINATE"
