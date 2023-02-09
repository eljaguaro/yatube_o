from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import (PasswordChangeView,
                                       PasswordChangeDoneView,
                                       PasswordResetView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView)

urlpatterns = [
    path('', include('posts.urls', namespace='posts')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    # path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about')),
    path('password_change/', PasswordChangeView.as_view(template_name='users/password_change_form.html'), name='password_change_form'),
    path('password_change/done/', PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),
    path('password_reset/', PasswordResetView.as_view(template_name='users/password_reset_form.html'),name='password_reset_form'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password_reset_complete/',PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),name='password_reset_complete'),
]

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
handler403 = 'core.views.permission_denied'

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
