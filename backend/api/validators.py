from rest_framework.serializers import ValidationError

from api.constants import (
    EMPTY_LIST_ERROR,
    BLANK_FIELD_ERROR,
    NON_POSITIVE_ERROR,
    REPEATING_VALUES_ERROR,
    SELF_SUBSCRIPTION_ERROR,
    ALREADY_SUBSCRIBED_ERROR,
    NOT_SUBSCRIBED_ERROR,
    ALREADY_EXISTS_ERROR,
    NOT_EXISTS_ERROR,
)


def positive_number_validator(value):
    if value <= 0:
        raise ValidationError(NON_POSITIVE_ERROR)


def non_empty_list_validator(value):
    if not value:
        raise ValidationError(EMPTY_LIST_ERROR)


def non_blank_validator(value):
    if not value:
        raise ValidationError(BLANK_FIELD_ERROR)


def non_repeating_validator(iterable1, iterable2):
    if len(iterable1) != len(iterable2):
        raise ValidationError(REPEATING_VALUES_ERROR)


def self_subscribe_validator(author, follower):
    if follower == author:
        raise ValidationError(SELF_SUBSCRIPTION_ERROR)


def no_subscription_validator(subscription):
    if subscription:
        raise ValidationError(ALREADY_SUBSCRIBED_ERROR)


def need_subscription_validator(subscription):
    if not subscription:
        raise ValidationError(NOT_SUBSCRIBED_ERROR)


def no_relation_validator(obj):
    if obj:
        raise ValidationError(ALREADY_EXISTS_ERROR)


def need_relation_validator(obj):
    if not obj:
        raise ValidationError(NOT_EXISTS_ERROR)
