from __future__ import annotations
import json
import asyncio
import logging
from typing import Optional, Dict, Any

from app.config import GEMINI_API_KEY, GEMINI_MODEL, COPILOT_TIMEOUT, APP_SIMULATION_DATE

# Configure structured logging
logger = logging.getLogger(__name__)

# --- 1. THE SYSTEM PROMPT DEFINITION ---
BASE_SYSTEM_PROMPT = f"""
You are the "PaintFlow Supply Chain Copilot", an expert logistics AI assistant.
Your goal is to help warehouse managers optimize inventory, predict risks, and handle disruptions.

CURRENT SYSTEM TIME: {APP_SIMULATION_DATE}

GUIDELINES:
1. **Be Action-Oriented:** Don't just report data; suggest transfers or reordering.
2. **Roleplay the Scenario:** If a "Truck Strike" is active, acknowledge delays.
3. **Structured Data:** You MUST return responses in the specified JSON format.
4. **Data Fidelity:** Never hallucinate inventory numbers. Use ONLY the provided context.

OUTPUT FORMAT (JSON ONLY):
{{
  "text": "Your helpful, natural language response here.",
  "ui_widget": {{
      "type": "TRANSFER_CARD" | "INSIGHT_CARD" | null,
      "props": {{ ... }}
  }}
}}
"""

async def get_chat_response(message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Orchestrator function: Decides whether to use Real AI or Heuristic Fallback.
    """
    context = context or {}
    scenario_id = context.get("scenario_id", "NORMAL")

    if not GEMINI_API_KEY:
        logger.info("Gemini is not configured; using the local copilot response.")
        return _heuristic_response(message, scenario_id, context)

    try:
        # Run Gemini logic with a timeout safety net
        return await asyncio.wait_for(
            _call_gemini_api(message, context, scenario_id),
            timeout=COPILOT_TIMEOUT
        )
    except (asyncio.TimeoutError, Exception) as e:
        logger.exception("Gemini API error; using the local copilot response.")
        return _heuristic_response(message, scenario_id, context)


ALLOWED_WIDGET_TYPES = {"TRANSFER_CARD", "INSIGHT_CARD"}


def _sanitize_widget(widget: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(widget, dict):
        return None
    widget_type = widget.get("type")
    if widget_type not in ALLOWED_WIDGET_TYPES:
        return None
    raw_props = widget.get("props")
    if not isinstance(raw_props, dict):
        return {"type": widget_type, "props": {}}

    sanitized_props = {}
    for k, v in raw_props.items():
        if isinstance(k, str) and len(k) <= 50:
            if isinstance(v, (str, int, float, bool)):
                sanitized_props[str(k)] = v
            elif isinstance(v, list):
                sanitized_props[str(k)] = [
                    str(item) for item in v[:20] if isinstance(item, (str, int, float, bool))
                ]
    return {"type": widget_type, "props": sanitized_props}


async def _call_gemini_api(user_message: str, context: Dict[str, Any], scenario_id: str) -> Dict[str, Any]:
    """
    Constructs the prompt and calls Google Gemini asynchronously in worker thread.
    """
    def _generate():
        # google-generativeai was retired by Google.  Import lazily so the
        # application can still start in local/offline mode before optional AI
        # dependencies are installed.
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)
        return client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.4,
                system_instruction=f"""
                {BASE_SYSTEM_PROMPT}

                CURRENT SIMULATION SCENARIO: {scenario_id}

                REAL-TIME INVENTORY SNAPSHOT:
                {context.get("inventory_snapshot", "No current inventory data available.")}
                """,
            ),
        )

    response = await asyncio.to_thread(_generate)

    # --- PARSE AND VALIDATE RESPONSE ---
    try:
        data = json.loads(response.text or "{}")
        text = data.get("text", "")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Gemini response did not include text")
        widget = _sanitize_widget(data.get("ui_widget"))
        return {"text": text.strip(), "ui_widget": widget}
    except Exception:
        return {
            "text": getattr(response, "text", "Analysis complete."),
            "ui_widget": None
        }



def _heuristic_response(
    message: str,
    scenario_id: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Fallback logic (Kept strictly as backup).
    """
    msg = message.lower()
    prefix = f"(Local analysis - {scenario_id}) "
    snapshot = (context or {}).get("inventory_snapshot", "")

    if "bridal" in msg or "pune" in msg:
        return {
            "text": prefix + "Critical shortage of Bridal Red in Pune detected. 20 units left. Recommend transfer from Mumbai.",
            "ui_widget": {"type": "TRANSFER_CARD", "props": {"from": "Mumbai", "to": "Pune", "sku": "Bridal Red", "qty": 500, "eta": "2 days", "savings": "₹15,000"}}
        }
    
    detail = snapshot if snapshot else "No live inventory alerts are available yet."
    return {
        "text": prefix + f"Here is the current inventory assessment: {detail} Ask about a city, stockouts, or a specific shade for a targeted recommendation.",
        "ui_widget": None
    }
