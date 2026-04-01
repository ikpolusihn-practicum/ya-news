from http import HTTPStatus
from datetime import datetime

import pytest
from django.urls import reverse
from django.test.client import Client

from news.models import News, Comment

@pytest.fixture
def comment_author(django_user_model):
    return django_user_model.objects.create(username='author')

@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create(username='other_user')

@pytest.fixture
def comment_author_client(comment_author):
    client = Client()
    client.force_login(comment_author)
    return comment_author_client

@pytest.fixture
def other_user_client(other_user):
    client = Client()
    client.force_login(other_user)
    return client

@pytest.fixture
def new():
    new = News.objects.create(
        title = 'new_title',
        text = 'new_text',
        date = datetime.today(),
    )

    return new

@pytest.fixture
def comment(new, comment_author):
    comment = Comment.objects.create(
        news=new,
        author=comment_author,
        text='some_comment',
    )

    return comment

@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_name',
    (
        'news:home',
        'news:detail',
        'users:login',
        'users:signup',
        'users:logout',
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


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_name, client_fixture, expected_status, expected_behavior',
    [
        # Author can access edit/delete
        ('news:edit', pytest.lazy_fixture('comment_author_client'), HTTPStatus.OK, 'access'),
        ('news:delete', pytest.lazy_fixture('comment_author_client'), HTTPStatus.OK, 'access'),

        # Other user cannot access edit/delete (404 not found)
        ('news:edit', pytest.lazy_fixture('other_user_client'), HTTPStatus.NOT_FOUND, 'forbidden'),
        ('news:delete', pytest.lazy_fixture('other_user_client'), HTTPStatus.NOT_FOUND, 'forbidden'),

        # Anonymous user is redirected to login
        # ('news:edit', pytest.lazy_fixture('anonymous_client'), HTTPStatus.FOUND, 'redirect'),
        # ('news:delete', pytest.lazy_fixture('anonymous_client'), HTTPStatus.FOUND, 'redirect'),
    ]
)
def test_comment_edit_and_delete_access_comprehensive(
        comment,
        url_name,
        client_fixture,
        expected_status,
        expected_behavior
):
    url = reverse(url_name, args=(comment.pk,))
    response = client_fixture.get(url)

    assert response.status_code == expected_status

    if expected_behavior == 'redirect':
        assert 'login' in response.url
