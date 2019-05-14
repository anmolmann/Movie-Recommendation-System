# Movie Recommendation System

Deployed a Movie Recommendation System using aws, Django, python &amp; Machine Learning algorithms such as Collaborative Filtering Algorithms (using Matrix Factorization and Neural Networks).

The purpose was to evaluate how an existing algorithm in a movie recommender system predicts movie ratings and get an indication of how the users perceive the recommendations given by the system.
The recommendations can be computed with a Low Rank Matrix Factorization (also called as SVD) algorithm that calculates both the user and movies latent features to predict ratings.
Secondly, the recommendations are also computed with a revised Collaborative Filtering algorithm which makes use of Neural Networks.

### Technology Used

- Front End Programming Tool:
	- HTML, CSS, Bootstrap, jQuery, Django Template language
- Back End Programming
	- Django Web Framework, Python version 3.6
- Database
	- Sqlite, which is the default db used by Django
- Machine Learning Packages for Recommendation Algorithms
	- Scipy, for MF (Matrix Factorization)/SVD Algorithm
	- Keras for NCF (Neural Collaborative Filtering) Algorithm

### Dataset Used for the Project

- Movielens dataset
- collected by the GroupLens Research Project at the University of Minnesota.
- This data set consists of:
	- 100,000 ratings (1-5) from 943 users on 1682 movies. 
	- Each user has rated at least 20 movies. 
	- Simple demographic info for the users (age, gender, occupation, zip)

### Installation Guidelines

- Install Python version 3.6 from python's official site for Windows.
- Install Django
- Install all the Machine Learning pacages and tools, which are as follows: Tensorflow, Keras and scipy.
- Install Django Bootstrap for front-end programming purpose.

- To install all the packages once, use this command:
	- `python install -r requirement.txt`

### Usage Guidelines

- cd "Project Code"; Enter into the project diretory, first.
*load the data into the database first using the code provided in load_*.py files. or just use the db file provided at this [link](https://drive.google.com/open?id=1bTo6NfP9H6KP0BRHDc-UsPK0h7gLxM9C)*
- Then, run this command to run the project:
	- `python manage.py runserver`; by default the code will run on port 8000.
	- If you want to change the port; run this command: `python manage.py runserver 0.0.0.0:Port_number_on_which_you want_to_run`.
	- Also, The model.h5 file provided [here](https://drive.google.com/open?id=1bTo6NfP9H6KP0BRHDc-UsPK0h7gLxM9C) should be download prior.

- Demo has been provided at this url: 
	- http://movie-recommender-dev.us-west-2.elasticbeanstalk.com/

### Author

Anmol Mann, mann.anmol15@gmail.com
