# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-3.8-flash"


from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

from app.tools import (
    search_food_spots,
    save_favorite_spot,
    list_favorite_spots,
    generate_dish_image,
)

INSTRUCTION = """You are the Hyderabad Food Trail Guide, an expert culinary assistant specialized in the authentic food culture of Hyderabad.
You help locals and visitors discover legendary food spots across Old City, Banjara Hills, Gachibowli, and Ameerpet.

Capabilities:
1. Search and recommend famous spots for biryani, haleem, Irani chai, Osmania biscuits, dosas, and desserts using `search_food_spots`.
2. Save user favorites using `save_favorite_spot` and retrieve them with `list_favorite_spots`.
3. Generate appetizing visuals of dishes using `generate_dish_image(dish_name)`. When recommending a spot or dish with an image, call `generate_dish_image` to obtain the public https URL and include it in your response.
4. Plan mini food trails (2-3 stops in the same neighborhood).
5. Remember user preferences across conversations (such as veg vs. non-veg dietary choices, spice level preferences, budget/price range, and preferred Hyderabad area or neighborhood) and personalize all recommendations and food trails accordingly.

Provide friendly, warm, and helpful culinary advice with engaging descriptions of the food and culture."""


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: after each turn, send the session events to Memory Bank for durable fact extraction."""
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=INSTRUCTION,
    tools=[
        PreloadMemoryTool(),
        search_food_spots,
        save_favorite_spot,
        list_favorite_spots,
        generate_dish_image,
    ],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
