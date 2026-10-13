<p align="center">
  <img src="https://www.gstatic.com/bricks/image/bb64055b-9705-4bfa-a040-d75046a6f36c.gif" width="300" height="225" alt="Built at Build with Gemini HYD">
</p>

# Hyderabad Food Trail Guide

An AI-powered culinary guide built with the Google Agent Development Kit (ADK) and Gemini 3.8 Flash, specialized in exploring the authentic food culture of Hyderabad across legendary neighborhoods like Old City, Banjara Hills, Gachibowli, and Ameerpet.

![Agent Demo](demo.gif)

---

## What the Agent Does

The agent provides personalized food recommendations, plans neighborhood food trails, manages personal favorites, and generates dish photography on demand:

- **Explore & Filter Food Spots (`search_food_spots`)**:
  - Searches a curated Firestore database of legendary Hyderabad eateries (`hyderabad_food_spots`).
  - Supports filtering by neighborhood (`Old City`, `Banjara Hills`, `Gachibowli`, `Ameerpet`), dietary preference (`veg` / `non-veg`), and free-text queries (e.g. `biryani`, `haleem`, `dosa`, `chai`).
  - Returns detailed spot info including signature dishes, price range, timings, and descriptions.

- **Cross-Session Long-Term Memory (Vertex AI Memory Bank)**:
  - Powered by `PreloadMemoryTool` and post-turn memory extraction callbacks.
  - Automatically remembers user tastes, dietary constraints (veg vs. non-veg), spice level preferences, budget range, and preferred neighborhoods across distinct sessions.
  - Automatically injects durable facts into future interactions to deliver deeply personalized culinary advice.

- **Save & Retrieve Favorites (`save_favorite_spot`, `list_favorite_spots`)**:
  - Lets users bookmark favorite food spots with custom notes directly into Firestore (`user_favorites`).
  - Retrieves saved spots across sessions with details and timestamps.

- **AI Dish Photography & Cloud Storage Upload (`generate_dish_image`)**:
  - Generates food visuals of authentic Hyderabadi dishes using `gemini-3.1-flash-lite-image` on Vertex AI (`global` location).
  - Saves the generated image as a session artifact in the agent runtime.
  - Uploads the image bytes to a public Google Cloud Storage bucket (`hyderabad-food-trail-274537b5`) and returns a permanent public HTTPS URL.

- **Food Trail Planning**:
  - Synthesizes 2-3 stop mini culinary trails in specific neighborhoods (e.g., morning Irani chai and Osmania biscuits, afternoon dum biryani, and evening dessert).

- **Web Chat UI & FastAPI Proxy (Cloud Run Frontend)**:
  - Lightweight web frontend and FastAPI proxy deployed to Cloud Run (`frontend/`).
  - Directly bridges client chat interactions with the deployed agent on Agent Runtime using the A2A protocol.

---

## Project Structure

```
hyderabad-food-trail/
├── app/
│   ├── agent.py               # Root agent, Gemini 3.8 Flash, PreloadMemoryTool & memory callbacks
│   ├── tools.py               # Firestore database tools & Vertex AI image generation tool
│   ├── fast_api_app.py        # FastAPI server integration with Memory Bank service
│   └── app_utils/             # ADK application utilities, services & A2A routing
├── frontend/
│   ├── main.py                # FastAPI proxy communicating over A2A protocol
│   ├── static/index.html      # Responsive web chat UI
│   ├── Dockerfile             # Container configuration for Cloud Run
│   └── requirements.txt       # Frontend dependencies
├── agents-cli-manifest.yaml   # Agent manifest configuration (ACLI 1.4.0, A2A enabled)
├── pyproject.toml             # Python project dependencies
├── demo.gif                   # Looping recording of the agent in action
└── README.md                  # Project documentation
```

---

## Wired Tools & Backend Architecture

| Component / Tool | Backend / Model | Purpose |
|---|---|---|
| `search_food_spots` | Google Cloud Firestore (`hyderabad_food_spots`) | Query restaurants by area, dietary preference, or keyword |
| `PreloadMemoryTool` | Vertex AI Memory Bank (Agent Engine) | Recall user preferences and dietary choices across sessions |
| `save_favorite_spot` | Google Cloud Firestore (`user_favorites`) | Bookmark a spot with personal notes |
| `list_favorite_spots` | Google Cloud Firestore (`user_favorites`) | Retrieve all bookmarked spots |
| `generate_dish_image` | Vertex AI (`gemini-3.1-flash-lite-image`) & Google Cloud Storage | Generate dish photography, store session artifact, and upload to public GCS |
| Web Frontend | FastAPI Proxy on Cloud Run | Serves chat interface communicating with Agent Runtime via A2A |

---

## Agent Configuration

- **Model**: `gemini-3.8-flash`
- **Orchestration**: Google ADK ReAct loop (`root_agent`)
- **Memory Service**: `VertexAiMemoryBankService` (Agent Engine `9112801849030737920`, `us-east1`)
- **Protocol**: A2A (Agent-to-Agent) compatible
- **Image Model**: `gemini-3.1-flash-lite-image` via Google GenAI SDK (Vertex AI)
- **Deployment**: Agent Runtime (`us-east1`) & Cloud Run Frontend
