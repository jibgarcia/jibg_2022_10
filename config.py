#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 8000 #3978
    # APP_ID = os.environ.get("MicrosoftAppId", "")
    # APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_TYPE = os.environ.get("MicrosoftAppType", "MultiTenant") 
    APP_ID = os.environ.get("MicrosoftAppId", "fc0dc04e-60b2-4984-a6e1-f21731ca592c")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "9nG8Q~NlUDfQXd8IDvZjxIr3ngNCdLeluD2GCcY9")
    LUIS_APP_ID = os.environ.get("LuisAppId", "1f6d13d5-e766-4367-a3c6-a6a2a789789b")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "76b1d1cfec80489680b4a804ac7c662c")
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "westeurope.api.cognitive.microsoft.com")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        # "AppInsightsInstrumentationKey", "InstrumentationKey=5d1c1614-4149-432f-ba86-cb5dffd14d89;IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/"
        "AppInsightsInstrumentationKey", "5d1c1614-4149-432f-ba86-cb5dffd14d89"
    )
