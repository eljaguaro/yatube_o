from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост1234567',
        )

    def test_models_have_correct_object_names(self):
        modelas = {
            self.post: 'Тестовый пост12',
            self.group: 'Тестовая группа'
        }
        for field, expected_value in modelas.items():
            with self.subTest(field=field):
                self.assertEqual(
                    str(field), expected_value)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'текст',
            'pub_date': 'дата публикации',
            'author': 'автор',
            'group': 'группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'основной текст поста',
            'pub_date': 'дата публикации поста',
            'author': 'имя автора поста',
            'group': 'название группы поста',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)
