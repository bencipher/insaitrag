import os


def main():
    print("How would you like to run the agent?")
    print("1. CLI Mode")
    print("2. Browser Mode (Streamlit)")

    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        print("Running in CLI mode...")
        os.system("python src/agent.py cli")
    elif choice == "2":
        print("Launching in Browser mode...")
        os.system("streamlit run src/agent.py")
    else:
        print("Invalid choice. Please enter 1 for CLI mode or 2 for Browser mode.")


if __name__ == "__main__":
    main()
