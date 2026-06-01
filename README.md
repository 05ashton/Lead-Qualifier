# AI-Powered Lead Qualifier & Summarizer
**By Ashton James Curl**

**Summary:** A full-stack, Kanban-style web application that utilizes a local open-source LLM to ingest unstructured sales notes, extract BANT criteria (Budget, Authority, Need, Timeline), score leads, and generate customized cold email drafts.

### Tech Stack
*   **Environment Orchestration:** Docker & Docker Compose
*   **Backend API Server:** Python / Flask (v3.0.2)
*   **Database:** MongoDB (v6.0)
*   **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6+ with Async/Await Fetch API)
*   **AI Inference:** Ollama (v0.2.1) running `llama3.2:1b` via local container network
*   **Data Validation:** Pydantic (v2.6.3)

---

### Links
*   **Bitbucket Repository:** (https://bitbucket.org/ashton-first-repo/lead_qualifer/src/main/)
*   **Canvas Video Demo:** [INSERT_YOUR_CANVAS_VIDEO_LINK_HERE]

---

### How to Run Locally

1. Ensure Docker Desktop is installed and running on your machine.
2. Clone this repository and navigate to the root directory in your terminal.
3. Run the following command to build the environment and pull the AI model:
```bash
   docker-compose up --build ```

Note: On the first run, Docker will automatically download the 1.3GB llama3.2:1b model. Please allow 1-2 minutes for the Ollama container to initialize.

Open your web browser and navigate to: http://localhost:5000

To gracefully stop the application, press Ctrl+C in the terminal, or run docker-compose down.


How to Run Tests

Testing for this application is conducted manually via the UI or by executing cURL commands against the exposed REST API endpoints.

Create: Submit a lead via the left-hand panel.

Read: Refreshing the page triggers a GET request to populate the Kanban board.

Update: Drag and drop a card into a new column, or click "Undo" in the sidebar to test state mutations.

Delete: Click the red "Delete" button on any card to trigger the soft-delete logic.



What is cool about this project?

this project is cool because it combines many of the tools we have learned in CS 322 into a practical application. This is something that would be helpful in a real world setting to sales people, so I think that it's cool that I made something that could actually have utility.


What AI tool(s) did I use, and for what specific tasks?

Google Gemini (Prototyping & Code Assist): I utilized Gemini as a pair-programmer to help orchestrate the multi-container Docker architecture, resolve port-binding conflicts during the environment setup, and design the Vanilla JS asynchronous AJAX fetch loops and CSS loading states.

Ollama w/ Llama 3.2 1B (Inference Engine): I used this open-source model hosted via a local Docker container for all in-app text generation and data extraction.

Task 1 (BANT Extraction): The Flask backend sends a prompt to Ollama requesting strict JSON output.
Prompt: "Read these raw notes and extract the BANT criteria. System: You must output valid JSON matching the schema. Notes: [RAW_NOTES]"

Task 2 (Email Generation): The frontend triggers a POST request that dynamically feeds the lead's extracted data back into a strict email generation formula.

Prompt: "Write a short cold email to [NAME] at [COMPANY]. You MUST strictly follow this formula: 1. Greeting. 2. Reference their specific Need: [NEED]. 3. Insert the exact text: '[INSERT YOUR CUSTOM SOLUTION HERE]'. 4. Call to action based on their Timeline: [TIMELINE]. Do not add fluff. Output ONLY the email text."


What did I learn by applying the code / building the project?

I learned how to successfully orchestrate a multi-container environment where a Python backend must communicate synchronously with both a NoSQL database (MongoDB) and a localized AI inference server (Ollama). On the frontend, I deepened my understanding of DOM manipulation and UI/UX design patterns, specifically learning how to implement asynchronous fetch() calls that trigger dynamic glass-morphism loading states so the user understands the application is processing data rather than freezing.


What were the main technical challenges? How did I solve them?

The primary technical challenge was creating a frictionless, "wall-free" AI application. Initially, integrating commercial APIs like Anthropic's Claude or Google's Gemini created a hard barrier: anyone reviewing or grading the application would be forced to create an account, generate their own API key, and configure hidden .ini files just to use the software.

I solved this by entirely decoupling the app from cloud APIs and pivoting to a localized open-source architecture using Ollama. I updated the docker-compose.yml to spin up a dedicated AI container and configured ai_service.py to automatically pull the lightweight llama3.2:1b model upon initialization. This completely removed the API key barrier, allowing the entire AI ecosystem to run locally and securely out of the box with a single docker-compose up command.