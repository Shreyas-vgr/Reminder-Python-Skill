# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the
# Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on
# implementing slots, dialog management, session persistence, api calls,
# and more.
# This sample is built using the handler classes approach in skill builder.

import logging
import pytz
import datetime

from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.services import ServiceException
from ask_sdk_model.services.reminder_management import (Trigger, TriggerType,
                                                        AlertInfo, SpokenInfo,
                                                        SpokenText,
                                                        PushNotification,
                                                        PushNotificationStatus,
                                                        ReminderRequest)
from ask_sdk_model.ui import AskForPermissionsConsentCard

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

REQUIRED_PERMISSIONS = ["alexa::alerts:reminders:skill:readwrite"]
TIME_ZONE_ID = 'America/Los_Angeles'


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = ("Welcome to the reminder skill, "
                        "try saying notify me to set a one minute reminder?")

        return (handler_input.response_builder.speak(speak_output).ask(
            speak_output).response)


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello Python World from Classes!"

        return (handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open
                # for the user to respond")
                .response)


class ReminderIntentHandler(AbstractRequestHandler):
    """Handler for Reminder Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ReminderIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        request_envelope = handler_input.request_envelope
        permissions = request_envelope.context.system.user.permissions
        reminder_service = handler_input.service_client_factory.get_reminder_management_service()

        if not (permissions and permissions.consent_token):
            return (handler_input.response_builder
                    .speak("Please give permissions to set reminders "
                           "using the alexa app.")
                    .set_card(AskForPermissionsConsentCard(permissions=REQUIRED_PERMISSIONS))
                    .response)

        now = datetime.datetime.now(pytz.timezone(TIME_ZONE_ID))
        one_min_from_now = now + datetime.timedelta(minutes=+1)
        notification_time = one_min_from_now.strftime("%Y-%m-%dT%H:%M:%S")

        trigger = Trigger(TriggerType.SCHEDULED_ABSOLUTE, notification_time,
                          time_zone_id=TIME_ZONE_ID)
        text = SpokenText(locale='en-US',
                          ssml='<speak>This is your reminder</speak>',
                          text='This is your reminder')
        alert_info = AlertInfo(SpokenInfo([text]))
        push_notification = PushNotification(PushNotificationStatus.ENABLED)
        reminder_request = ReminderRequest(notification_time, trigger,
                                           alert_info, push_notification)

        try:
            reminder_response = reminder_service.create_reminder(
                reminder_request)
        except ServiceException as error:
            logger.error(error)
            raise error

        return (
            handler_input.response_builder.speak("Reminder Created").response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (handler_input.response_builder.speak(speak_output).ask(
            speak_output).response)


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(
            handler_input) or ask_utils.is_intent_name("AMAZON.StopIntent")(
            handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
            )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session
                # open for the user to respond")
                .response)


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors.
    If you receive an error stating the request handler chain is not found,
    you have not implemented a handler for the intent being invoked or
    included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = ("Sorry, I had trouble doing what you asked. "
                        "Please try again.")

        return (handler_input.response_builder.speak(speak_output).ask(
            speak_output).response)


# The SkillBuilder object acts as the entry point for your skill,
# routing all request and response payloads to the handlers above.
# Make sure any new handlers or interceptors you've defined are included below.
# The order matters - they're processed top to bottom.

sb = CustomSkillBuilder(api_client=DefaultApiClient())

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(ReminderIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(
    IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()
