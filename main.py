import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

def main():
    mode = os.environ.get("RUN_MODE", "").lower()
    print(f"{mode=}")

    if mode == "cli":
        print("Running in CLI mode...")
        os.system("python src/agent.py cli")
    elif mode == "browser":
        print("Launching in Browser mode...")
        subprocess.run(["streamlit", "run", "src/agent.py"])
    else:
        print("Invalid mode - exiting...")


if __name__ == "__main__":
    main()
