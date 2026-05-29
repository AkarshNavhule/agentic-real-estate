import sqlite3
import os
from semantic_kernel.functions import kernel_function
from typing import Annotated

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "crm.db")


class PropertyManagementPlugin:
    """
    A Semantic Kernel Plugin that exposes internal CRM data to the AI Agent.
    This acts as our local tool/MCP integration.
    """

    @kernel_function(
        name="check_tour_availability",
        description="Checks the internal SQLite CRM database for available open house tour dates and the assigned real estate agent for a specific property."
    )
    def check_tour_availability(
            self,
            property_id: Annotated[str, "The numeric ID of the property (e.g., '1', '2', or '3')"]
    ) -> str:

        print(f"--> [AGENT TOOL TRIGGERED] AI is checking SQLite for Property ID: {property_id}")

        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT available_dates, agent_name FROM tours WHERE property_id=?", (property_id,))
            result = c.fetchone()
            conn.close()

            if result:
                return f"Tours available: {result[0]}. Assigned Agent: {result[1]}."
            return "No tour information found for this property ID in the CRM."

        except Exception as e:
            return f"Database error: {str(e)}"