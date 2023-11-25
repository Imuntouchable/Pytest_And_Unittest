from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'page, args',
    (('news:home', None),
     ('users:login', None),
     ('users:logout', None),
     ('users:signup', None),
     ('news:detail', pytest.lazy_fixture('news_pk')),),
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous(client, page, args):
    url = reverse(page, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'page, args',
    (('news:edit', pytest.lazy_fixture('comment_pk')),
     ('news:delete', pytest.lazy_fixture('comment_pk')),),
)
def test_pages_availability_for_auth(author_client, page, args):
    url = reverse(page, args=args)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'page, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_pk')),
        ('news:delete', pytest.lazy_fixture('comment_pk')),
    ),
)
def test_pages_availability_for_edit_delete_anonymous(
    client,
    page,
    args
):
    url = reverse(page, args=args)
    response = client.get(url)
    page_rez = reverse('users:login')
    rez = f'{page_rez}?next={url}'
    assertRedirects(response, rez)


@pytest.mark.parametrize(
    'page',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
    page,
    comment_pk,
    admin_client,
    author_client
):
    url = reverse(page, args=comment_pk)
    response_first = admin_client.get(url)
    response_second = author_client.get(url)
    assert ((response_first.status_code == HTTPStatus.NOT_FOUND)
            and (response_second.status_code == HTTPStatus.OK)
            )
