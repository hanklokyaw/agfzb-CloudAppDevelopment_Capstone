from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from .models import CarMake, CarModel, CarDealer, DealerReview
from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf, get_dealer_reviews_from_cf, post_request, get_dealer_cars, get_car_by_id
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
# ...
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contactus.html', context)


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
# def get_dealerships(request):
#     context = {}
#     if request.method == "GET":
#         return render(request, 'djangoapp/index.html', context)
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://25b5ddb1.au-syd.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        # dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = get_dealers_from_cf(url)
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)
        # return HttpResponse(dealer_names)

def get_dealerships_by_id(request):
    if request.method == "GET":
        url = "https://25b5ddb1.au-syd.apigw.appdomain.cloud/api/dealership?id="
        # Get dealers from the URL
        dealerships = get_dealer_by_id_from_cf(url, 4)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)

def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://25b5ddb1.au-syd.apigw.appdomain.cloud/api/review"
        # Get reviews from the URL
        context["reviews"] = get_dealer_reviews_from_cf(url, dealer_id)
        context["dealer_id"] = dealer_id
        # reviews = get_dealer_reviews_from_cf(url, dealer_id)
        # reviews_comments = ' '.join([review.review for review in reviews])
        # TODO issues with 404 not found when calling ibm nlu
        # print('about to print reviews')
        # reviews_sentiments = ' '.join([review.sentiment for review in reviews])
        # return HttpResponse(reviews_comments)
        # print('about to print review sentiments')
        # print(reviews_sentiments)
        # return HttpResponse(reviews_sentiments)
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
@csrf_exempt
def add_review(request, dealer_id):
    context = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            url = "https://25b5ddb1.au-syd.apigw.appdomain.cloud/api/review"
            review = dict()
            review["time"] = datetime.utcnow().isoformat()
            review["id"] = dealer_id
            review["review"] = request.POST["content"]
            review["name"] = request.user.username
            if request.POST["purchasecheck"] == "on":
                review["purchase"] = True
            carId = request.POST["car"]
            cars = get_car_by_id(carId)
            for car in cars:
                review["car_make"] = car.name
                review["car_model"] = car.carMake.name
                review["car_year"] = car.year.year
            json_payload = dict()
            json_payload["review"] = review
            post_request(url, json_payload, dealerId=dealer_id)

            context["dealer_id"] = dealer_id
            context["reviews"] = get_dealer_reviews_from_cf(url, dealer_id)
            return render(request, 'djangoapp/dealer_details.html', context)
            #redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            # if not auth, return to login page again
            return render(request, 'djangoapp/login.html', context)
    elif request.method == "GET":
        # query cars
        context["dealer_id"] = dealer_id
        context["cars"] = get_dealer_cars(dealer_id)
        print(context)
        return render(request, 'djangoapp/add_review.html', context)