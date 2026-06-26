# 🎯 AI Lead Qualifier & Pipeline Manager

> A privacy-first, full-stack Kanban web application that uses a local open-source LLM to ingest unstructured sales notes, extract BANT criteria, score leads, and generate customized outreach.

### The Business Problem
Sales Development Representatives (SDRs) spend hours every week translating unstructured call notes into CRM data and drafting personalized follow-up emails. Furthermore, feeding sensitive prospect data into cloud-based AI tools (like ChatGPT) creates massive data privacy and security risks for enterprise companies.

### The Solution
This application streamlines the SDR workflow using a **100% offline, locally hosted LLM**. It provides a frictionless Kanban interface that automatically qualifies leads using the BANT framework (Budget, Authority, Need, Timeline) and generates formulaic email drafts without ever sending proprietary data to a third-party server.

---

### 🛠 Tech Stack & Architecture
* **Environment:** Docker & Docker Compose (Multi-container architecture)
* **Backend API:** Python / Flask 
* **Database:** MongoDB 
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6+ Fetch API)
* **AI Inference:** Ollama running `llama3.2:1b` (Locally hosted)
* **Data Validation:** Pydantic

---

### 🚀 Key Features
* **Zero Data Leakage:** AI inference runs entirely within a local Docker container network, ensuring enterprise data privacy.
* **Asynchronous Kanban UI:** Drag-and-drop pipeline management with real-time UI metric updates via REST API calls.
* **BANT Extraction:** Forces strict JSON schemas to extract Budget, Authority, Need, and Timeline from messy text.
* **Formulaic Email Engine:** Generates customized cold emails based on extracted prospect needs and timelines.
* **Soft-Delete State Management:** Allows users to safely archive and restore leads without permanently dropping database records.

---

### 💻 How to Run Locally

1. Ensure **Docker Desktop** is installed and running on your machine.
2. Clone this repository and navigate to the root directory in your terminal:
   ```bash
   git clone https://github.com/05ashton/Lead-Qualifier.git
   cd Lead-Qualifier
   ```
3. Run the following command to build the environment and pull the AI model:
   ```bash
   docker-compose up --build
   ```
   *(Note: On the first run, Docker will automatically download the 1.3GB `llama3.2:1b` model. Please allow a moment for the Ollama container to initialize.)*
4. Open your web browser and navigate to: `http://localhost:5000`
5. To gracefully stop the application, press `Ctrl+C` in the terminal, or run `docker-compose down`.
