# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog


class BookingDialog(CancelAndHelpDialog):
    """Flight booking implementation."""

    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(BookingDialog, self).__init__(
            dialog_id or BookingDialog.__name__, telemetry_client
        )
        self.telemetry_client = telemetry_client
        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.destination_step,
                self.origin_step,
                self.start_date_step,
                self.return_date_step,
                self.budget_step,
                self.confirm_step,
                self.final_step,
            ],
        )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(text_prompt)
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        
        self.add_dialog(
            DateResolverDialog("StartDate", self.telemetry_client)
        )
        self.add_dialog(
            DateResolverDialog("EndDate", self.telemetry_client)
        )

        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__

        self.hist_dialog = dict()

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for destination."""
        self.hist_dialog["query"] = step_context._turn_context.activity.text
        booking_details = step_context.options        

        if booking_details.dst_city is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("To what city would you like to travel?")
                ),
            )

        return await step_context.next(booking_details.dst_city)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for origin city."""
        self.hist_dialog["destination"] = step_context._turn_context.activity.text
        booking_details = step_context.options        

        # Capture the response to the previous step's prompt
        booking_details.dst_city = step_context.result
        if booking_details.or_city is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("From what city will you be travelling?")
                ),
            )

        return await step_context.next(booking_details.or_city)

    async def start_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for travel date."""

        self.hist_dialog["origin"] = step_context._turn_context.activity.text
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.or_city = step_context.result

        if not booking_details.str_date or self.is_ambiguous(
            booking_details.str_date
        ):
            return await step_context.begin_dialog(
                "StartDate", booking_details.str_date
            )

        return await step_context.next(booking_details.str_date)

    async def return_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for travel date."""

        self.hist_dialog["start_date"] = step_context._turn_context.activity.text
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.str_date = step_context.result

        if not booking_details.end_date or self.is_ambiguous(
            booking_details.end_date
        ):
            return await step_context.begin_dialog(
                "EndDate", booking_details.end_date
            )

        return await step_context.next(booking_details.end_date)

    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for budget."""
        self.hist_dialog["end_date"] = step_context._turn_context.activity.text
        booking_details = step_context.options        

        # Capture the response to the previous step's prompt
        booking_details.end_date = step_context.result
        if booking_details.budget is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("What is your budget for this booking?")
                ),
            )

        return await step_context.next(booking_details.budget)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Confirm the information the user has provided."""
        
        booking_details = step_context.options

        # Capture the results of the previous step
        self.hist_dialog["budget"] = step_context._turn_context.activity.text
        booking_details.budget = step_context.result
        
        msg = (
            f"Please confirm, I have you traveling to: { booking_details.dst_city }"
            f" from: { booking_details.or_city } on: { booking_details.str_date}"
            f" and returning on: { booking_details.end_date }. You have a budget of: { booking_details.budget}."
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg))
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction and end the dialog."""
    
        # Data for Application Insights
        self.hist_dialog["user_yes_or_no"] = step_context._turn_context.activity.text
        booking_details = step_context.options
        
        properties = {}
        properties["or_city"] = booking_details.or_city
        properties["dst_city"] = booking_details.dst_city
        properties["str_date"] = booking_details.str_date
        properties["end_date"] = booking_details.end_date
        properties["budget"] = booking_details.budget
         
        if step_context.result:
            self.telemetry_client.track_trace("BOOKING OK", properties, "INFO")
            self.telemetry_client.track_trace("CHAT_HISTORY", self.hist_dialog, "INFO")
            return await step_context.end_dialog(booking_details) 
        else: 
            else_msg = "Sorry I could not help you today."
            prompt_else_msg = MessageFactory.text(else_msg, else_msg)
            await step_context.context.send_activity(prompt_else_msg)
            self.telemetry_client.track_trace("BOOKING FAILED", properties, "ERROR")
            self.telemetry_client.track_trace("CHAT_HISTORY", self.hist_dialog, "ERROR")

        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types