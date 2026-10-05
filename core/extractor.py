#Actionableitems , decision , questions  to extract from meeting transcript using langchain and groq llm
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os


# Initialize Groq LLM
def get_llm():
    return ChatGroq(
       model="openai/gpt-oss-120b",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2
    )


# Split long transcript into smaller chunks
def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=5000,
        chunk_overlap=500,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    return splitter.split_text(transcript)


# Create a LangChain prompt chain
def build_chain(system_prompt: str, llm):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{text}")
    ])

    return prompt | llm | StrOutputParser()


# Merge extracted results and remove duplicate information
def combine_results(results: list, system_prompt: str, llm) -> str:
    results = [result.strip() for result in results if result.strip()]

    if not results:
        return ""

    if len(results) == 1:
        return results[0]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=5000,
        chunk_overlap=300,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chain = build_chain(system_prompt, llm)

    # Keep reducing batches until they fit into one result
    while len(results) > 1:
        combined_text = "\n\n".join(results)
        batches = splitter.split_text(combined_text)

        # Avoid an infinite loop if splitting doesn't reduce the count
        if len(batches) >= len(results):
            batches = [
                "\n\n".join(results[i:i + 5])
                for i in range(0, len(results), 5)
            ]

        results = [
            chain.invoke({"text": batch})
            for batch in batches
        ]

    return results[0]


# Generic chunk-based extraction
def extract_from_transcript(
    transcript: str,
    extraction_prompt: str,
    combine_prompt: str,
    no_result_message: str
) -> str:

    if not transcript or not transcript.strip():
        return no_result_message

    llm = get_llm()
    chunks = split_transcript(transcript)

    map_chain = build_chain(extraction_prompt, llm)

    # Extract information from each chunk
    chunk_results = []

    for i, chunk in enumerate(chunks, start=1):
        result = map_chain.invoke({"text": chunk})

        if result.strip() and no_result_message.lower() not in result.lower():
            chunk_results.append(result)

    if not chunk_results:
        return no_result_message

    # Merge results and remove duplicates
    final_result = combine_results(
        chunk_results,
        combine_prompt,
        llm
    )

    return final_result.strip() or no_result_message


# 1. Extract Action Items
def extract_action_items(transcript: str) -> str:
    extraction_prompt = (
        "You are an expert meeting analyst. Extract all action items "
        "from this portion of a meeting transcript.\n"
        "For each action item, provide:\n"
        "- Task description\n"
        "- Owner (who is responsible, or 'Not specified')\n"
        "- Deadline (if mentioned, otherwise 'Not specified')\n"
        "Do not invent missing details. Return a numbered list. "
        "If no action items are found, return exactly: "
        "'No action items found.'"
    )

    combine_prompt = (
        "You are an expert meeting analyst. Combine the action items "
        "extracted from different portions of a meeting transcript.\n"
        "Remove duplicate or repeated action items. Preserve distinct tasks, "
        "owners and deadlines. Do not invent missing details. "
        "If the same task appears with additional information, merge it "
        "accurately. Return a clear numbered list with task, owner and "
        "deadline. If no action items exist, say "
        "'No action items found.'"
    )

    return extract_from_transcript(
        transcript,
        extraction_prompt,
        combine_prompt,
        "No action items found."
    )


# 2. Extract Key Decisions
def extract_key_decisions(transcript: str) -> str:
    extraction_prompt = (
        "You are an expert meeting analyst. Extract all key decisions "
        "explicitly made in this portion of a meeting transcript. "
        "Do not confuse suggestions or discussions with final decisions. "
        "Return a numbered list. If none are found, return exactly: "
        "'No key decisions found.'"
    )

    combine_prompt = (
        "You are an expert meeting analyst. Combine key decisions "
        "extracted from different portions of a meeting transcript. "
        "Remove duplicates, preserve distinct decisions and do not "
        "turn suggestions into confirmed decisions. Do not invent facts. "
        "Return a clear numbered list. If none exist, say "
        "'No key decisions found.'"
    )

    return extract_from_transcript(
        transcript,
        extraction_prompt,
        combine_prompt,
        "No key decisions found."
    )


# 3. Extract Open Questions
def extract_questions(transcript: str) -> str:
    extraction_prompt = (
        "You are an expert meeting analyst. Extract all unresolved "
        "questions, unanswered issues or topics needing follow-up "
        "from this portion of a meeting transcript. "
        "Do not include questions that were clearly answered. "
        "Return a numbered list. If none are found, return exactly: "
        "'No open questions found.'"
    )

    combine_prompt = (
        "You are an expert meeting analyst. Combine unresolved questions "
        "and follow-up topics extracted from different portions of a "
        "meeting transcript. Remove duplicates, preserve distinct "
        "questions and exclude issues that were clearly resolved. "
        "Do not invent information. Return a clear numbered list. "
        "If none exist, say 'No open questions found.'"
    )

    return extract_from_transcript(
        transcript,
        extraction_prompt,
        combine_prompt,
        "No open questions found."
    )
