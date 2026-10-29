from functools import lru_cache
import logging
from typing import Final

from celery import shared_task
from django.urls import reverse
from django.core.cache import cache
from lxml.etree import Element, _Element, tostring

from . import models
from .conf import settings

logger = logging.getLogger(__name__)


class XMLBuilder:
    _TITLE_FIELDS = [
        ("Title1", "official_pre", "official_title", "prefix"),
        ("Title2", "designation_pre", "miscellaneous_title", "prefix"),
        ("Title3", "academic_pre", "academic_title", "prefix"),
        ("Title4", "official_post", "official_title", "suffix"),
        ("Title5", "academic_post", "academic_title", "suffix"),
        ("Title6", "designation_post", "miscellaneous_title", "suffix"),
    ]

    _ASSOC_KINDS = {
        "staff": ("staffOrganisationAssociation", "st"),
        "visiting": ("visitingOrganisationAssociation", "vs"),
    }

    def build_users_xml(self) -> str:
        nsmap: Final[dict[str | None, str]] = {
            None: "v1.user-sync.pure.atira.dk",
            "v3": "v3.commons.pure.atira.dk",
        }
        root = Element("users", nsmap=nsmap)
        for user in models.User.objects.all():
            root.append(self._generate_user_element(nsmap, user.person))
        return self._to_string(root)

    def build_persons_xml(self) -> str:
        nsmap: Final[dict[str | None, str]] = {
            None: "v1.unified-person-sync.pure.atira.dk",
            "v3": "v3.commons.pure.atira.dk",
        }
        root = Element("persons", nsmap=nsmap)
        for person in models.Person.objects.all():
            root.append(self._generate_person_element(nsmap, person.person, person.academic, person.pure_user))
        return self._to_string(root)

    def _generate_user_element(self, nsmap, user) -> _Element:
        element = Element("user", id=str(user.id))
        element.append(self._text_element("userName", user.username))
        element.append(self._text_element("email", user.email))
        element.append(self._name_element(nsmap, user.first_name, user.last_name))
        return element

    def _generate_person_element(self, nsmap, person, academic, pure_user) -> _Element:
        root = Element(
            "person",
            id=str(person.id),
            managedInPure="false",
        )
        root.append(self._name_element(nsmap, person.first_name, person.last_name))

        titles = self._get_titles(nsmap, person)
        if titles:
            titles_element = Element("titles")
            titles_element.extend(titles)
            root.append(titles_element)

        root.append(self._text_element("gender", "unknown"))

        if (url:= self._get_avatar(person)) and person.avatar_display_rule == "A":
            root.append(self._photo_element(url))

        orgs_element = Element("organisationAssociations")
        for association in models.PersonOrganization.objects.filter(
            person_id=person.id
        ):
            orgs_element.append(self._org_element(nsmap, association, academic))

        root.append(orgs_element)

        links_element = Element("links")
        links_element.append(self._link_element(nsmap, person.card))
        root.append(links_element)

        if pure_user:
            pure_user_element = Element("user", id=str(person.id))
            root.append(pure_user_element)

        root.append(self._text_element("visibility", "Public"))

        return root

    def _get_titles(self, nsmap, person) -> list:
        return [
            self._title_element(nsmap, pure_title_id, pure_title_name, value)
            for pure_title_id, pure_title_name, api_title_name, api_title_position in self._TITLE_FIELDS
            if (value := getattr(person, api_title_name, {}).get(api_title_position))
        ]

    def _title_element(self, nsmap, title_id, title_name, value) -> _Element:
        root = Element("title", id=title_id)
        root.append(self._text_element("typeClassification", title_name))
        value_element = Element("value")
        value_element.append(
            self._text_element(f"{{{nsmap['v3']}}}text", value, lang="en", country="GB")
        )
        root.append(value_element)

        return root

    def _get_avatar(self, person):
        if not person.avatar_private:
            return None
        path = reverse("campusonline:avatar-private", kwargs={"hash": person.hash})
        return path

    def _photo_element(self, avatar_url: str) -> _Element:
        root = Element("photos")

        photo_element = Element("personPhoto", id="Photo")
        photo_element.append(self._text_element("classification", "portrait"))

        http_element = Element("http")
        http_element.append(self._text_element("url", avatar_url))

        data_element = Element("data")
        data_element.append(http_element)

        photo_element.append(data_element)
        root.append(photo_element)

        return root

    def _org_element(self, nsmap, association, academic) -> _Element:
        is_staff = association.employee
        kind = "staff" if is_staff else "visiting"
        org_type, org_type_short = self._ASSOC_KINDS[kind]

        root = Element(
            org_type,
            id=f"{association.person_id}-{association.organization_id}-{org_type_short}",
            managedInPure="false",
        )

        org_element = Element("organisation")
        org_element.append(
            self._text_element(
                f"{{{nsmap['v3']}}}source_id", str(association.organization_id)
            )
        )

        period_element = Element("period")
        period_element.append(
            self._text_element(
                f"{{{nsmap['v3']}}}startDate",
                association.start_date.strftime("%d-%m-%Y"),
            )
        )

        root.append(org_element)
        root.append(period_element)

        if is_staff:
            root.append(
                self._text_element(
                    "staffType",
                    "academic" if academic else "nonacademic",
                )
            )

        return root

    def _link_element(self, nsmap, business_card_url) -> _Element:
        root = Element(f"{{{nsmap['v3']}}}link", id="MEDONLINE")
        root.append(self._text_element(f"{{{nsmap['v3']}}}url", business_card_url))
        root.append(self._text_element(f"{{{nsmap['v3']}}}type", "personal"))

        description_element = Element(f"{{{nsmap['v3']}}}description")
        description_element.append(
            self._text_element(
                f"{{{nsmap['v3']}}}text",
                "MEDonline Business card",
                lang="en",
                country="GB",
            )
        )
        description_element.append(
            self._text_element(
                f"{{{nsmap['v3']}}}text",
                "MEDonline Visitenkarte",
                lang="de",
                country="DE",
            )
        )

        root.append(description_element)

        return root

    def _name_element(self, nsmap, first_name, last_name) -> _Element:
        root = Element("name")
        root.append(self._text_element(f"{{{nsmap['v3']}}}firstname", first_name))
        root.append(self._text_element(f"{{{nsmap['v3']}}}lastname", last_name))
        return root

    def _text_element(self, tag, text, **attrs) -> _Element:
        root = Element(tag, **attrs)
        root.text = text
        return root

    def _to_string(self, element) -> str:
        return tostring(
            element, xml_declaration=True, encoding="UTF-8", pretty_print=True
        ).decode()


class XMLTasks:
    @shared_task(bind=True, ignore_result=True, name=f"{__name__}.generate")
    def generate(task):
        builder = XMLBuilder()

        users_xml = builder.build_users_xml()
        persons_xml = builder.build_persons_xml()

        cache.set(settings.PURE_USER_XML_CACHE_KEY, users_xml)
        cache.set(settings.PURE_PERSON_XML_CACHE_KEY, persons_xml)

        logger.info(
            "Generated XML: users=%d chars, persons=%d chars",
            len(users_xml),
            len(persons_xml),
        )
