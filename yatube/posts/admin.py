from django.contrib import admin
from .models import Post, Group


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group'
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    # скрыть author поле, чтобы оно не отображалось в форме изменений
    exclude = ('author',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'description',
    )
    empty_value_display = '-пусто-'


# admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
