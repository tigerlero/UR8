from django.urls import path
from . import views
handler404 = views.handler404
handler500 = views.handler500
handler403 = views.handler403
handler400 = views.handler400
urlpatterns = [
    path('', views.home, name="home"),
    path('sign-up/', views.signup_view, name="sign_up"),
    path('sign-in/', views.signin_view, name="sign_in"),
    path('sign-out/', views.signout_view, name="sign_out"),
    path('profile/', views.profile, name="profile"),
    path('edit_avatar/', views.edit_avatar, name="edit_avatar"),
    path('reset-pwd/', views.reset_pwd, name="reset_pwd"),
    path('upload_video/', views.upload_video, name="upload_video"),
    path('uploaded_video/', views.view_vid, name="view_vid"),
    path('delete-video/<int:video_id>/', views.del_vid, name="del_vid"),
    path('sub/<int:channel_id>/', views.sub, name="sub"),
    path('del_subscribes/<int:channel_id>/', views.del_subscribes, name="del_subscribes"),
    path('del-notifications/<int:notification_id>/', views.del_notifications, name="del_notifications"),
    path('update-video/<int:video_id>/', views.updt_vid, name="updt_vid"),
    path('search_video/', views.search_vid, name="search_vid"),
    path('view-video/<int:video_id>/', views.s_vid, name="s_vid"),
    path('rated-video/<int:video_id>/', views.rated_video, name="rated_video"),
    path('liked-review/<int:video_id>/<int:review_id>/', views.rated_review, name="rated_review"),
    path('disliked-review/<int:video_id>/<int:review_id>/', views.rated_review2, name="rated_review2"),
    path('delete-review/<int:review_id>/<int:video_id>/', views.delete_review, name="delete_review"),
    path('edit-review/<int:video_id>/<int:review_id>/', views.edit_review, name="edit_review"),
    path('channel/<str:channel_slug>/', views.channel, name="channel"),
    path('notifications/', views.notifications, name="notifications"),
    path('subscribes/', views.subscribes, name="subscribes"),
    path('channels/', views.channels, name="channels"),
]