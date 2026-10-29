from django.core.cache import cache
from django.http import HttpResponse
from outpost.django.api.authentication import BearerTokenAuthentication
from outpost.django.api.permissions import ExtendedDjangoModelPermissions
from rest_framework.views import APIView
from rest_framework_xml.renderers import XMLRenderer

from .conf import settings
from .models import User, Person
from .tasks import XMLBuilder, XMLTasks


class UserView(APIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [ExtendedDjangoModelPermissions]
    queryset = User.objects.all()
    renderer_classes = [XMLRenderer]

    def get(self, request):
        response = HttpResponse()
        response["Content-Type"] = "application/xml"
        xml = cache.get(settings.PURE_USER_XML_CACHE_KEY, None)
        if not xml:
            xml = XMLBuilder().build_users_xml()
        response.write(xml)
        return response


class PersonView(APIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [ExtendedDjangoModelPermissions]
    queryset = Person.objects.all()
    renderer_classes = [XMLRenderer]

    def get(self, request):
        response = HttpResponse()
        response["Content-Type"] = "application/xml"
        xml = cache.get(settings.PURE_PERSON_XML_CACHE_KEY, None)
        if not xml:
            xml = XMLBuilder().build_persons_xml()
        response.write(xml)
        return response
