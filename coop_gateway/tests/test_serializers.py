from unittest import TestCase

from shortuuid import uuid
from mock import MagicMock

from coop_local.models import (
    Contact,
    Engagement,
    LegalStatus,
    Organization,
    Person,
    Role,
    TransverseTheme,
)

from coop_gateway.serializers import (
    serialize_organization,
    serialize_person,
)
from .mock_test_case import MockTestCase


class SeralizeTestCase(MockTestCase):
    def setUp(self):
        self.requests_mock = self.patch('coop_gateway.signals.requests')
        self.settings_mock = self.patch('coop_gateway.signals.settings')

        self.settings_mock.PES_HOST = 'http://localhost'
        self.settings_mock.PES_API_KEY = uuid()

    def create_contact(self, content_object, **kwargs):
        kwargs['content_object'] = content_object

        if 'content' not in kwargs:
            kwargs['content'] = uuid()

        contact = Contact(**kwargs)
        contact.save()
        return contact

    def create_person(self):
        person = Person(first_name=uuid(),
                        last_name=uuid())
        person.save()
        return person


class TestSeralizeOrganization(SeralizeTestCase, TestCase):

    def create_organization(self, **kwargs):

        if 'title' not in kwargs:
            kwargs['title'] = uuid()

        organization = Organization(**kwargs)
        organization.save()
        return organization

    def create_transverse_theme(self):
        theme = TransverseTheme(name=uuid())
        theme.save()
        return theme

    def create_legal_status(self):
        legal_status = LegalStatus(label=uuid())
        legal_status.save()
        return legal_status

    def create_role(self):
        role = Role(label=uuid())
        role.save()
        return role

    def create_engagement(self, organization, person, role):
        engagement = Engagement(organization=organization,
                                person=person,
                                role=role)
        engagement.save()
        return engagement

    def tests_uuid_is_always_present(self):
        organization = self.create_organization()

        result = serialize_organization(organization, [])

        self.assertEquals(result['uuid'], organization.uuid)

    def tests_included_fields_are_serialized(self):
        organization = self.create_organization()

        result = serialize_organization(organization, ['title'])

        self.assertEquals(result['title'], organization.title)

    def tests_organization_contacts_serialization(self):
        organization = self.create_organization()
        contact = self.create_contact(organization)

        result = serialize_organization(organization, ['contacts'])

        self.assertEquals(result['contacts'], [
            {
                'uuid': contact.uuid,
                'content': contact.content,
            }
        ])

    def tests_pref_phone_is_referenced_by_uuid(self):
        organization = self.create_organization()
        contact = self.create_contact(organization)
        organization.pref_phone = contact
        organization.save()

        result = serialize_organization(organization, ['pref_phone'])

        self.assertEquals(result['pref_phone'], contact.uuid)

    def tests_pref_email_is_referenced_by_uuid(self):
        organization = self.create_organization()
        contact = self.create_contact(organization)
        organization.pref_email = contact
        organization.save()

        result = serialize_organization(organization, ['pref_email'])

        self.assertEquals(result['pref_email'], contact.uuid)

    def tests_transverse_themes_are_serialized_as_a_list_of_id(self):
        organization = self.create_organization()
        theme = self.create_transverse_theme()
        organization.transverse_themes.add(theme)
        organization.save()

        result = serialize_organization(organization, ['transverse_themes'])

        self.assertEquals(result['transverse_themes'], [theme.pk])

    def tests_pref_legal_status_is_referenced_by_slug(self):
        legal_status = self.create_legal_status()
        organization = self.create_organization(legal_status=legal_status)

        result = serialize_organization(organization, ['legal_status'])

        self.assertEquals(result['legal_status'], legal_status.slug)

    def test_members_are_serialized(self):
        organization = self.create_organization()
        person = self.create_person()
        role = self.create_role()
        pes_role = {
            'slug': role.slug,
            'uuid': uuid()
        }
        self.create_engagement(organization, person, role)

        requests_mock = self.patch('coop_gateway.serializers.requests')
        response_mock = MagicMock()
        requests_mock.get.return_value = response_mock
        response_mock.json.return_value = [pes_role]

        result = serialize_organization(organization, ['members'])

        self.assertEquals(result['members'], [{
            'person': person.uuid,
            'role': pes_role['uuid']
        }])


class TestSeralizePerson(SeralizeTestCase, TestCase):

    def tests_defaults(self):
        person = self.create_person()
        pref_email = self.create_contact(person)
        person.pref_email = pref_email
        person.save()

        result = serialize_person(person)

        self.assertEquals(result, {
            'uuid': person.uuid,
            'first_name': person.first_name,
            'last_name': person.last_name,
            'pref_email': pref_email.uuid,
            'contacts': [{
                'uuid': pref_email.uuid,
                'content': pref_email.content,
            }],
        })
