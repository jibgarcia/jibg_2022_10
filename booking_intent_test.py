# code to test
from flight_booking_recognizer import FlightBookingRecognizer
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
from helpers.luis_helper import Intent, LuisHelper
from botbuilder.core import Recognizer
from config import DefaultConfig

import unittest # test framework

class Test_Connection(unittest.TestCase):
    def test_config(self):
        configuration = DefaultConfig()
        self.assertEqual(configuration.PORT, 3978)
        self.assertIsNot(configuration.LUIS_API_KEY, "") # checks that LUIS_API_KEY is not empty
        self.assertIsNot(configuration.APPINSIGHTS_INSTRUMENTATION_KEY, "")

class Test_Intent(unittest.TestCase):
    def test_none_intent(self):
        configuration = DefaultConfig()        
        endpoint = "https://" + configuration.LUIS_API_HOST_NAME
        runtime = CognitiveServicesCredentials(configuration.LUIS_API_KEY)
        client = LUISRuntimeClient(endpoint=endpoint, credentials=runtime)

        sample_query = "mmmbop"
        sample_result = client.prediction.resolve(configuration.LUIS_APP_ID, query=sample_query)

        self.assertEqual("None", sample_result.top_scoring_intent.intent)

class Test_Luis_Entities(unittest.TestCase):
    def test_recognizer(self):
        configuration = DefaultConfig()        
        endpoint = "https://" + configuration.LUIS_API_HOST_NAME
        runtime = CognitiveServicesCredentials(configuration.LUIS_API_KEY)
        client = LUISRuntimeClient(endpoint=endpoint, credentials=runtime)

        sample_query = "I would like to book a flight to Rome for 50€"
        sample_result = client.prediction.resolve(configuration.LUIS_APP_ID, query=sample_query)

        self.assertEqual("book", sample_result.top_scoring_intent.intent)
        self.assertEqual("budget", sample_result.entities[0].type)
        self.assertEqual("50 €", sample_result.entities[0].entity)
        self.assertEqual("dst_city", sample_result.entities[1].type)
        self.assertEqual("rome", sample_result.entities[1].entity)

if __name__ == '__main__':
    unittest.main()