from django.db import models
from social_django import models as oauth_models
from django.contrib.auth.models import User

# Create your models here.
from alphatracker.widget import DatePickerInput

class Investor(models.Model):
    name            = models.CharField(max_length=50)
    account         = models.CharField(max_length=50)
    url             = models.CharField(max_length=50)
    join_time       = models.DateField()

class Company(models.Model):
    # company info
    name            = models.CharField(max_length=50)
    account         = models.CharField(max_length=50)
    url             = models.CharField(max_length=50)
    establish_time  = models.DateField()
    size            = models.IntegerField(default=0)

    # site data
    rating          = models.FloatField(default=0.0) # 0.0 if not recommended by algo
    modified_time   = models.DateTimeField()
    collected_times = models.IntegerField(default=0)
    created_by      = models.ForeignKey(User, null=True, blank=True, on_delete = models.CASCADE)
    collected_user  = models.ManyToManyField(User, related_name="collector")
    
    is_external     = models.BooleanField(null=True)
    investors       = models.ManyToManyField(Investor, related_name='invested_companies')

class CandleStick(models.Model):
    company     = models.ForeignKey(Company, on_delete = models.CASCADE)
    date        = models.DateField()
    max_price   = models.FloatField()
    min_price   = models.FloatField()
    open_price  = models.FloatField()
    close_price = models.FloatField()

class Profile(models.Model):
    collection          = models.ManyToManyField(Company, related_name='contributors')
    
    PRIVATE             = 'Private'
    FOLLOWERS_ONLY      = 'Followers Only'
    PUBLIC              = 'Public'
    VISIBILITY_CHOICES  = [
        (PRIVATE, 'Private'),
        (FOLLOWERS_ONLY, 'Followers Only'),
        (PUBLIC, 'Public')
    ]
    visibility          = models.CharField(max_length=14, choices=VISIBILITY_CHOICES, default=PUBLIC)
    user                = models.OneToOneField(User, default=None, on_delete=models.PROTECT)
    following           = models.ManyToManyField(User, related_name = 'followers')
    follower            = models.ManyToManyField(User, related_name = 'following')
    
    balance             = models.FloatField(default=10000.00)

    image               = models.FileField(blank=True)
    content_type        = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f'id={self.id}, user={self.user}, collection={self.collection}, balance={self.balance}'

class Transaction(models.Model):
    user_id          = models.IntegerField()
    company_id       = models.IntegerField()
    transaction_time = models.DateField()
    shares_held      = models.IntegerField()

class Post(models.Model):
    title               = models.TextField()
    content             = models.TextField()
    author              = models.ForeignKey(User, default=None, on_delete=models.PROTECT, related_name="author")
    BLOG                = 'Blog'
    NEWS                = 'News'
    INSIGHTS            = 'Insights'
    GENERAL             = 'General'
    CATEGORY_CHOICES    = [
        (BLOG, 'Blog'),
        (NEWS, 'News'),
        (INSIGHTS, 'Insights'),
        (GENERAL, 'General')
    ]
    category            = models.CharField(max_length=8, choices=CATEGORY_CHOICES, default=GENERAL) 
    modified_time       = models.DateTimeField() 
    liked_times         = models.IntegerField(default=0)
    liked_user          = models.ManyToManyField(User)

class Notification(models.Model):
    is_read     = models.BooleanField(default=False)
    message     = models.TextField()
    time        = models.DateTimeField(auto_now_add=True)
    receiver    = models.ForeignKey(User, default=None, on_delete=models.PROTECT, related_name='receiver') # I will receive the notifications
    sender      = models.ForeignKey(User, default=None, on_delete=models.CASCADE, related_name='sender') # User is not define here
    post        = models.ForeignKey(Post, default=None, null=True, blank=True, on_delete=models.CASCADE, related_name='post')
    # sender_id   = models.IntegerField() # store sender_id