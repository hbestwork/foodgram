from rest_framework.fields import CharField
from rest_framework.relations import ManyRelatedField, PrimaryKeyRelatedField

PAGE_SIZE = 6
PAGE_SIZE_QUERY_PARAM = 'limit'

EMPTY_LIST_ERROR = ManyRelatedField.default_error_messages['empty']
BLANK_FIELD_ERROR = CharField.default_error_messages['blank']
NON_POSITIVE_ERROR = 'Это значение должно быть положительным.'
REPEATING_VALUES_ERROR = 'Элементы не должны повторяться.'
PK_NOT_FOUND = PrimaryKeyRelatedField.default_error_messages['does_not_exist']
SELF_SUBSCRIPTION_ERROR = 'Нельзя подписаться на самого себя.'
ALREADY_SUBSCRIBED_ERROR = 'Уже подписан.'
NOT_SUBSCRIBED_ERROR = 'Еще не подписан.'
ALREADY_EXISTS_ERROR = 'Уже добавлен.'
NOT_EXISTS_ERROR = 'Еще не добавлен.'
