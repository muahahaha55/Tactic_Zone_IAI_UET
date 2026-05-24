from streamlit.runtime.state import SessionStateProxy
import threading
import datetime
import os
from io import StringIO
from Scrapper.PremierLeague import PremierLeagueCrawler
from Scrapper.scrapperData import Data as scrapperData
import RAG.Data as RAG_Data
from RAG.RAG_app import RAG_application
from langchain_grog import ChatGrog

# Update interval set to 24 hours (24 hr * 60 min * 60 sec)
UPDATE_INTERVAL = 24 * 60 * 60


def system_init(llm: ChatOpenAI):
    """
    Initialize the project variables and manage the RAG Vector Database.
    """
    if check_RAG_vector_db_exist():
        add_doc_to_RAG_vector_db()
    else:
        create_RAG_vector_db()
        add_doc_to_RAG_vector_db()


def update_PremierLeague_data(llm: ChatOpenAI):
    """
    Scrape the latest data from fbref.com, save to Excel, and transform to Markdown.
    """
    try:
        crawler = PremierLeagueCrawler()
        crawler.getTeamsUrl()

        for team_name, team_url in crawler.teamsInfo.items():
            team_data = crawler.scrap(team_url)
            crawler.preprocess_data(team_data)
            crawler.save_data(
                team_data,
                team_name,
                output_dir=scrapperData.team_data_savePath,
                save_as_excel=True
            )

        md_threads = []
        for team_name in crawler.teamsInfo.keys():
            thread = threading.Thread(
                target=transform_team_data_to_md,
                args=(scrapperData.team_data_savePath, team_name, llm)
            )
            md_threads.append(thread)
            thread.start()

        for thread in md_threads:
            thread.join()

    except Exception as e:
        print(f"Error during data update process: {e}")


def transform_team_data_to_md(filePath: str, team_name: str, llm: ChatOpenAI):
    """
    Transform the structured Excel team data into Markdown format via LLM.
    """
    try:
        team_stats_prompt = PremierLeagueCrawler.process_teamData_to_prompt(
            filePath + f"{team_name}_stats.xlsx", team_name
        )
        team_stats_md = PremierLeagueCrawler.transform_xlsx_to_md(team_stats_prompt, llm)
        PremierLeagueCrawler.save_md_to_file(team_stats_md, team_name)
    except Exception as e:
        print(f"Error transforming data for {team_name}: {e}")


def create_RAG_vector_db():
    """
    Create a new instance of the RAG vector store.
    """
    Rag_app = RAG_application()
    Rag_app.create_vector_db()


def add_doc_to_RAG_vector_db():
    """
    Load Markdown statistical data and ingest it into the Vector DB.
    """
    Rag_app = RAG_application()
    crawler = PremierLeagueCrawler()
    crawler.getTeamsUrl()
    try:
        for team_name in crawler.teamsInfo.keys():
            team_data = PremierLeagueCrawler.load_md_as_str(
                f"{scrapperData.team_data_savePath}{team_name}_all_stats.md"
            )
            docs = Rag_app.split_documents(team_data)
            Rag_app.add_doc_to_vector_db(docs)
    except Exception as e:
        print(f"Error adding documents to Vector DB: {e}")


def check_RAG_vector_db_exist() -> bool:
    """
    Check whether the Vector DB persist directory exists.
    """
    return os.path.exists(RAG_Data.persist_directory)


def setup_scheduled_updates(**session_state: SessionStateProxy):
    """
    Setup the background thread for periodic scheduled data updates.
    """
    if "update_thread" not in session_state or not session_state["update_thread"].is_alive():
        session_state["update_stop_event"] = threading.Event()
        session_state["update_thread"] = threading.Thread(
            target=_private_scheduled_update_worker,
            args=(session_state["update_stop_event"], session_state["LLM"])
        )
        session_state["update_thread"].daemon = True
        session_state["update_thread"].start()

    if "last_update_time" not in session_state:
        session_state["last_update_time"] = datetime.datetime.now()


def _private_scheduled_update_worker(stop_event: threading.Event, llm: ChatOpenAI):
    """
    Worker loop for handling scheduled tasks based on the defined interval.
    """
    while not stop_event.is_set():
        stop_event.wait(UPDATE_INTERVAL)
        if not stop_event.is_set():
            update_PremierLeague_data(llm)


def stop_scheduled_updates(**session_state: SessionStateProxy):
    """
    Stop the background update thread smoothly.
    """
    if "update_stop_event" in session_state:
        session_state["update_stop_event"].set()
        session_state["update_thread"].join(timeout=1)


def get_initial_graph_state():
    """
    Return the initial dictionary state for the main graph workflow.
    """
    return {
        "user_query": "",
        "user_query_history": [],
        "response": "",
        "llm_transcript": "",
        "adapter_route": "",
    }