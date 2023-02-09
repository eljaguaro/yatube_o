import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.conf import settings
from django import forms
from django.urls import reverse
from ..models import Group, Post, User, Follow
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

POSTSNUM_PAGE1 = 10
POSTSNUM_PAGE2_1 = 3
POSTSNUM_PAGE_EMT = 0

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.user2 = User.objects.create(username='auth2')
        cls.user3 = User.objects.create(username='auth3')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug',
            description='Тестовое описание',
        )
        cls.img = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост1234567',
            group=cls.group,
            image=SimpleUploadedFile(
                name='image',
                content=cls.img,
                content_type='image'
            )
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cache.clear()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """ Создаем авторизованный клиент """
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        self.authorized_client3 = Client()
        self.authorized_client3.force_login(self.user3)
        self.authorized_client.get(reverse('posts:profile_follow', kwargs={
            'username':
                self.user2.username}))
        cache.clear()

    def post_test(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.image, self.post.image)

    def test__page_show_correct_context(self):
        response = self.guest_client.get(reverse('posts:index'))
        last_post = response.context['page_obj'][-1]
        self.post_test(last_post)

    def test_group_list_show_correct_context(self):
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}))
        last_post = response.context['page_obj'][-1]
        self.post_test(last_post)

    def test_profile_show_correct_context(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.post.author.username}))
        last_post = response.context['page_obj'][-1]
        self.post_test(last_post)

    def test_post_detail_pages_show_correct_context(self):
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        postcont = response.context.get('post')
        self.assertEqual(postcont.text, self.post.text)
        self.assertEqual(postcont.author, self.post.author)
        self.assertEqual(postcont.image, self.post.image)

    def test_create_post_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context.get('is_edit'), True)

    def test_index_cache(self):
        response = self.guest_client.get(reverse('posts:index'))
        res = response.content
        response.context['page_obj'][0].delete()
        response2 = self.guest_client.get(reverse('posts:index'))
        res2 = response2.content
        self.assertEqual(res, res2)
        cache.clear()
        response3 = self.guest_client.get(reverse('posts:index'))
        res3 = response3.content
        self.assertNotEqual(res, res3)

    def test_following(self):
        self.authorized_client.get(reverse('posts:profile_follow', kwargs={
            'username':
                self.user3.username}))
        self.assertTrue(
            Follow.objects.filter(user=self.user.id,
                                  author=self.user3.id
                                  ).exists())

    def test_unfollowing(self):
        self.authorized_client.get(reverse('posts:profile_unfollow', kwargs={
            'username':
                self.user2.username}))
        self.assertFalse(
            Follow.objects.filter(user=self.user.id,
                                  author=self.user2.id
                                  ).exists())

    def test_follow_index(self):
        self.authorized_client.get(reverse('posts:profile_follow', kwargs={
            'username':
                self.user2.username}))
        response1 = self.authorized_client.get(reverse('posts:follow_index'))
        res1 = response1.content
        response11 = self.authorized_client3.get(reverse('posts:follow_index'))
        res11 = response11.content
        Post.objects.create(
            author=self.user2,
            text='test-o-post')
        response2 = self.authorized_client.get(reverse('posts:follow_index'))
        res2 = response2.content
        response22 = self.authorized_client3.get(reverse('posts:follow_index'))
        res22 = response22.content
        self.assertNotEqual(res1, res2)
        self.assertEqual(res11, res22)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ALL_POSTS = 13
        cls.user = User.objects.create_user(username='autha')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        many_posts = []
        for _ in range(ALL_POSTS):
            many_posts.append(Post(
                author=cls.user,
                text='test post',
                group=cls.group
            ))
        Post.objects.bulk_create(many_posts)

    def setUp(self):
        """ Создаем авторизованный клиент """
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_index_pag(self):
        response = self.guest_client.get(reverse('posts:index'))
        post = response.context['page_obj']
        self.assertEqual(len(post), POSTSNUM_PAGE1)

    def test_index_pag2(self):
        """ Проверка: на второй странице должно быть три поста """
        response = self.client.get(reverse('posts:index') + '?page=2')
        post = response.context['page_obj']
        self.assertEqual(len(post), POSTSNUM_PAGE2_1)

    def test_group_list_pag(self):
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}))
        post = response.context['page_obj']
        self.assertEqual(len(post), POSTSNUM_PAGE1)

    def test_group_list_pag2(self):
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}) + '?page=2')
        post = response.context['page_obj']

        self.assertEqual(len(post), POSTSNUM_PAGE2_1)

    def test_profile_pag(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={
                'username': self.user.username}))
        post = response.context['page_obj']
        self.assertEqual(len(post), POSTSNUM_PAGE1)

    def test_profile_pag2(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={
                'username': self.user.username}) + '?page=2')
        post = response.context['page_obj']
        self.assertEqual(len(post), POSTSNUM_PAGE2_1)
