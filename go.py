import Tinder
import time
import random

import json


api = Tinder.tinderAPI()

f=open("data.txt", "r+")
ALL_DATA = json.load(f)
f.close()

f=open("swipelog.txt", "r+")
SWIPE_LOG = json.load(f)
f.close()


SWIPE_COUNT = len(SWIPE_LOG)
LIKED_COUNT = len(list(filter(lambda x: "LIKE" == list(x.values())[0], SWIPE_LOG)))

print(SWIPE_COUNT, LIKED_COUNT)


INTERESTS = ["Wine", "Craft Beer", "Grab a drink", "House Parties", "Dancing", "Festivals", "Travel", "Spirituality", "Movies"]
KEYWORDS = ["wine", "go out", "party", "beer", "chill", "420", "dance", "dancing", "mango", "cheese", "travel", "explore", "software", "code", "coding", "geek", "ai", "singularity", "artificial intelligence", "edm", "psychedelic", "rave", "festival", "concert", "cabin crew"]

def chillz(data: Tinder.Person):
    if (len(data.images) == 1):
        return False
    
    if (len(data.bio) == 0):
        return False

    if hasattr(data, 'interests'):
        for myInterest in INTERESTS:
            if (myInterest in data.interests):
                print("Intrested in " + myInterest)
                return True
    
    bio = data.bio.lower()
    for keyword in KEYWORDS:
        if (bio.find(keyword) != -1):
            print("Found '"+keyword+"' keyword in bio")
            return True

    return False






def log(data: Tinder.Person, actionTaken):
    global ALL_DATA, SWIPE_LOG

    f=open("swipes.txt", "a+")
    f.write(actionTaken + " - " + data.id + "\n")
    f.write(data.bio + "\n")
    if (hasattr(data, 'interests')):
        f.write(str(data.interests) + "\n")
    f.write("\n")
    f.close()

    
    SWIPE_LOG.append({
        data.id: actionTaken
    })
    f=open("swipelog.txt", "w+")
    json.dump(SWIPE_LOG, f, indent=2)
    f.close()

    
    ALL_DATA[data.id] = data.data
    f=open("data.txt", "w+")
    json.dump(ALL_DATA, f, indent=4)
    f.close()



if __name__ == "__main__":
    
    while True:
        try:
            potentials = api.nearby_persons()
            print("Got", len(potentials))
        except Exception as e:
            print(e)
            t = random.randint(60*30,60*60)
            print("Taking a break...", t)
            time.sleep(t)
            continue


        for girl in potentials:
            if (chillz(girl)):
                api.like(girl.id)
                log(girl, "LIKE")
                LIKED_COUNT += 1
            else:
                api.dislike(girl.id)
                log(girl, "PASS")
            SWIPE_COUNT += 1
            print("Liked", LIKED_COUNT, "/", SWIPE_COUNT)

            time.sleep(random.randint(5,30))




