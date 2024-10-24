import os

from dotenv import load_dotenv

load_dotenv("/Users/donghyeon/Desktop/development/ai-intelligence-app/agent2/config/.env")

AZURE_OPEN_AI_ENDPOINT = os.getenv("AZURE_OPEN_AI_ENDPOINT")
AZURE_OPEN_AI_API_KEY = os.getenv("AZURE_OPEN_AI_API_KEY")
AZURE_OPEN_AI_API_VERSION = os.getenv("AZURE_OPEN_AI_API_VERSION")
AZURE_OPEN_AI_DEPLOYMENT_NAME = os.getenv("AZURE_OPEN_AI_DEPLOYMENT_NAME")

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from agents.agent_tools import SearchTravelTopicContext, SearchWeb
from autogen.cache import Cache
from agents.travel_history_archive_tool import retrieve_travel_history_archive_context_by_embeddings_similarity


final_messages = []


def AppendFinalMessage(message: str):
    final_messages.append(message)


# 대화 종료 발언
def SayTerminate() -> str:
    return "TERMINATE"


# Vector DB에서 거리 유사도를 기반으로 특정 여행 계획 기록에 대한 컨텍스트를 추출하는 함수
def SearchTravelFlowsHistoryArchiveContext(query: str) -> str:
    return retrieve_travel_history_archive_context_by_embeddings_similarity(query)


config_list = [{
    "model": AZURE_OPEN_AI_DEPLOYMENT_NAME,
    "api_type": "azure",
    "api_key": AZURE_OPEN_AI_API_KEY,
    "base_url": AZURE_OPEN_AI_ENDPOINT,
    "api_version": AZURE_OPEN_AI_API_VERSION,
}]

PROMPT_MESSAGE = """
너는 챗봇 사용자의 질문이나 요구사항을 잘 이해하고, 최종 답변을 위한 행동을 충실히 수행하는 대화상대 이다.

ChatbotAgent가 반드시 준수해야 하는 항목:
- 제공된 도구(tool)와 너의 추론 능력, 글 요약 능력을 최대로 발휘하여 챗봇 사용자가 만족할 수 있는 최종 답변을 준비한다.
- 최종 답변 준비가 완료되면, 반드시 AppendFinalMessage 도구를 실행하여 최종 답변을 저장해야 한다.
- 최종 답변 저장이 완료되면, 반드시 SayTerminate 도구를 실행해야 한다.

아래와 같은 format 사용해서 프로세스를 수행해:
    
질문: 인풋(input)으로 들어온 질문 이다. 너는 이 질문에 대해 답변을 해야 한다.
생각: 너는 항상 니가 답변을 준비하기 위해 무엇을 해야할 지 생각해고 계획을 세워야 한다.
행동: 니가 계획한 것을 수행하는 것이 행동이다. 너에게 제공된 도구(tool)를 활용하여 생각한 것을 행동으로 옮겨야 해.
행동 입력: 행동을 수행하기 위한 입력값. 너는 이 입력값을 통해 도구를 사용하고 행동을 수행해야 해.
관찰: 행동의 결과. 너는 앞서 수행된 행동의 결과를 관찰하고 분석해야 해.
... (이 프로세스는 반복 가능하다.)
생각: 나는 지금 최종 답변을 알고 있다.
최종 답변: 최초 인풋(input) 질문에 대한 최종적인 답변이야.

시작해!
질문: {input}
"""

ChatbotAgent = AssistantAgent(
    name="ChatbotAgent",
    llm_config={"config_list": config_list, "cache_seed": None},
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    description='''
        ChatbotAgent는 챗봇 사용자의 질문이나 요구사항을 잘 이해하고, 최종 답변을 위한 행동을 충실히 수행하는 챗봇 사용자의 대화상대 이다.
        '''
)

# Register functions for each agent

ChatbotAgent \
    .register_for_llm(
    name="SearchWeb",
    description="""
    웹 기반 검색을 수행하는 도구
    함수 입력 파라미터 상세:
    - query: 검색 질의
    """
)(SearchWeb)

ChatbotAgent \
    .register_for_llm(
    name="SearchTravelTopicContext",
    description="""
    DB에 저장된 WiKi 페이지 기반 검색을 수행하는 도구
    함수 입력 파라미터 상세:
    - query: 검색 질의
    """
)(SearchTravelTopicContext)

ChatbotAgent \
    .register_for_llm(
    name="SearchTravelFlowsHistoryArchiveContext",
    description="""
    여행 기록 기반으로 관련 정보 검색을 수행하는 도구
    함수 입력 파라미터 상세:
    - query: 검색 질의
    여행 기록 정보 주요 포함 항목:
    - 여행 날짜(연도-월-일), 여행 멤버, 여행 멤버의 관계, 여행 목적, 여행 장소 목록 등
    """
)(SearchTravelFlowsHistoryArchiveContext)

ChatbotAgent \
    .register_for_llm(
    name="AppendFinalMessage",
    description="""
    최종 답변을 저장하는 도구
    함수 입력 파라미터 상세:
    - message: 최종 답변
    """
)(AppendFinalMessage)

ChatbotAgent \
    .register_for_llm(
    name="SayTerminate",
    description="""
    대화 종료를 위해 TERMINATE 메시지를 반환하는 도구
    """
)(SayTerminate)


ToolsAgent = UserProxyAgent(
    name="ToolsAgent",
    human_input_mode="NEVER",
    code_execution_config=False,
    description="""
    필요한 도구(tool)를 적시 적소에 실행 시키는 도구 실행 전문 에이전트
    """,
)

ToolsAgent \
    .register_for_execution(name="SayTerminate")(SayTerminate)

ToolsAgent \
    .register_for_execution(name="SearchWeb")(SearchWeb)

ToolsAgent \
    .register_for_execution(name="SearchTravelTopicContext")(SearchTravelTopicContext)

ToolsAgent \
    .register_for_execution(name="SearchTravelFlowsHistoryArchiveContext")(SearchTravelFlowsHistoryArchiveContext)

ToolsAgent \
    .register_for_execution(name="AppendFinalMessage")(AppendFinalMessage)


def get_prompt_message(sender, recipient, context):
    return PROMPT_MESSAGE.format(input=context["question"])


def chat(message) -> list:

    final_messages.clear()

    with Cache.disk(cache_seed=45) as cache:

        chat_result = ChatbotAgent.initiate_chat(
            recipient=ToolsAgent,
            message=get_prompt_message,
            question=f"{message}",
            cache=cache
        )

    return final_messages
