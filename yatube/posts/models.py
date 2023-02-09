from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        "Название группы", max_length=200,
        help_text='Максимум 100 символов')
    slug = models.SlugField(
        "Краткое название группы",
        max_length=200, unique=True, help_text='Максимум 200 символов'
    )
    description = models.TextField("Описание",
                                   blank=True,
                                   null=True,
                                   help_text='Максимум 300 символов')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="текст",
                            help_text='основной текст поста', null=True)
    pub_date = models.DateTimeField(verbose_name="дата публикации",
                                    help_text='дата публикации поста',
                                    null=True, auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name="автор",
                               help_text='имя автора поста',
                               related_name='posts', null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              verbose_name="группа",
                              help_text='название группы поста',
                              related_name='posts',
                              blank=True, null=True
                              )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField(verbose_name="текст",
                            help_text='текст комментария', null=True)
    created = models.DateTimeField(verbose_name="дата публикации",
                                   help_text='дата публикации комментария',
                                   null=True, auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                               verbose_name="автор",
                               help_text='имя автора комментария',
                               related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             verbose_name="пост",
                             help_text='пост, связанный с комментарием',
                             related_name='comments'
                             )


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name="подписчик",
                             help_text='имя подписчика',
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name="автор",
                               help_text='автор на которого подписались',
                               related_name='following'
                               )
