from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
# from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import logout
import random

import json
import fake_data.fake_data_generator as fd
from alphatracker.forms import addCompanyForm
from alphatracker.models import Company, Profile, Investor, Notification, CandleStick, Transaction, Post

# ---------------------------------------------------------------------------- #
#                           Authentication and Setup                           #
# ---------------------------------------------------------------------------- #

def _known_user_check(action_function):
    def my_wrapper_function(request, *args, **kwargs):
        if 'picture' not in request.session:
            request.session['picture'] = request.user.social_auth.get(provider='google-oauth2').extra_data['picture']
        return action_function(request, *args, **kwargs)
    return my_wrapper_function

def user_logout(request):
    context = {}
    logout(request)
    return render(request, "alphatracker/welcome.html", context)

def welcome_action(request):
    context = {}
    if request.user.is_authenticated:
        if not Company.objects.exists():
            make_data(100, 20)
        if 'picture' not in request.session:
            request.session['picture'] = request.user.social_auth.get(provider='google-oauth2').extra_data['picture']
        if not Profile.objects.filter(user=request.user):
            profile = Profile(user=request.user, image=request.session['picture'])
            profile.save()
    return render(request, "alphatracker/welcome.html", context)

def make_data(num_companies, num_investors):
    data = fd.fake_data(num_companies, num_investors, "")

    for j in range(num_investors):
        (inv_name, join_time, inv_acc, inv_url) = \
            (data["investor_name"][j],
             data["investor_join_time"][j],
             data["investor_account"][j],
             data["investor_url"][j])
        new_investor = Investor(name=inv_name, join_time=join_time, 
            account=inv_acc, url=inv_url)
        new_investor.save()

    comp_to_inv     = data["company_investors"]
    comp_to_stock   = data["company_stock"]
    for i in range(num_companies):
        (name, est, acc, url, size) = \
            (data["company_name"][i],
             data["establish_time"][i],
             data["company_account"][i],
             data["company_url"][i],
             data["company_size"][i])
        new_company = Company(name=name, account=acc, establish_time=est, 
            url=url, size=size, modified_time=timezone.now(),
            is_external = True if (random.uniform(0, 1) > 0.3) else False)
        new_company.save()
        for investor_name in comp_to_inv[name]:
            investor = Investor.objects.get(name=investor_name)
            new_company.investors.add(investor)
        for stick in comp_to_stock[name]:
            new_stick = CandleStick(company=new_company, date=stick["date"],
                max_price=stick["max_price"], min_price=stick["min_price"],
                open_price=stick["open_price"], close_price=stick["close_price"])
            new_stick.save()

# ---------------------------------------------------------------------------- #
#                                Top Bar Actions                               #
# ---------------------------------------------------------------------------- #

@login_required
def show_notifications(request):
    context = {}
    new_notifications = Notification.objects.filter(receiver=request.user, is_read = False).order_by('-id').exclude(sender = request.user)
    nn_copy = new_notifications.all()
    new_list = []
    for new_notification in new_notifications:
        new_notification.is_read = True
        new_notification.save()
        new_list.append(new_notification.id)
    print(new_list)
    old_notifications = Notification.objects.filter(receiver=request.user).order_by('-id').exclude(sender = request.user)
    old_notifications2 = old_notifications.exclude(id__in=new_list)
    context["new_notifications"] = new_notifications
    context["old_notifications"] = old_notifications2
    print(new_notifications)
    print("-------------")
    print(old_notifications)
    return render(request, "alphatracker/notification.html", context)

def notifications_json_dumps_serializer(request):
    if not request.user.is_authenticated:
        return render(request, "alphatracker/welcome.html", {})
    print(request.user)
    # print(Notification.objects.filter(receiver=request.user))
    notifications = Notification.objects.filter(receiver=request.user, is_read = False).exclude(sender = request.user)
    if notifications.exists():
        print(notifications)
        flag = 1 # Have unread
    else:
        flag = 0 # No unread
    response_data = {
        'flag' : flag
    }
    response_json = json.dumps(response_data)
    print(response_data)
    return HttpResponse(response_json, content_type='application/json')

# ---------------------------------------------------------------------------- #
#                                Companies Table                               #
# ---------------------------------------------------------------------------- #

@login_required
@_known_user_check
def companies_action(request):
    context = {}
    if request.user.is_authenticated:
        context = {'name': request.user.username, 
        'items': Company.objects.filter(is_external=False).order_by("name")}
    return render(request, "alphatracker/top_companies.html", context)

def external_companies_json_dumps_serializer(request):
    if not request.user.is_authenticated:
        return render(request, "alphatracker/welcome.html", {})
    
    external_companies = Company.objects.all()
    external_companies_response_data = []
    for external_company in external_companies:
        external_companies_response_data.append(external_company.name)

    response_data = {
        'external_companies' : external_companies_response_data
    }
    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')

def _my_json_error_response(message, status=200):
    response_json = '{ "error": "' + message + '" }'
    return HttpResponse(response_json, content_type='application/json', status=status)

@login_required
def fetch_company(request):
    context = {}
    if not request.user.is_authenticated:
        return render(request, "alphatracker/welcome.html", context)

    context['name'] = request.user.username
    context['items'] = Company.objects.filter(is_external=False).order_by("name")

    if not request.method == "POST":
        context['error'] = 'Method Not Allowed'
        return render(request, "alphatracker/top_companies.html", context)
    if not "input_company" in request.POST:
        context['error'] = 'Bad Request'
        return render(request, "alphatracker/top_companies.html", context)

    input_company = request.POST["input_company"]
    try:
        query_company = Company.objects.get(name=input_company)
        if query_company.is_external: # external
            query_company.is_external = False
            query_company.modified_time = timezone.now()
            query_company.created_by = request.user
            query_company.save()
        else:
            context['error'] = f'Company {input_company} is already in table'
    except Exception as e:
        context['error'] = f'External company {input_company} does not exist'

    return render(request, "alphatracker/top_companies.html", context)
        
def input_investor(request):
    pass

@login_required
def collect_company(request, id):
    context = {}
    company = get_object_or_404(Company, id=id)
    company.collected_user.add(request.user)
    company.collected_times = company.collected_user.count()
    company.save()
    request.user.profile.collection.add(company)
    request.user.save()
    context["items"] = Company.objects.all()
    return redirect(reverse('companies'))

@login_required
def uncollect_company(request, id):
    context = {}
    company = get_object_or_404(Company, id=id)
    company.collected_user.remove(request.user)
    company.collected_times = company.collected_user.count()
    company.save()
    request.user.profile.collection.remove(company)
    request.user.save()
    context["items"] = Company.objects.all()
    return redirect(reverse('companies'))

@login_required
def uncollect_my_company(request, id):
    context = {}
    company = get_object_or_404(Company, id=id)
    company.collected_user.remove(request.user)
    company.collected_times = company.collected_user.count()
    company.save()
    request.user.profile.collection.remove(company)
    request.user.save()
    # context["items"] = Company.objects.all()
    context = {'profile': request.user.profile,}
    print(request.user.profile.collection.all()) # check all the collections for this user
    return render(request, "alphatracker/my_collection.html", context)

# ---------------------------------------------------------------------------- #
#                                   Community                                  #
# ---------------------------------------------------------------------------- #

@login_required
def community_action(request, active_id=None):
    context = {}
    context["items"] = Post.objects.all().order_by('-id')
    # active_id is post id
    if active_id == None:
        context["active_idx"] = 1
    else:
        active_idx = Post.objects.filter(id__lte=active_id).count()
        context["active_idx"] = Post.objects.count() - active_idx + 1
    # print(context)
    # print(active_idx)
    return render(request, "alphatracker/community.html", context)

