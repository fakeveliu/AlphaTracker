"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from alphatracker import views

urlpatterns = [
    # top navbar
    path('', views.welcome_action, name='welcome'),
    path('companies', views.companies_action, name='companies'),
    path('investors', views.top_investors_ranking, name='top_investors_ranking'),
    path('community/<int:active_id>', views.community_action, name='community'),
    path('community', views.community_action, name='community'),
    #  path('debug', views.debug_action, name='debug'),
    path('mycollection', views.my_collection, name='my_collection'),

    path('oauth/', include('social_django.urls', namespace='social')),
    path('logout', views.user_logout, name='logout'),

    # companies page
    path('collect/<int:id>', views.collect_company, name='collect-action'),
    path('uncollect/<int:id>', views.uncollect_company, name='uncollect-action'),
    path('fetch-company', views.fetch_company),
    path('load-external-companies', views.external_companies_json_dumps_serializer),

    # market page
    path('market/<int:id>', views.market_company_action, name='market-company'),
    path('market/get-chart/<int:id>', views.stock_chart_json_dumps_serializer),
    path('transact/<int:id>', views.transact, name='transact-company'),

    # community page
    # path('post', views.post, name='post-article'),
    path('submit_post', views.submit_post, name="submit-post"),
    path('delete/<int:id>', views.delete_post, name='delete-post'),
    path('like/<int:id>', views.like_post, name='like-post'),
    path('unlike/<int:id>', views.unlike_post, name='unlike-post'),

    # my profile page
    path('changevis', views.change_visibility, name='change_visibility'),
    path('followers', views.my_followers, name='my_followers'),
    path('following', views.my_following, name='my_following'),
    path('othercollection/<int:id>', views.other_collection, name='other_collection'),
    path('uncollect_my_company/<int:id>', views.uncollect_my_company, name='uncollect-my-action'),
    path('my_transactions', views.my_transactions, name='my_transactions'),

    # other profile page
    path('unfollow/<int:id>', views.unfollow, name='unfollow'),
    path('follow/<int:id>', views.follow, name='follow'),
   #  path('image/<int:id>', views.get_image, name="image"),

    # notification page
    path('show_notifications', views.show_notifications, name='show_notifications'),
    path('judge_notifications', views.notifications_json_dumps_serializer),
    path('instructions', views.instructions, name='instructions')
]
