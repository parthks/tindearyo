import requests


import datetime
from time import time


from geopy.geocoders import Nominatim

TOKEN = "c6f7b8ba-6edb-4318-b57d-ad2eef3d468e"
TINDER_URL = "https://api.gotinder.com"
geolocator = Nominatim(user_agent="auto-tinder")



class tinderAPI():

    def __init__(self):
        self._token = TOKEN
        self.headers = {
            'User-Agent': '',
            "X-Auth-Token": self._token
        }

    def profile(self):
        data = requests.get(TINDER_URL + "/v2/profile?include=account%2Cuser", headers=self.headers).json()
        return Profile(data["data"], self)

    def matches(self, limit=10):
        data = requests.get(TINDER_URL + f"/v2/matches?count={limit}", headers=self.headers).json()
        return list(map(lambda match: Person(match["person"], self), data["data"]["matches"]))

    def like(self, user_id):
        data = requests.get(TINDER_URL + f"/like/{user_id}", headers=self.headers).json()
        return {
            "is_match": data["match"],
            "liked_remaining": data["likes_remaining"]
        }

    def dislike(self, user_id):
        requests.get(TINDER_URL + f"/pass/{user_id}", headers=self.headers).json()
        return True

    def nearby_persons(self):
        data = requests.get(TINDER_URL + "/v2/recs/core", headers=self.headers).json()
        return list(map(lambda user: Person(user, self), data["data"]["results"]))



class Person(object):

    def __init__(self, user, api):

        data = user["user"]
        if (user.get("experiment_info", False)):
            data["experiment_info"] = user["experiment_info"]

        self._api = api
        self.data = data

        self.id = data["_id"]
        self.name = data.get("name", "Unknown")

        self.bio = data.get("bio", "")
        self.distance = data.get("distance_mi", 0) / 1.60934

        self.birth_date = datetime.datetime.strptime(data["birth_date"], '%Y-%m-%dT%H:%M:%S.%fZ') if data.get(
            "birth_date", False) else None
        self.gender = ["Male", "Female", "Unknown"][data.get("gender", 2)]

        self.images = list(map(lambda photo: photo["url"], data.get("photos", [])))

        self.jobs = list(
            map(lambda job: {"title": job.get("title", {}).get("name"), "company": job.get("company", {}).get("name")}, data.get("jobs", [])))
        self.schools = list(map(lambda school: school["name"], data.get("schools", [])))

        if data.get("pos", False):
            self.location = geolocator.reverse(f'{data["pos"]["lat"]}, {data["pos"]["lon"]}')

        if (data.get("experiment_info", False) and 
            data["experiment_info"].get("user_interests", False) and
            data["experiment_info"]["user_interests"].get("selected_interests", False)):
            interests = data["experiment_info"]["user_interests"]["selected_interests"]
            self.interests = list(map(lambda d: d.get("name", ''), interests))


    def __repr__(self):
        return f"{self.id}  -  {self.name} ({self.birth_date.strftime('%d.%m.%Y')})"


    def like(self):
        return self._api.like(self.id)

    def dislike(self):
        return self._api.dislike(self.id)




class Profile(Person):

    def __init__(self, data, api):

        super().__init__(data["user"], api)

        self.email = data["account"].get("email")
        self.phone_number = data["account"].get("account_phone_number")

        self.age_min = data["user"]["age_filter_min"]
        self.age_max = data["user"]["age_filter_max"]

        self.max_distance = data["user"]["distance_filter"]
        self.gender_filter = ["Male", "Female"][data["user"]["gender_filter"]]