@login_required
def submit_post(request):
    context = {}
    context["items"] = Post.objects.all().order_by('id')
    # Do you sure we should pass context post below?
    if not request.user.is_authenticated:
        return render(request, "alphatracker/welcome.html", context)

    if not request.method == "POST":
        context["error"] = "Method Not Allowed"
        return render(request, "alphatracker/community.html", context)
    if (not "title" in request.POST) or (not "content" in request.POST) \
        or (not "category" in request.POST):
        context["error"] = "Bad Request"
        return render(request, "alphatracker/community.html", context)

    title = request.POST['title']
    if len(title) == 0:
        context["error"] = "Title cannot be empty"
        return render(request, "alphatracker/community.html", context)
    if len(title) > 150:
        context["error"] = "Title cannot be more than 150 characters long"
        return render(request, "alphatracker/community.html", context)
    
    content = request.POST['content']
    if len(content) == 0:
        context["error"] = "Article cannot be empty"
        return render(request, "alphatracker/community.html", context)
    if len(content) > 120000:
        context["error"] = "Article is too long"
        return render(request, "alphatracker/community.html", context)
    
    category = request.POST['category']
    if not category in [Post.BLOG, Post.NEWS, Post.INSIGHTS, Post.GENERAL]:
        context["error"] = "Invalid article category"
        return render(request, "alphatracker/community.html", context)
        
    author = request.user
    modified_time = timezone.now()
    try:
        post = Post(title = title,
                    content = content,
                    author = author,
                    category = category,
                    modified_time = modified_time)
        post.save()
        print("post is saved.")
    except:
        context["error"] = "Bad Request"
        return render(request, "alphatracker/community.html", context)

    # return render(request, "alphatracker/community.html", context)
    return redirect('community')

@login_required
def delete_post(request, id):
    print(id)
    if not request.user.is_authenticated:
        return render(request, "alphatracker/welcome.html")
    # context = {}
    # context["items"] = Post.objects.all().order_by('id')
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect('community')
    # return redirect('community', msg="good")
    # return render(request, "alphatracker/community.html", context)

@login_required
def like_post(request, id):
    if not request.user.is_authenticated:
        return render(request, "alphatracker/welcome.html")
    post = get_object_or_404(Post, id=id)
    post.liked_user.add(request.user)
    post.liked_times = post.liked_user.count()
    post.save()
    notification = Notification(is_read = False,
                            message = " is liked by ",
                            time = timezone.now(),
                            receiver = post.author,
                            sender = request.user, 
                            post = post)
    notification.save()
    print("notification created")
    print(notification)
    return redirect('community', active_id=id)

@login_required
def unlike_post(request, id):
    if not request.user.is_authenticated:
        return render(request, "alphatracker/welcome.html")
    post = get_object_or_404(Post, id=id)
    post.liked_user.remove(request.user)
    post.liked_times = post.liked_user.count()
    post.save()
    return redirect('community', active_id=id)

# ---------------------------------------------------------------------------- #
#                                    Market                                    #
# ---------------------------------------------------------------------------- #

def stock_chart_json_dumps_serializer(request, id):
    if not request.user.is_authenticated:
        return render(request, "alphatracker/welcome.html", {})
    company = get_object_or_404(Company, id=id)
    chart_response_data = []
    for stick in company.candlestick_set.all():
        stick_data = {
            "date"          : stick.date.strftime("%m/%d/%Y"),
            "max_price"     : stick.max_price,
            "min_price"     : stick.min_price,
            "open_price"    : stick.open_price,
            "close_price"   : stick.close_price
        }
        chart_response_data.append(stick_data)

    response_data = {
        'company_id'   : id,
        'company_name'  : company.name,
        'sticks'        : chart_response_data
    }
    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')

@login_required
def market_company_action(request, id):
    context = {}

    company = get_object_or_404(Company, id=id)
    news = Post.objects.filter(category="News", content__contains=str(company.name)) | Post.objects.filter(category="News", title__contains=str(company.name))
    context["news"] = news
    context["profile"] = request.user.profile
    context["company"] = company
    msg = request.session.pop('msg', False)

    context["latest_price_info"] = CandleStick.objects.filter(company=company).order_by('-id')[0]

    try:
        transaction = Transaction.objects.filter(company_id=id, user_id=request.user.id).order_by('-id')
        latest_shares = transaction[0].shares_held
    except:
        latest_shares = 0
    context["shares_held"] = latest_shares
    context["transactions"] = transaction

    if msg:
        context["msg"] = msg
    print(news)
    return render(request, "alphatracker/market_company.html", context)

