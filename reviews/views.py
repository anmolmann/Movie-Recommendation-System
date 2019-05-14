from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Review, Wine, Cluster, Fake
from .forms import ReviewForm
from .suggestions import svd_recommendations
from .ncf import load_model, update_model
from .fetch_videos import fetch
import datetime, sys
import pandas as pd
import numpy as np
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import tensorflow as tf

from django.contrib.auth.decorators import login_required

updated_model_init = False
previous_user = None

def about(request):
    return render(request, 'reviews/about.html')

def review_list(request):
    global updated_model_init
    global previous_user
    latest_review_list = Review.objects.order_by('-pub_date')[:12]
    context = {
        'latest_review_list':latest_review_list,
        'temp1': 'Not Found',
        'temp2': 'https://image.tmdb.org/t/p/w500None'
    }
    print(latest_review_list)

    if request.user.is_authenticated == True:
        user_id = request.user.id
        try:
            Fake.objects.get(actual_id=user_id)
        except:
            fake = Fake()
            fake.actual_id = user_id
            fake.fake_id = User.objects.count()
            fake.save()
            print(fake.actual_id, fake.fake_id, '---------the--end')

    try:
        user_id = request.user.id
        if previous_user != user_id:
            updated_model_init = False
            previous_user = user_id
        temp = User.objects.get(id=user_id)
        print(temp.last_login.time().strftime("%H:%M:%S"), temp.date_joined.time().strftime("%H:%M:%S"))
        if (not updated_model_init) and (temp.last_login.date() == temp.date_joined.date()):
            if abs(int(temp.last_login.time().strftime("%M")) - int(temp.date_joined.time().strftime("%M"))) < 2:
                update_model(user_id, True)
                updated_model_init = True
    except:
        None

    return render(request, 'reviews/review_list.html', context)


