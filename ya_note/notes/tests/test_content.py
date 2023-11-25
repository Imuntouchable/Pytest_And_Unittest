from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Просто текст.',
            author=cls.author,
            slug='slug'
        )

    def test_note_in_list(self):
        response = self.author_client.get(self.LIST_URL)
        object_list = self.note in response.context['object_list']
        self.assertEqual(object_list, True)

    def test_note_of_author(self):
        user_notelist = (
            (self.author, True),
            (self.reader, False),
        )
        for user, notelist in user_notelist:
            self.client.force_login(user)
            response = self.client.get(self.LIST_URL)
            object_list = self.note in response.context['object_list']
            self.assertEqual(object_list, notelist)

    def test_for_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for page, args in urls:
            with self.subTest(page=page):
                url = reverse(page, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