@login_required
def transact(request, id):
    if not request.user.is_authenticated:
        return render(request, "alphatracker/welcome.html", {})
    if not request.method == "POST":
        request.session['msg'] = 'Method Not Allowed'
        return redirect(reverse('market-company', kwargs={'id': id}))
    if (not "quantity" in request.POST) or \
        not ("buy_company" in request.POST or "sell_company" in request.POST):
        request.session['msg'] = 'Bad Request'
        return redirect(reverse('market-company', kwargs={'id': id}))
    
    # validates quantity
    quantity = request.POST['quantity']
    if not quantity.isdigit():
        request.session['msg'] = "Input number of shares is not a positive integer"
        return redirect(reverse('market-company', kwargs={'id': id}))
    quantity = int(quantity)

    company = get_object_or_404(Company, id=id)
    company_id = company.id
    user_id = request.user.id
    candlestick = CandleStick.objects.filter(company=company).order_by('-id')[0]
    transaction_time = candlestick.date
    price = (candlestick.open_price + candlestick.close_price)/2
    msg = ''

    if 'buy_company' in request.POST:
        try:
            latest = Transaction.objects.filter(company_id=company_id, user_id=user_id).order_by('-id')[0]
            current_shares_held = latest.shares_held + quantity
        except:
            current_shares_held = quantity
        new_transaction = Transaction(company_id = company_id, 
                                        user_id = user_id, 
                                        transaction_time = transaction_time,
                                        shares_held = current_shares_held)
        new_transaction.save()
        request.user.profile.balance -= price * int(quantity)
        request.user.profile.save()
        msg = f'You successfuly bought {quantity} shares and currently hold {current_shares_held} shares.'
    elif 'sell_company' in request.POST:
        try:
            latest = Transaction.objects.filter(company_id=company_id, user_id=user_id).order_by('-id')[0]
            current_shares_held = latest.shares_held - quantity
        except:
            current_shares_held = -quantity
        new_transaction = Transaction(company_id = company_id, 
                                        user_id = user_id, 
                                        transaction_time = transaction_time,
                                        shares_held = current_shares_held)
        new_transaction.save()
        request.user.profile.balance += price * quantity
        request.user.profile.save()
        msg = f'You successfuly sold {quantity} shares and currently hold {current_shares_held} shares.'

    request.session['msg'] = msg
    return redirect(reverse('market-company', kwargs={'id': id}))

# ---------------------------------------------------------------------------- #
#                                  My Profile                                  #
# ---------------------------------------------------------------------------- #


def get_image(request, id):
    user = get_object_or_404(User, id=id)
    profile = user.profile
    if not profile.image:
        raise Http404
    return HttpResponse(profile.image, content_type=profile.content_type)

@login_required
def my_collection(request):
    # my_profile = Profile.objects.filter(user=request.user)
    # print(request.user.profile.collection.all())
    context = {}
    if request.method == 'GET':
        context = {'profile': request.user.profile,}
        print(request.user.profile.visibility)
        return render(request, "alphatracker/my_collection.html", context)

@login_required
def my_transactions(request):
    if request.method == 'GET':
        profile = request.user.profile
        transactions = Transaction.objects.all().values()
        # transactions_info = []
        transaction_records = {} # {1, transaction_record}
        transaction_records_list = [] # [transaction_record]
        for transaction in transactions:
            if transaction['user_id'] == request.user.id:
                transaction_record = {} # {..., 'shares_held', 'transaction_table_list': transaction_table_list}
                transaction_table_list_item = {} # {'transaction_time': 2022-11-12, 'shares_held': 22 }
                company_id = transaction['company_id']
                if company_id in transaction_records.keys():
                    transaction_record = transaction_records[company_id]
                    transaction_record['shares_held'] = transaction['shares_held']
                else:
                    company = Company.objects.get(id=transaction['company_id'])
                    transaction_record['company_id'] = transaction['company_id']
                    transaction_record['name'] = company.name
                    transaction_record['establish_time'] = company.establish_time
                    transaction_record['size'] = company.size
                    transaction_record['created_by'] = company.created_by
                    transaction_record['modified_time'] = company.modified_time
                    transaction_record['collected_times'] = company.collected_times
                    transaction_record['shares_held'] = transaction['shares_held']
                transaction_table_list_item['transaction_time'] = transaction['transaction_time']
                transaction_table_list_item['shares_held'] = transaction['shares_held']
                if 'transaction_table_list' in transaction_record:
                    transaction_table_list = transaction_record['transaction_table_list']
                else:
                    transaction_table_list = []
                transaction_table_list.append(transaction_table_list_item)
                transaction_record['transaction_table_list'] = transaction_table_list[::-1]
                transaction_records[company_id] = transaction_record
        for transaction_record_value in transaction_records.values():
            transaction_records_list.append(transaction_record_value)
        print(transaction_records)
        context = {'transaction_records': transaction_records_list, 'profile': profile}
        return render(request, "alphatracker/my_transaction.html", context)

@login_required
def change_visibility(request):
    vis = request.POST['visibility']
    print(vis)
    # print(request.user.profile.collection.all())
    request.user.profile.visibility = str(vis)
    request.user.profile.save()
    context = {}
    context = {'profile': request.user.profile,}
    print("user request: " + vis)
    print("user now: " + request.user.profile.visibility)
    return render(request, "alphatracker/my_collection.html", context)

@login_required
def my_followers(request):
    context = {}
    if request.method == 'GET':
        context = {'profile': request.user.profile,}
        print(request.user.profile.follower)
    return render(request, "alphatracker/my_followers.html", context)

@login_required
def my_following(request): 
    context = {}
    if request.method == 'GET':
        context = {'profile': request.user.profile,}
        print(request.user.profile.following)
    return render(request, "alphatracker/my_following.html", context)

# ---------------------------------------------------------------------------- #
#                             Other Profile Actions                            #
# ---------------------------------------------------------------------------- #

@login_required
def follow(request, id):
    user_to_follow = get_object_or_404(User, id=id)
    request.user.profile.following.add(user_to_follow)
    request.user.save()
    user_to_follow.profile.follower.add(request.user)
    user_to_follow.save()
    notification = Notification(is_read = False,
                                message = "You are followed by ",
                                time = timezone.now(),
                                receiver = user_to_follow,
                                sender = request.user)
    notification.save()
    print("notification created")
    print(notification)
    return redirect('other_collection', id=id)

@login_required
def unfollow(request, id):
    user_to_unfollow = get_object_or_404(User, id=id)
    request.user.profile.following.remove(user_to_unfollow)
    request.user.save()
    user_to_unfollow.profile.follower.remove(request.user)
    user_to_unfollow.save()
    return redirect('other_collection', id=id)

# ---------------------------------------------------------------------------- #
#                                  URL Actions                                 #
# ---------------------------------------------------------------------------- #

@login_required
def other_collection(request, id):
    context = {}
    profile = get_object_or_404(Profile, id=id)
    print("my followering: ")
    print(request.user.profile.following.all())
    print("other user's visibility: " + profile.visibility)
    # print(profile.user in request.user.profile.following.all())
    # my_profile = Profile.objects.filter(user=request.user)
    if request.method == 'GET':
        if profile.visibility == "Public":
            context = {'profile': profile,}
            return render(request, "alphatracker/other_collection.html", context)
        else:
            if profile.visibility == "Followers Only" and profile.user in request.user.profile.following.all():
                context = {'profile': profile,}
                return render(request, "alphatracker/other_collection.html", context)
            else:
                context = {'profile': profile,
                            'msg': "This user's collection is hidden."}
                return render(request, "alphatracker/other_collection_hidden.html", context)

@login_required
def top_investors_ranking(request):
    context = {}
    if request.method == 'GET':
        context = {'profiles': Profile.objects.all().order_by('-balance')}
        print( Profile.objects.all())
    # context["items"] = Investor.objects.all()
    return render(request, "alphatracker/top_investors.html", context)

@login_required
def instructions(request):
    return render(request, "alphatracker/instructions.html", {})

# ----------------------------------- debug ---------------------------------- #

def debug_action(request):
    twitter_companies = Company.objects.filter(is_external=True)
    alphatracker_companies = Company.objects.filter(is_external=False)
    context = {
        "twitter_companies" : twitter_companies,
        "alphatracker_companies" : alphatracker_companies
    }
    return render(request, "alphatracker/debug.html", context)
