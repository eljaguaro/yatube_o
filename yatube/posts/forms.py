from .models import Post, Comment
from django import forms


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст',
            'group': 'Группа',
        }
        exclude = ('date', 'author')

    def clean_subject(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Вы должны что-то написать')
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст',
        }
        exclude = ('date', 'author', 'post')

    def clean_subject(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Вы должны что-то написать')
        return data
