from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news_pk, form_data):
    url = reverse('news:detail', args=news_pk)
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
        author_client,
        news_pk,
        form_data,
        news,
        author
):
    url = reverse('news:detail', args=news_pk)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.latest('news')
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news_pk):
    url = reverse('news:detail', args=news_pk)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, comment_pk, news_pk):
    news_url = reverse('news:detail', args=news_pk)
    url_to_comments = news_url + '#comments'
    delete_url = reverse('news:delete', args=comment_pk)
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        admin_client,
        comment_pk,
        news_pk
):
    url = reverse('news:delete', args=comment_pk)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client,
        comment_pk,
        form_data,
        news_pk,
        comment
):
    edit_url = reverse('news:edit', args=comment_pk)
    response = author_client.post(edit_url, data=form_data)
    url_to_comments = reverse('news:detail', args=news_pk) + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        admin_client,
        comment_pk,
        form_data,
        comment
):
    edit_url = reverse('news:edit', args=comment_pk)
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']
