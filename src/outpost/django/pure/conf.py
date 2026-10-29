from appconf import AppConf
from django.conf import settings


class PureAppConf(AppConf):
    USER_XML_CACHE_KEY = "user"
    PERSON_XML_CACHE_KEY = "person"

    class Meta:
        prefix = "PURE"
