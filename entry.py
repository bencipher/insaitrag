import os


def main():
    attempts = 0
    max_attempts = 5

    while attempts < max_attempts:
        print("How would you like to run the agent?")
        print("1. CLI Mode")
        print("2. Browser Mode (Streamlit)")
        print("0. Exit")

        choice = input("Enter your choice (1, 2, or 0 to exit): ").strip()

        if choice == "1":
            print("Running in CLI mode...")
            os.system("python src/agent.py cli")
            break
        elif choice == "2":
            print("Launching in Browser mode...")
            os.system("streamlit run src/agent.py")
            break
        elif choice == "0":
            print("Exiting the program.")
            break
        else:
            print(
                "Invalid choice. Please enter 1 for CLI mode, 2 for Browser mode, or 0 to exit."
            )
            attempts += 1

        if attempts >= max_attempts:
            print("You have exceeded the maximum number of attempts. Exiting.")


if __name__ == "__main__":
    main()
