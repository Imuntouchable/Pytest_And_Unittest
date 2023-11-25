from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    ADD_URL = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.form_data = {'title': 'title',
                         'text': 'text',
                         'slug': 'slug'}
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_author_can_create(self):
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = 1
        notes_create_count = Note.objects.count()
        self.assertEqual(notes_create_count, notes_count)
        note = Note.objects.filter(slug=self.form_data['slug']).first()
        self.assertIsNotNone(note)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_unique_slugs(self):
        self.author_client.post(self.ADD_URL, data=self.form_data)
        second = self.author_client.post(self.ADD_URL, data=self.form_data)
        self.assertFormError(
            second,
            form='form',
            field='slug',
            errors=self.form_data['slug'] + WARNING
        )

    def test_auto_slug(self):
        del self.form_data['slug']
        self.author_client.post(self.ADD_URL, data=self.form_data)
        slug = slugify(self.form_data['title'])
        created_note = Note.objects.get(slug=slug)
        self.assertEqual(created_note.slug, slug)


class TestNoteEditDelete(TestCase):

    NOTE_TEXT = 'text'
    NEW_TEXT = 'text 2'
    NOTE_TITLE = 'title'
    NEW_TITLE = 'title 2'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug='slug',
            author=cls.author,
        )
        cls.edit_note_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_note_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_note_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_note_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        self.author_client.post(
            self.edit_note_url,
            data=self.form_data
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(
            self.edit_note_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
