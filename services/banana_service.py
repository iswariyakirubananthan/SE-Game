"""
services/banana_service.py - Banana Game API Interoperability Service
====================================================================
Demonstrates:
  - Theme B: Interoperability
    * Communicating with an external University of Bedfordshire REST service
    * HTTP GET requests with custom User-Agent and timeouts
    * Parsing dynamic JSON payloads
    * Resilient error handling and fallback mechanism for network resilience

API Endpoint: http://marcconrad.com/uob/banana/api.php?out=json
Observed JSON Response structure:
  {
    "question": "https://www.sanfoh.com/uob/banana/data/tb....png",
    "solution": 8
  }
"""

import requests
import logging
import random

# Configure logger for interoperability debugging
logger = logging.getLogger(__name__)

BANANA_API_URL = "http://marcconrad.com/uob/banana/api.php?out=json"
REQUEST_TIMEOUT = 6  # seconds

# Curated fallback puzzles from the same Banana API dataset
# Ensures graceful degradation if the external university server experiences downtime
FALLBACK_PUZZLES = [
    {
        "question": "https://www.sanfoh.com/uob/banana/data/tb0b0edafeccba6a9ac5d8ddc0cn111.png",
        "solution": 1
    },
    {
        "question": "https://www.sanfoh.com/uob/banana/data/tb30cadfb0ee69c03a41351a651n88.png",
        "solution": 8
    },
    {
        "question": "https://www.sanfoh.com/uob/banana/data/tb45b20bbcf237b6c5df96ef5c3n44.png",
        "solution": 4
    },
    {
        "question": "https://www.sanfoh.com/uob/banana/data/tb5d00b1712aeb780cd56930261n66.png",
        "solution": 6
    },
    {
        "question": "https://www.sanfoh.com/uob/banana/data/tb615c85b5d8a9018e69eeef1f9n33.png",
        "solution": 3
    }
]


class BananaApiService:
    """
    Encapsulates all external communications with the University of Bedfordshire
    Banana Puzzle API.
    """

    @classmethod
    def fetch_puzzle(cls):
        """
        Retrieves a puzzle from the external API.
        
        Returns:
            dict: {
                "question": str (image URL),
                "solution": int (target answer),
                "is_fallback": bool
            }
        Raises:
            Exception if both live API and fallback are unreachable.
        """
        headers = {
            "User-Agent": "BananaQuest-GameEngine/1.0 (University of Bedfordshire Assignment Client)"
        }

        try:
            # Theme B: Interoperability - Sending HTTP GET request to external server
            response = requests.get(BANANA_API_URL, headers=headers, timeout=REQUEST_TIMEOUT)

            # Check HTTP Status Code
            if response.status_code == 200:
                data = response.json()

                # Validate expected JSON fields
                if "question" in data and "solution" in data:
                    question_url = str(data["question"]).strip()
                    solution_val = int(data["solution"])

                    return {
                        "question": question_url,
                        "solution": solution_val,
                        "is_fallback": False
                    }
                else:
                    logger.warning("Banana API returned unexpected JSON keys: %s", data)
            else:
                logger.warning("Banana API responded with non-200 status: %d", response.status_code)

        except requests.exceptions.RequestException as exc:
            # Handles timeouts, DNS lookup failures, connection drops
            logger.error("Interoperability error communicating with Banana API: %s", str(exc))

        # Graceful Fallback: Ensure uninterrupted user experience
        logger.info("Engaging offline fallback puzzle to maintain gameplay integrity.")
        fallback_item = random.choice(FALLBACK_PUZZLES)
        return {
            "question": fallback_item["question"],
            "solution": fallback_item["solution"],
            "is_fallback": True
        }
