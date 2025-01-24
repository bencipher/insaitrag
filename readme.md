# **Conversational Agent Documentation**

## **Overview**

This document provides detailed instructions on how to set up, run, and deploy the conversational agent, along with sample queries, responses, and an evaluation framework for assessing the agent's performance.

---

## **Setting Up the Environment**

### **Pre-Conditions**

Before setting up the environment, make sure to set the following environment variables and update the `.env.example` file with the appropriate API keys:

#### **OpenAI API Key**

1. Create an account on OpenAI and obtain an API key.
2. Update the `.env.example` file with the OpenAI API key:
   ```bash
   OPENAI_API_KEY=your_openai_api_key
   ```

#### **LogFire API Key**

3. Obtain the LogFire API key (for convenience, a temporary key is provided).
4. Update the `.env.example` file with the LogFire API key:
   ```bash
   LOGFIRE_API_KEY=your_logfire_api_key
   ```

Please note that the LogFire API key provided is temporary and should be rotated later for security reasons.

### **1. Setting Up ChromaDB for Vector Storage**

ChromaDB is used as the vector database to store embeddings and facilitate semantic search for the agent. Follow these steps to set it up:

#### **Pulling and Running ChromaDB Docker Container**

1. Pull the ChromaDB container:
   ```bash
   docker pull chromadb/chroma
   ```
2. Run the container, mapping port `8019` on your local machine to port `8000` in the container:
   ```bash
   docker run -p 8019:8000 chromadb/chroma
   ```

---

### **2. Setting Up the Python Environment with Poetry**

#### **Initialize Poetry**

1. Navigate to the root folder of your project where the `poetry.lock` file is located.
2. Initialize Poetry:
   ```bash
   poetry init
   ```
3. Install dependencies using:
   ```bash
   poetry install
   ```

#### **Activate the Poetry Environment**

1. Start the Poetry environment:
   ```bash
   poetry shell
   ```
2. For Windows users, activate the environment using the provided script:
   ```bash
   ./scripts/shell/activate
   ```

---

### **3. Preparing the Vector Database**

Once ChromaDB is running and your Python environment is set up, you need to create embeddings for the FAQ data. Run the following script:

```bash
python src/setup_vector.py
```

This script will generate embeddings from your FAQ dataset and store them in ChromaDB. Ensure your Docker container is running and accessible before executing this step.

---

## **Running the Conversational Agent**

The main entry point for the agent is the `main.py` file, which provides two interaction modes: **CLI Mode** and **Browser Mode (via Streamlit)**.

### **1. CLI Mode**

To run the agent in CLI mode:

```bash
python main.py
```

Follow the on-screen instructions to select **CLI Mode**. The agent will respond to your typed queries in the terminal.

### **2. Browser Mode (Streamlit)**

To run the agent in Browser Mode:

1. Start the Streamlit app:
   ```bash
   python main.py
   ```
2. Choose the option for **Browser Mode** when prompted.
3. Open the provided local or network URL (e.g., `http://localhost:8501`) in your web browser.
4. Interact with the agent using the chat interface.

---

This documentation provides a comprehensive guide to setting up, running, and evaluating this conversational agent. For additional support, please contact me femolak@gmail.com.
