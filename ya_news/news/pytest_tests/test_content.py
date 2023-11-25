import pytest
from django.conf import settings
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('bulk_news')
def test_news_count(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    comments_count = len(object_list)
    assert comments_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('bulk_news')
def test_news_order(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('bulk_comments')
def test_comments_order(client, news_pk):
    url = reverse('news:detail', args=news_pk)
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.parametrize(
    'user, answer', (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False)
    )
)
def test_comment_form_availability_for_different_users(
    news_pk,
    user,
    answer
):
    url = reverse('news:detail', args=news_pk)
    response = user.get(url)
    result = 'form' in response.context
    assert result == answer