def review_detail(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    return render(request, 'reviews/review_detail.html', {'review': review})


def wine_list(request):
    wine_list = Wine.objects.order_by('-name')
    #wine_list = fetch(wine_list)
    
    page = request.GET.get('page', 1)
    paginator = Paginator(wine_list, 12)

    try:
        wine_list = paginator.page(page)
    except PageNotAnInteger:
        wine_list = paginator.page(1)
    except EmptyPage:
        wine_list = paginator.page(paginator.num_pages)

    # Get the index of the current page
    index = wine_list.number - 1  # edited to something easier without index
    # This value is maximum index of your pages, so the last page - 1
    max_index = len(paginator.page_range)
    # You want a range of 7, so lets calculate where to slice the list
    start_index = index - 3 if index >= 3 else 0
    end_index = index + 3 if index <= max_index - 3 else max_index
    # Get our new page range. In the latest versions of Django page_range returns 
    # an iterator. Thus pass it to list, to make our slice possible again.
    page_range = list(paginator.page_range)[start_index:end_index]

    context = {
        'wine_list':wine_list,
        'page_range': page_range, 
        'temp1': 'Not Found',
        'temp2': 'https://image.tmdb.org/t/p/w500None'
     }

    return render(request, 'reviews/wine_list.html', context)


def wine_detail(request, wine_id):
    movie_obj = get_object_or_404(Wine, pk=wine_id)
    movie_info = fetch(movie_obj)

    form = ReviewForm()

    return render(
        request, 
        'reviews/wine_detail.html',
        {'wine': movie_obj,
         'form': form,
         'movie_info': movie_info,
         'temp1': 'Not Found', 
         'temp2': 'https://image.tmdb.org/t/p/w500None'
         })


# limit the access to our add_review view so only logged-in users can use it.

@login_required
def add_review(request, wine_id):
    wine = get_object_or_404(Wine, pk=wine_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        rating = form.cleaned_data['rating']
        comment = form.cleaned_data['comment']
        # user_name = form.cleaned_data['user_name']

        # The request object has a reference to the active user,
        # and this instance has a username field that we can use as needed.
        user_name = request.user.username
        user_id = request.user.id

        print('User id: {}\t-------\t User name: {}'.format(user_id, user_name))

        try:
            # if review by this user on this movie already exists then update the rating
            obj = Review.objects.get(wine__id=wine.id, user_id=user_id)
            obj, created = Review.objects.update_or_create(
                user_id=user_id, wine__id=wine.id,
                defaults={'rating':rating,
                         'comment': comment,
                         'pub_date': datetime.datetime.now()})
        except:
            # otherwise save a new review
            review = Review()
            review.wine = wine
            review.user_id = user_id
            review.user_name = user_name
            review.rating = rating
            review.comment = comment
            review.pub_date = datetime.datetime.now()
            review.save()

        update_model(request.user.id)

        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('reviews:wine_detail', args=(wine.id,)))
    
    return render(
        request, 
        'reviews/wine_detail.html', 
        {'wine': wine, 'form': form, 'username': user_name}
        )

@login_required
def user_review_list(request, username=None):
    global updated_model_init
    global previous_user
    user_id = request.user.id
    if not username:
        username = request.user.username

    try:
        update_Fake = Fake.objects.get(actual_id=user_id)
    except:
        fake = Fake()
        fake.actual_id = user_id
        fake.fake_id = User.objects.count()
        fake.save()

    print((Fake.objects.get(actual_id=user_id)).fake_id, ': fake id\t--------')
    print(request.user.username, '-----------', request.user.id)

    if previous_user != user_id:
        updated_model_init = False
        previous_user = user_id
    temp = User.objects.get(id=user_id)
    print(temp.last_login.time().strftime("%H:%M:%S"), temp.date_joined.time().strftime("%H:%M:%S"))
    if (not updated_model_init) and (temp.last_login.date() == temp.date_joined.date()):
        if abs(int(temp.last_login.time().strftime("%M")) - int(temp.date_joined.time().strftime("%M"))) < 2:
            update_model(user_id, True)
            updated_model_init = True

    latest_review_list = Review.objects.filter(user_name=username).order_by('-pub_date')
    context = {'latest_review_list':latest_review_list, 'username':username}
    return render(request, 'reviews/user_review_list.html', context)

# Wine represents the items to be recommended to the users (movies in this case)
@login_required
def user_recommendation_list(request):
    
    temp = svd_recommendations(request.user.id)
    error = temp[0]
    preds = (temp[1])[:10]
    print(preds)
    wine_list = Wine.objects.filter(id__in=preds.MovieID.values)

    return render(
        request, 
        'reviews/user_recommendation_list.html', 
        {'username': request.user.username, 'wine_list': wine_list, 'error': error}
        )

#already_trained = False

@login_required
def ncf_users_recommendation_list(request):

    #global already_trained

    print("Predicting")

    user_reviews = Review.objects.filter(user_name=request.user.username).prefetch_related('wine')

    # 2. from the ratings, get a set of movie IDs which the user has rated
    user_reviews_wine_ids = set(map(lambda x: x.wine.id, user_reviews))
    # then get a movie ids excluding the previous IDs
    wine_list = Wine.objects.exclude(id__in=user_reviews_wine_ids)
    
    res = []
    user_id = Fake.objects.get(actual_id = request.user.id).fake_id


    with tf.Session():
        if (len(user_reviews_wine_ids) != 0):
            model = load_model()
            model.load_weights("./model.h5")
            for row in wine_list:
                res.append([row.id, 
                    model.predict(
                        [np.array([user_id]), np.array([row.id])]
                    )[0][0]]
                )
            res = pd.DataFrame(res, columns=['movieid', 'prediction'])
        else:
            #update model
            #update_model(user_id, True)
            #model = load_model()
            #model.load_weights("./model.h5")
            #for row in wine_list:
            #    res.append([row.id, model.predict(
            #        [np.array([user_id]), np.array([row.id])]
            #        )[0][0]])

            # wine.review_set.count

            temp = pd.DataFrame(list(Wine.objects.all()), columns=['wine'])
            res = pd.DataFrame(
                [[i.average_rating(), i.review_set.count(), i.id] for i in temp.wine.values.tolist()],
                columns=['prediction', 'count', 'movieid']
                )

            res = res.sort_values(by='count', ascending=False)[:10]

            #print(res.head())

    res = res.sort_values(by='prediction', ascending=False)

    #print(res.head())

    temp = res.movieid.values[:10]

    wine_list = Wine.objects.filter(id__in=temp)

    return render(
        request, 
        'reviews/ncf_users_recommendation_list.html', 
        {'username': request.user.username,'wine_list': wine_list}
    )