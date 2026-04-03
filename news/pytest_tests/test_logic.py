from http import HTTPStatus
from datetime import datetime

import pytest
from django.test.client import Client
from django.urls import reverse
from django.core.exceptions import ValidationError

from news.models import News, Comment
from news.forms import BAD_WORDS, WARNING

ORIGINAL_COMMENT_TEXT = 'original comment text'
NEW_COMMENT_TEXT = 'new comment text'


@pytest.fixture
def comment_author(django_user_model):
    return django_user_model.objects.create(username='author')


@pytest.fixture
def comment_author_client(comment_author):
    client = Client()
    client.force_login(comment_author)
    return client


@pytest.fixture
def authorized_user(django_user_model):
    return django_user_model.objects.create(username='authorized_user')


@pytest.fixture
def authorized_user_client(authorized_user):
    client = Client()
    client.force_login(authorized_user)
    return client


@pytest.fixture
def anonymous_user_client():
    return Client()


@pytest.fixture
def new(comment_author):
    new = News.objects.create(
        title='new_title',
        text='new_text',
        date=datetime.today(),
    )

    comment = Comment.objects.create(
        news=new,
        author=comment_author,
        text=ORIGINAL_COMMENT_TEXT
    )

    return new, comment


@pytest.mark.django_db
@pytest.mark.parametrize(
    'scenario, client_fixture, expected_comments_count',
    (
        ('authorized_user', pytest.lazy_fixture('authorized_user_client'), 2),
        ('unauthorized_user', pytest.lazy_fixture('anonymous_user_client'), 1),
    )
)
def test_comment_creation(
        new,
        scenario,
        client_fixture,
        expected_comments_count
):
    new, comment = new
    url = reverse('news:detail', args=(new.pk,))
    comment_data = {
        'text': 'comment_text',
    }
    client_fixture.post(url, comment_data)
    comment_count = Comment.objects.filter(news=new.pk).count()
    assert comment_count == expected_comments_count


@pytest.mark.django_db
def test_bad_words_block(new, authorized_user_client):
    new, comment = new
    url = reverse('news:detail', args=(new.pk,))
    comment_data = {
        'text': f'comment_text_{BAD_WORDS[0]}',
    }
    authorized_user_client.post(url, comment_data)
    with pytest.raises(ValidationError):
        raise ValidationError(WARNING)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'action_scenario, user_type, client_fixture',
    (
        ('edit', 'author',
         pytest.lazy_fixture('comment_author_client'),),
        ('delete', 'author',
         pytest.lazy_fixture('comment_author_client'),),

        ('edit', 'other_user',
         pytest.lazy_fixture('authorized_user_client'),),
        ('delete', 'other_user',
         pytest.lazy_fixture('authorized_user_client'),),
    )
)
def test_delete_and_edit_comment(
        new,
        action_scenario,
        user_type,
        client_fixture,
):
    new, comment = new

    if action_scenario == 'delete':
        url = reverse('news:delete', args=(new.pk,))
        response = client_fixture.post(url)
        comment_count = Comment.objects.filter(news=new.pk).count()
        if user_type == 'author':
            assert response.status_code == HTTPStatus.FOUND
            assert comment_count == 0
        elif user_type == 'other_user':
            assert response.status_code == HTTPStatus.NOT_FOUND
            assert comment_count == 1

    elif action_scenario == 'edit':
        url = reverse('news:edit', args=(new.pk,))
        comment_new_version = {
            'text': NEW_COMMENT_TEXT,
        }
        response = client_fixture.post(url, data=comment_new_version)
        comment.refresh_from_db()

        if user_type == 'author':
            assert response.status_code == HTTPStatus.FOUND
            assert comment.text == NEW_COMMENT_TEXT

        elif user_type == 'other_user':
            assert response.status_code == HTTPStatus.NOT_FOUND
            assert comment.text == ORIGINAL_COMMENT_TEXT
