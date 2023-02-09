import shutil
import tempfile

from ..forms import PostForm
from ..models import Group, Post, User, Comment
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug',
            description='Тестовое описание',
            id=1
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост1234567',
            pk=1
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cache.clear()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_create_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={
                'username':
                    self.user.username}))
        post = Post.objects.exclude(pk=1).first()
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.exclude(pk=1).filter(
                text=form_data['text'],
                author=self.user,
                group=form_data['group'],
                image='posts/small.gif',
            ).exists(), Post.objects.filter(pk=2)[0]
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            post.text, form_data['text']),
        self.assertEqual(
            post.group.id,
            form_data['group'])

    def test_edit_post(self):
        form_data = {
            'text': 'Тестовый тексто',
            'group': self.group.id
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={
                'post_id': self.post.id}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))
        post = Post.objects.all().first()
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.text, form_data['text']),
        self.assertEqual(post.group.id, form_data['group'])

    def test_create_comm(self):
        comments_count = Comment.objects.filter(post=self.post).count()
        form_data = {
            'text': 'текст комм',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.filter(post=self.post).count(),
                         comments_count)
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.filter(post=self.post).count(),
                         comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                author=self.user,
                post=self.post
            ).exists(),
        )
