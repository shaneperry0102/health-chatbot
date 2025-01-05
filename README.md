# Healthcare AI Assistant Application

This application is an AI-powered healthcare assistant that integrates web search capabilities and Youtube video recommendation, offering a helpful environment for patients, doctors and concerned users.

## Key Features and Functionalities

1. **Intelligent Chat Interface**: 
   - Powered by Llama3 70B 8192, an advanced AI model from Groq.
   - Enables natural language interactions for queries.

2. **LangGraph-based Workflow**: 
   - Orchestrates AI decision-making processes.
   - Provides a real-time Mermaid diagram of the workflow in the sidebar.

3. **Intuitive Streamlit Interface**: 
   - Offers a clean, user-friendly interface for seamless interaction.

4. **Web Resource Access**: 
    - Capable of making API requests and accessing online information.

## Setup and Usage

### Python Dependency Installation

Before running the application, ensure you have configured the necessary API keys in the `secrets.toml` file located at the `.streamlit` of the project directory. Follow these steps for Python dependency installation:

1. Create a virtual environment by running:
   ```sh
   python -m venv .venv
   ```
   This command creates a new directory named `.venv` in your project directory, which will contain the Python executable and libraries.

2. Activate the virtual environment:
   - On Windows, run:
     ```cmd
     .\.venv\Scripts\activate
     ```
   - On macOS and Linux, run:
     ```sh
     source .venv/bin/activate
     ```
   After activation, your terminal prompt will change to indicate that the virtual environment is active.

3. With the virtual environment activated, install the required Python packages by running:
   ```sh
   pip install -r requirements.txt
   ```
   This command reads the `requirements.txt` file and installs all the listed packages along with their dependencies.

Remember to activate the virtual environment (`venv`) every time you work on this project. To deactivate the virtual environment and return to your global Python environment, simply run `deactivate`.

### Starting the Application

Finally, to start the application:

1. Launch the Streamlit application:
   ```sh
   streamlit run app.py
   ```

2. Access the application via your web browser to start interacting with the AI assistant.
