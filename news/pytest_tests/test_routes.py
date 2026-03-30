from http import HTTPStatus

import pytest
from django.urls import reverse

@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_name',
    ('news:home', 'users:login', 'users:signup', 'users:logout')
)
def test_home_availability_for_anonymous_user(client, url_name):
    url = reverse(url_name)
    if url_name == 'users:logout':
        response = client.post(url)
    else:
        response = client.get(url)
    assert response.status_code == HTTPStatus.OK
