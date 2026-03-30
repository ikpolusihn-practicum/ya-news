from http import HTTPStatus
from datetime import datetime

import pytest
from django.urls import reverse

from news.models import News

@pytest.fixture
def new():
    new = News.objects.create(
        title = 'new_title',
        text = 'new_text',
        date = datetime.today(),
    )

    return new

@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_name',
    (
        'news:home',
        'news:detail',
        'users:login',
        'users:signup',
        'users:logout'
    )
)
def test_home_availability_for_anonymous_user(client, url_name, new):

    if url_name == 'news:detail':
        url = reverse(url_name, args=(new.pk,))
    else:
        url = reverse(url_name)


    if url_name == 'users:logout':
        response = client.post(url)
    else:
        response = client.get(url)
    assert response.status_code == HTTPStatus.OK
