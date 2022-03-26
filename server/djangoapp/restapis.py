import requests
import json
# import related models here
from .models import CarDealer, DealerReview, CarModel
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    api_key = None
    try:
        api_key = kwargs["api_key"]
    except:
        print("nlu api key not passed")
    response = {}
    try:
        # Call get method of requests library with URL and parameters

        if api_key:
            # nlu request
            print('about to call nlu with api_key' + api_key)
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            # no authentication GET
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST from {} ".format(url))
    result = requests.post(url, params=kwargs, json=json_payload)
    return result

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        body = json_result["body"]
        # For each dealer object
        for dealer in body["docs"]:
            # Get its content in `doc` object
            # dealer_doc = dealer["docs"]
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
            
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_by_id_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        body = json_result["body"]
        # For each dealer object
        for dealer in body["docs"]:
            # Get its content in `doc` object
            # dealer_doc = dealer["docs"]
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            if (dealer_doc["id"] == dealerId):
                results.append(dealer_obj)
            
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview):
    # NLU api url/key
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/4651b5cd-97f0-4feb-bbd3-6428a40e2724"
    api_key = "TAG05-_yHleAA6AJIMLB0BmJ-KApGlk2wEhPIFEl9LXA"

    # Call get_request with a URL parameter
    params = dict()
    params["api_key"] = api_key
    # params["text"] = kwargs["text"]
    # params["version"] = kwargs["version"]
    # params["features"] = kwargs["features"]
    # params["return_analyzed_text"] = kwargs["return_analyzed_text"]
    # response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
      #                              auth=HTTPBasicAuth('apikey', api_key))

    response = get_request(url, **params)
    return response

def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    
    # api_key = "TAG05-_yHleAA6AJIMLB0BmJ-KApGlk2wEhPIFEl9LXA"
    # # Call get_request with a URL parameter
    # if api_key:
    #     # Basic authentication GET
    #     json_result = request.get(url, dealerId=dealer_id, auth=HTTPBasicAuth('apikey', api_key))
    # else:
    #     # no authentication GET
    #     json_result = request.get(url, dealerId=dealer_id)
    json_result = get_request(url, dealerId=dealer_id)
    if json_result:
        # Get the row list in JSON as dealers
        body = json_result.get("body")
        # For each dealer object
        if body:
            for review in body.get("reviews"):
                # Get its content in `doc` object
                # dealer_doc = dealer["docs"]
                dealer_doc = review
                nluAnalyzedReview = analyze_review_sentiments(dealer_doc.get("review",""))
                print('nluAnalyzedReview is: ')
                print(nluAnalyzedReview)
                # Create a DealerReview object with values in `doc` object
                dealer_obj = DealerReview(
                    dealership=dealer_doc.get("dealership",""), 
                    name=dealer_doc.get("name",""),
                    purchase=dealer_doc.get("purchase",""),
                    id=dealer_doc.get("id",""),
                    review=dealer_doc.get("review",""), 
                    purchase_date=dealer_doc.get("purchase_date",""),
                    car_make=dealer_doc.get("car_make",""),
                    car_model=dealer_doc.get("car_model",""),
                    car_year=dealer_doc.get("car_year",""),
                    sentiment=nluAnalyzedReview
                )
                # if (dealer_doc["id"] == dealer_id):
                results.append(dealer_obj)
            
    return results

def get_dealer_cars(dealer_id):
    return CarModel.objects.filter(dealerId=dealer_id)

def get_car_by_id(id):
    return CarModel.objects.filter(id=id)