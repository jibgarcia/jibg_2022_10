# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from booking_details import BookingDetails

class Intent(Enum):
    BOOK_FLIGHT = "book"
    CANCEL = "Cancel"
    GET_WEATHER = "GetWeather"
    NONE_INTENT = "none"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )

            if intent == Intent.BOOK_FLIGHT.value:
                result = BookingDetails()

                # We need to get the result from the LUIS JSON which at every level returns an array.
                to_entities = recognizer_result.entities.get("$instance", {}).get(
                    "dst_city", []
                )
                if len(to_entities) > 0:
                    if recognizer_result.entities.get("dst_city", [{"$instance": {}}])[0]:
                        result.dst_city = to_entities[0]["text"].capitalize()

                from_entities = recognizer_result.entities.get("$instance", {}).get(
                    "or_city", []
                )
                if len(from_entities) > 0:
                    if recognizer_result.entities.get("or_city", [{"$instance": {}}])[0]:
                        result.or_city = from_entities[0]["text"].capitalize()

                bud_entities = recognizer_result.entities.get("$instance", {}).get(
                    "budget", []
                )
                if len(bud_entities) > 0:
                    if recognizer_result.entities.get("budget", [{"$instance": {}}])[0]:
                        result.budget = bud_entities[0]["text"]

                str_date_entities = recognizer_result.entities.get("$instance", {}).get(
                    "str_date", [])
                if len(str_date_entities) > 0:
                    if recognizer_result.entities.get("str_date", [{"$instance": {}}])[0]:
                        result.str_date = str_date_entities[0]["text"]
                
                end_date_entities = recognizer_result.entities.get("$instance", {}).get(
                    "end_date", [])
                if len(end_date_entities) > 0:
                    if recognizer_result.entities.get("end_date", [{"$instance": {}}])[0]:
                        result.end_date = end_date_entities[0]["text"]

        except Exception as exception:
            print(exception)

        return intent, result
