from datetime import datetime

import pytest
from django.test.client import Client
from django.urls import reverse
from django.core.exceptions import ValidationError

from news.models import News, Comment
from news.forms import BAD_WORDS, WARNING


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
def new():
    new = News.objects.create(
        title = 'new_title',
        text = 'new_text',
        date = datetime.today(),
    )

    return new

@pytest.mark.django_db
@pytest.mark.parametrize(
    'scenario, client_fixture, expected_comments_count',
    (
        ('authorized_user', pytest.lazy_fixture('authorized_user_client'), 1),
        ('unauthorized_user', pytest.lazy_fixture('anonymous_user_client'), 0),
    )
)
def test_comment_creation(new, scenario, client_fixture, expected_comments_count):
    url = reverse('news:detail', args=(new.pk,))
    comment_data = {
        'text': 'comment_text',
    }
    client_fixture.post(url, comment_data)
    comment_count = Comment.objects.filter(news=new.pk).count()
    if scenario == 'authorized_user':
        assert comment_count == 1
    elif scenario == 'unauthorized_user':
        assert comment_count == 0

@pytest.mark.django_db
def test_bad_words_block(new, authorized_user_client):
    url = reverse('news:detail', args=(new.pk,))
    comment_data = {
        'text': f'comment_text_{BAD_WORDS[0]}',
    }
    authorized_user_client.post(url, comment_data)
    with pytest.raises(ValidationError):
        raise ValidationError(WARNING)
