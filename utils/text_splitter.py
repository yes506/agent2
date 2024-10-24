from langchain.text_splitter import RecursiveCharacterTextSplitter


def split_text(source: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False
    )
    chunks = splitter.split_text(source)
    return chunks


def split_text_for_travel_flows(source: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False
    )
    chunks = splitter.split_text(source)
    return chunks


def trim_text_source(raw_source: str) -> str:
    trimmed_source = raw_source.rstrip().lstrip().replace("\n", " ")
    return trimmed_source
