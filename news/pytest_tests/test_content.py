import pytest
from datetime import datetime, timedelta

from django.urls import reverse

from news.models import News
from yanews import settings

NEWS_AMOUNT = 16

@pytest.fixture
def news_creation():

    current_date = datetime.today()

    news_list = [
        News(
            title=f'new_title_{i}',
            text=f'new_text_{i}',
            date=current_date - timedelta(days=1),
        )
        for i in range(1, NEWS_AMOUNT)
    ]

    News.objects.bulk_create(news_list)

@pytest.mark.django_db
def test_new_amount():
    response = reverse('news:home')
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE
