import logging

from django.contrib.gis.db import models
from django.contrib.postgres.fields import (
    ArrayField,
    HStoreField,
)

from .conf import settings

logger = logging.getLogger(__name__)


class User(models.Model):
    """
    ## Fields

    ### `id` (`integer`)
    Primary key and foreign key to [MEDonline person](../../campusonline/person) this assignment refers to.

    """

    person = models.OneToOneField(
        "campusonline.Person",
        models.DO_NOTHING,
        db_constraint=False,
        primary_key=True,
        db_column="id",
    )

    class Meta:
        managed = False
        db_table = "pure_user"

    class Refresh:
        interval = 21600

    def __str__(self):
        return f"{self.person.last_name}, {self.person.first_name}"


class Person(models.Model):
    """
    ## Fields

    ### `id` (`integer`)
    Primary key and foreign key to [MEDonline person](../../campusonline/person) this assignment refers to.

    ### `academic` (`boolean`)
    Whether the person holds an academic position.

    ### `pure_user` (`boolean`)
    Whether the person has an active PURE user account.

    """

    person = models.OneToOneField(
        "campusonline.Person",
        models.DO_NOTHING,
        db_constraint=False,
        primary_key=True,
        db_column="id",
    )
    academic = models.BooleanField()
    pure_user = models.BooleanField()

    class Meta:
        managed = False
        db_table = "pure_person"

    class Refresh:
        interval = 21600

    def __str__(self):
        return f"{self.person.last_name}, {self.person.first_name}"


class PersonOrganization(models.Model):
    """
    ## Fields

    ### `id` (`integer`)
    Primary key.

    ### `person_id` (`integer`)
    Foreign key to [MEDonline person](../../campusonline/person) this assignment belongs to.

    ### `organization_id` (`integer`)
    Foreign key to [MEDonline organization](../../campusonline/organization) this assignment refers to.

    ### `start_date` (`datetime`)
    Start date of the person's assignment to the organization.

    ### `employee` (`boolean`)
    Whether this is a employee position:

    """

    id = models.IntegerField(primary_key=True, serialize=False)
    person = models.ForeignKey(
        "campusonline.Person",
        models.DO_NOTHING,
        db_constraint=False,
        null=True,
        blank=True,
    )
    organization = models.ForeignKey(
        "campusonline.Organization",
        models.DO_NOTHING,
        db_constraint=False,
        null=True,
        blank=True,
    )
    start_date = models.DateTimeField()
    employee = models.BooleanField()

    class Meta:
        managed = False
        db_table = "pure_person_organization"

    class Refresh:
        interval = 21600

    def __str__(self):
        return str(self.id)
