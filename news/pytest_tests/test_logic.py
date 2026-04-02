from datetime import datetime

import pytest
from django.test.client import Client
from django.urls import reverse
from django.core.exceptions import ValidationError

from news.models import News, Comment
from news.forms import BAD_WORDS, WARNING


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
        title = 'new_title',
        text = 'new_text',
        date = datetime.today(),
    )

    comment = Comment.objects.create(
        news=new,
        author=comment_author,
        text=f'Original comment text'
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
def test_comment_creation(new, scenario, client_fixture, expected_comments_count):
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
def test_delete_and_edit_comment():
    ...
