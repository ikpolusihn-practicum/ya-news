import pytest
from datetime import timedelta, date

from django.urls import reverse
from pytest_django.fixtures import client

from news.models import News
from yanews import settings

NEWS_AMOUNT = 16

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
