from datetime import timedelta

import pytest
from django.conf import settings
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def count_comments_initially():
    return Comment.objects.count()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='title',
        text='text',
    )


@pytest.fixture
def news_pk(news):
    return news.pk,


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='text'
    )


@pytest.fixture
def comment_pk(comment):
    return comment.pk,


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст комментария'
    }


@pytest.fixture
def bulk_news():
    now = timezone.now()
    News.objects.bulk_create(
        News(title=f'News {index}',
             text='News text',
             date=now - timedelta(days=index)
             )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def bulk_comments(news, author):
    now = timezone.now()
    for index in range(11):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Text {index}'
        )
        comment.created = now - timedelta(days=index)
        comment.save()
