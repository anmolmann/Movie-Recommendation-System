from .models import Review, Wine, Cluster, Fake
from django.contrib.auth.models import User
from sklearn.cluster import KMeans
from scipy.sparse import dok_matrix, csr_matrix
import pandas as pd
import numpy as np
import datetime
from django.shortcuts import get_object_or_404


#function for recommendation engine 
def recommend_movies(predictions_df, userID, movies_df, original_ratings_df, num_recommendations=10):
    
    # Get and sort the user's predictions

    # UserID starts at 1, not 0
    user_row_number = userID - 1 
    print(user_row_number)

    # UserID starts at 1
    sorted_user_predictions = predictions_df.iloc[user_row_number].sort_values(ascending=False) 
    
    # Get the user's data and merge in the movie information.
    user_data = original_ratings_df[original_ratings_df.UserID == (userID)]
    user_full = (user_data.merge(movies_df, how = 'left', left_on = 'MovieID', right_on = 'MovieID').
                     sort_values(['Rating'], ascending=False)
                 )

    print ('User {0} has already rated {1} movies.'.format(userID, user_full.shape[0]))
    print ('Recommending highest {0} predicted ratings movies not already rated.'.format(num_recommendations))
    
    # Recommend the highest predicted rating movies that the user hasn't seen yet.
    recommendations = (movies_df[~movies_df['MovieID'].isin(user_full['MovieID'])].merge(
            pd.DataFrame(sorted_user_predictions).reset_index(), 
            how = 'left',
            left_on = 'MovieID',
            right_on = 'MovieID'
        ).rename(
                columns = {user_row_number: 'Predictions'}
            ).sort_values(
                'Predictions',
                 ascending = False
                 ).iloc[:num_recommendations, :-1])

    return recommendations


def svd_recommendations(current_user):
    
    # the users explicit reviews/ratings table
    ratings_df = pd.DataFrame(list(Review.objects.values_list('user_id', 'wine__id', 'rating')),
                                 columns=['UserID', 'MovieID', 'Rating'])

    error = None
    temps = Review.objects.filter(user_id__gte=944)

    temps = set(temps.values_list('user_id', flat=True))

    for i in temps:
        ratings_df.loc[ratings_df['UserID'] == i] = Fake.objects.get(actual_id=i).fake_id
        #print(i, ratings_df.loc[ratings_df['UserID'] == i])

    add_init_review = False
    check_user_existence = Review.objects.filter(user_id=current_user)
    if not check_user_existence:
        add_init_review = True
        print('No reviews yet!')
        index = np.random.choice(ratings_df.MovieID.values.max(), 1)[0]
        print(index, '--------------', current_user)
        # otherwise save a new review
        review = Review()
        review.wine = wine = get_object_or_404(Wine, pk=index)
        review.user_id = current_user
        review.user_name = User.objects.get(id=current_user).username
        review.rating = 0
        review.comment = ''
        review.pub_date = datetime.datetime.now()
        review.save()
        error = 'Please rate the movie added in your reviews to ameliorate/improve your recommendations.'
        current_user = Fake.objects.get(actual_id=current_user).fake_id
        temp = pd.DataFrame({'UserID': [current_user], 'MovieID': [index], 'Rating': [0]})
        #temp = pd.DataFrame([user_id, index, 0])
        ratings_df = ratings_df.append(temp)

    if not add_init_review:
        current_user = Fake.objects.get(actual_id=current_user).fake_id
    Ratings = ratings_df.pivot_table(values = 'Rating', index = 'UserID', columns ='MovieID').fillna(0)

    # Normalizing the data and convert into a numpy array
    R_new = Ratings.as_matrix()
    R = R_new

    # just to verify rows * columns
    print(R.shape)

    mean_of_user_ratings = np.mean(R, axis = 1)
    R_norm = R - mean_of_user_ratings.reshape(-1, 1)

    #Importing the Single Value Decompositon svds
    from scipy.sparse.linalg import svds
    U, sigma, Vt = svds(R_norm, k = 20)
    """
    Vt represents how relevant is each feature to the movie.
    U represents how much the user like each feature
    sigma represents the weights of these features.
    k represents the no. of latency factors to be considered
    """
    #Converting to diagonal matrix
    sigma = np.diag(sigma)

    #Making Recommendations
    all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + mean_of_user_ratings.reshape(-1, 1)
    make_predictions_now = pd.DataFrame(all_user_predicted_ratings, columns = Ratings.columns)

    # the movies detail table 
    movies_df = pd.DataFrame(
        list(Wine.objects.values_list('id', 'name', 'genres')), 
        columns=['MovieID', 'movie title', 'genres'])

    # print(movies_df.head())

    #The function is called on the user with the necessary arguments    
    #print(current_user)

    predictions = recommend_movies(
        make_predictions_now,
        # id of the current user
        current_user, 
        movies_df, 
        ratings_df, 
        10
        )

    #The predicted movies
    #print(predictions.head())

    return [error, predictions]