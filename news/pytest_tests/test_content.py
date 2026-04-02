import pytest
from datetime import timedelta, date

from django.urls import reverse
from pytest_django.fixtures import client
from django.test.client import Client
from django.utils import timezone

from news.models import News, Comment
from yanews import settings

NEWS_AMOUNT = 16
COMMENTS_AMOUNT = 5

@pytest.fixture
def news_creation():
    current_date = date.today()

    news_list = [
        News(
            title=f'new_title_{i}',
            text=f'new_text_{i}',
            date=current_date - timedelta(days=i),
        )
        for i in range(NEWS_AMOUNT)
    ]
    News.objects.bulk_create(news_list)

@pytest.fixture
def comment_author(django_user_model):
    return django_user_model.objects.create(username='author')

@pytest.fixture
def comment_author_client(comment_author):
    client = Client()
    client.force_login(comment_author)
    return client

@pytest.fixture
def anonymous_user_client():
    return Client()

@pytest.fixture()
def create_one_new(comment_author):

    new = News.objects.create(
        title='new_title',
        text='new_text',
        date=date.today() - timedelta(days=COMMENTS_AMOUNT),
    )

    for i in range(COMMENTS_AMOUNT):
        comment = Comment.objects.create(
            news=new,
            author=comment_author,
            text=f'Comment text {i}'
        )
        comment.created = timezone.now() - timedelta(days=i)
        comment.save()

    return new

@pytest.mark.django_db
def test_news_amount_and_order(client, news_creation):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE

    dates_from_page = [new.date for new in object_list]
    current_date = date.today()
    expected_dates = [current_date - timedelta(days=i) for i in range(NEWS_AMOUNT)]
    expected_dates = sorted(expected_dates, reverse=True)[:settings.NEWS_COUNT_ON_HOME_PAGE]

    assert dates_from_page == expected_dates

@pytest.mark.django_db
def test_comments_order(create_one_new, comment_author_client):
    url = reverse('news:detail', args=(create_one_new.pk,))
    response = comment_author_client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
    assert 'form' in response.context

@pytest.mark.django_db
def test_comment_form_not_available_for_unauthorised_user(anonymous_user_client, create_one_new):
    url = reverse('news:detail', args=(create_one_new.pk,))
    response = anonymous_user_client.get(url)
    assert 'form' not in response.context
