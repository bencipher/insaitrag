import os
from dotenv import load_dotenv

load_dotenv()


def start():
    mode = os.environ.get("RUN_MODE", "").lower()

    if mode == "cli":
        print("Running in CLI mode...")
        os.system("python src/agent.py cli")
    elif mode == "browser":
        print("Launching in Browser mode...")
        os.system("streamlit run src/agent.py")
    else:
        print("Invalid mode - exiting...")


if __name__ == "__main__":
    start()
