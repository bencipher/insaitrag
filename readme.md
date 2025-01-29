# **Conversational Agent Documentation**

## **Overview**

This document provides detailed instructions on how to set up, run, and deploy the conversational agent, along with sample queries, responses, and an evaluation framework for assessing the agent's performance. The agent can be used in **two modes**: **CLI Mode** (via terminal) or **Browser Mode** (via Streamlit). This flexibility allows users to interact with the agent based on their preferred approach.

---

## **Setting Up the Environment**

### **Pre-Conditions**

Before setting up the environment, you need to configure the following environment variables in a `.env` file or directly in your system environment:

#### **1. General Requirements**

- **OpenAI API Key**  
  Obtain an OpenAI API key and set it in the `.env` file:
  ```bash
  OPENAI_API_KEY=your_openai_api_key
  ```

- **LogFire API Key**  
  Obtain a LogFire API key (temporary keys can be used) and set it in the `.env` file:
  ```bash
  LOGFIRE_API_KEY=your_logfire_api_key
  ```

- **ChromaDB Authentication Credentials**  
  Set your ChromaDB authentication credentials:
  ```bash
  CHROMA_AUTH_CREDENTIALS=your_generated_hex_token
  CHROMA_SERVER_AUTHN_PROVIDER=chromadb.auth.token_authn.TokenAuthenticationServerProvider
  CHROMA_AUTH_TOKEN_TRANSPORT_HEADER=X-Chroma-Token
  ```

- **ChromaDB Host and Port Configuration**  
  Depending on your deployment setup, configure the `CHROMA_HOST` and `CHROMA_PORT` environment variables in your `.env` file:

  - **Fully Dockerized Setup**:
    ```bash
    CHROMA_HOST=vector_db
    CHROMA_PORT=8000
    ```

  - **Local Setup (DB inside a container)**:
    Uncomment the following lines if you are running the application locally but the database is inside a Docker container:
    ```bash
    # CHROMA_HOST=localhost
    # CHROMA_PORT=8019
    ```

#### **2. Special Environment Variable for Full Docker Mode**

For running the agent entirely in Docker (Browser Mode only), add the following environment variable:
```bash
RUN_MODE=browser
```

### **Setting Up the Python Environment**

1. **Install Poetry**  
   Ensure you have Poetry installed on your machine. If not, install it using:
   ```bash
   pip install poetry
   ```

2. **Initialize and Activate Poetry**  
   Navigate to the root folder of the project where `pyproject.toml` is located. Initialize the environment using:
   ```bash
   poetry install
   ```

3. **Activate the Poetry shell:**
   ```bash
   poetry shell
   ```

### **Setting Up Vector Database**

The agent uses ChromaDB as the vector database to store embeddings and facilitate semantic search. There are two ways to spin up ChromaDB: either as a standalone container for local use or as part of the full Docker application.

1. **Running ChromaDB Standalone (for CLI or Local Use)**  
   To use the agent locally (with CLI or Browser Mode), start ChromaDB as a standalone container:
   ```bash
   docker compose up -d --build vector-db
   ```

   Once ChromaDB is up, you can proceed with preparing the vector database.

2. **Preparing the Vector Database**  
   After ChromaDB is running, generate embeddings for the FAQ data by executing:
   ```bash
   python src/setup_vector.py
   ```

## **Running the Conversational Agent**

The agent can run in two modes: CLI Mode (local use) and Browser Mode (local or full Docker deployment). Choose a method based on your preference.

### **Method 1: Local Setup (CLI or Browser Mode)**

1. **Run the Application**  
   To start the agent locally, execute the following command:
   ```bash
   python main.py
   ```

2. **Select a Mode**  
   When prompted, you can choose between CLI Mode or Browser Mode:
   - **CLI Mode**: Interact with the agent in the terminal.
   - **Browser Mode**: A Streamlit app will be launched, and you can interact with the agent through a browser at the provided URL (e.g., `http://localhost:8501`).

### **Method 2: Full Docker Deployment (Browser Mode Only)**

If you prefer to use the agent entirely in Docker (Browser Mode only), follow these steps:

1. **Configure the Environment**  
   Set the following environment variable to enable Browser Mode:
   ```bash
   RUN_MODE=browser
   ```

   You can do this in two ways:
   - Set it in the `.env` file.
   - Pass it directly in the Docker build command.

2. **Build and Run the Docker Application**  
   Run the following command to build and start the application:
   ```bash
   docker-compose up --build -d
   ```

3. **Access the Streamlit Interface**  
   Once the container is running, access the agent via a browser at the URL provided by Streamlit (e.g., `http://localhost:8501`).

## **Summary of Usage Modes**

1. **CLI Mode**
   - **Use Case**: Local execution only.
   - **How to Run**: Start the application locally (`python main.py`) and select CLI Mode when prompted.

2. **Browser Mode**
   - **Use Case**: Available both locally and in full Docker deployment.
   - **How to Run**:
     - **Locally**: Start the application locally (`python main.py`) and select Browser Mode when prompted.
     - **In Docker**: Set `RUN_MODE=browser` and execute the Docker build command.

---

This documentation provides a comprehensive guide to setting up, running, and evaluating this conversational agent. For additional support, please contact me at femolak@gmail.com.
