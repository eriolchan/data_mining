import sys
import math
import codecs

users = {"Angelica": {"Blues Traveler": 3.5, "Broken Bells": 2.0,
                      "Norah Jones": 4.5, "Phonenix": 5.0,
                      "Slightly Stoopid": 1.5,
                      "The Strokes": 2.5, "Vampire Weekend": 2.0},
         "Bill": {"Blues Traveler": 2.0, "Broken Bells": 3.5,
                  "Deadmau5": 4.0, "Phonenix": 2.0,
                  "Slightly Stoopid": 3.5, "Vampire Weekend": 3.0},
         "Chan": {"Blues Traveler": 5.0, "Broken Bells": 1.0,
                  "Deadmau5": 1.0, "Norah Jones": 3.0, "Phonenix": 5.0,
                  "Slightly Stoopid": 1.0},
         "Dan": {"Blues Traveler": 3.0, "Broken Bells": 4.0,
                 "Deadmau5": 4.5, "Phonenix": 3.0,
                 "Slightly Stoopid": 4.5, "The Strokes": 4.0,
                 "Vampire Weekend": 2.0},
         "Hailey": {"Broken Bells": 4.0, "Deadmau5": 1.0,
                    "Norah Jones": 4.0, "The Strokes": 4.0,
                    "Vampire Weekend": 1.0},
         "Jordyn": {"Broken Bells": 4.5, "Deadmau5": 4.0,
                    "Norah Jones": 5.0, "Phonenix": 5.0,
                    "Slightly Stoopid": 4.5, "The Strokes": 4.0,
                    "Vampire Weekend": 4.0},
         "Sam": {"Blues Traveler": 5.0, "Broken Bells": 2.0,
                 "Norah Jones": 3.0, "Phonenix": 5.0,
                 "Slightly Stoopid": 4.0, "The Strokes": 5.0},
         "Veronica": {"Blues Traveler": 3.0, "Norah Jones": 5.0,
                      "Phonenix": 4.0, "Slightly Stoopid": 2.5,
                      "The Strokes": 3.0}
        }


class recommender:
  def __init__(self, data, k=1, metric='pearson', n=5):
    """Initialize recommender
    currently, if data is dictionary the recommender is initialized
    to it.
    For all other data types of data, no initialization occurs.
    k is the k value for k nearest neighbor
    metric is which distance formula to use
    n is the maximum number of recommendations to make"""
    self.k = k
    self.n = n
    self.username2id = {}
    self.userid2name = {}
    self.productid2name = {}
    # for some reason I want to save the name of the metric
    self.metric = metric
    if self.metric == 'pearson':
      self.fn = self.pearson
    elif self.metric == 'manhattan':
      self.fn = self.manhattan
    elif self.metric == 'euclidean':
      self.fn = self.euclidean
    else:
      self.fn = self.cosine

    # if data is dictionary, set recommender data to it
    if type(data).__name__ == 'dict':
      self.data = data


  def convert_productid2name(self, id):
    """Given product id number, return product name"""
    if id in self.productid2name:
      return self.productid2name[id]
    else:
      return id


  def user_ratings(self, id, n):
    """Return n top ratings for user with id"""
    print "Ratings for " + self.userid2name[id]
    ratings = self.data[id]
    print len(ratings)
    ratings = [(self.convert_productid2name(k), v)
        for (k, v) in ratings.items()]
    # finally sort and return
    ratings = sorted(ratings, key=lambda artistTuple: artistTuple[1],
        reverse=True)
    for rating in ratings[:n]:
      print "%s\t%i" % (rating[0], rating[1])


  def load_book_db(self, path=''):
    """Load the BX book dataset. Path is where the BX files are
    located"""
    self.data = {}
    i = 0
    # first load book ratings into self.data
    f = codecs.open(path + "BX-Book-Ratings.csv", 'r', 'utf8')
    for line in f:
      i += 1
      # separate line into fields
      fields = line.strip().split(';')
      user = fields[0].strip('"')
      book = fields[1].strip('"')
      rating = int(fields[2].strip('"'))
      if user in self.data:
        current_ratings = self.data[user]
      else:
        current_ratings = {}
      current_ratings[book] = rating
      self.data[user] = current_ratings
    f.close()

    # now load books into self.productid2name
    # books contains isbn, title, and author among other fields
    f = codecs.open(path + "BX-Books.csv", 'r', 'utf8')
    for line in f:
      i += 1
      # separate line into fields
      fields = line.strip().split(';')
      isbn = fields[0].strip('"')
      title = fields[1].strip('"')
      author = fields[2].strip('"')
      title = title + ' by ' + author
      self.productid2name[isbn] = title
    f.close()

    # now load user infor into both self.userid2name and
    # self.username2id
    f = codecs.open(path + "BX-Users.csv", 'r', 'utf8')
    for line in f:
      i += 1
      # separate line into fields
      fields = line.strip().split(';')
      userid = fields[0].strip('"')
      location = fields[1].strip('"')
      if len(fields) > 2:
        age = fields[2].strip('"')
      else:
        age = 'NULL'
      if age != 'NULL':
        value = location + ' (age: ' + age + ')'
      else:
        value = location
      self.userid2name[userid] = value
      self.username2id[location] = userid
    f.close()
    print i


  def load_movie_db(self, path=''):
    """Load movie rating dataset"""
    self.data = {}
    is_first_line = True
    names = []
    # read the file
    f = open(path + 'Movie_Ratings.csv', 'r')
    for line in f:
      fields = line.strip().split(',')
      if is_first_line:
        for name in fields[1:]:
          name = name.strip('"')
          names.append(name)
          self.data[name] = {}
        is_first_line = False
      else:
        movie = fields[0].strip('"')
        i = 0
        for rating in fields[1:]:
          if rating == '':
            rating = 0
          else:
            rating = int(rating)
          user_ratings = self.data[names[i]]
          user_ratings[movie] = rating
          i += 1


  def pearson(self, rating1, rating2):
    sum_xy = 0
    sum_x = 0
    sum_y = 0
    sum_x2 = 0
    sum_y2 = 0
    n = 0
    for key in rating1:
      if key in rating2:
        n += 1
        x = rating1[key]
        y = rating2[key]
        sum_xy += x * y
        sum_x += x
        sum_y += y
        sum_x2 += pow(x, 2)
        sum_y2 += pow(y, 2)
    # if no ratings in common, return 0
    if n == 0:
      return 0
    # now compute denominator
    denominator = math.sqrt(sum_x2 - pow(sum_x, 2) / n) * math.sqrt(sum_y2 - pow(sum_y, 2) / n)
    if denominator == 0:
      return 0
    else:
      return (sum_xy - (sum_x * sum_y) / n) / denominator


  def minkowski(self, rating1, rating2, r):
    """Computes the Minkowski distance. Both rating1 and rating2 are
    dictionaries of the form
    {'The Strokes': 3.0, 'Slightly Stoopid': 2.5 ..."""
    distance = 0
    common_ratings = False
    for key in rating1:
      if key in rating2:
        distance += pow(abs(rating1[key] - rating2[key]), r)
        common_ratings = True
    if common_ratings:
      return pow(distance, 1/r)
    else:
      return -1 # Indicates no ratings in common


  def manhattan(self, rating1, rating2):
    return self.minkowski(rating1, rating2, 1)


  def euclidean(self, rating1, rating2):
    return self.minkowski(rating1, rating2, 2)


  def cosine(self, rating1, rating2):
    if len(rating1) != len(rating2):
      sys.stderr.write('user ratings should have some dimension')
      sys.exit(1)

    sum_xy = 0
    sum_x2 = 0
    sum_y2 = 0
    for key in rating1:
      x = rating1[key]
      y = rating2[key]
      sum_xy += x * y
      sum_x2 += pow(x, 2)
      sum_y2 += pow(y, 2)
    # compute the denominator
    denominator = math.sqrt(sum_x2) * math.sqrt(sum_y2)
    if denominator == 0:
      return 0
    else:
      return sum_xy / denominator


  def compute_nearest_neighbor(self, username):
    """Creates a sorted list of users based on their distance to
    username"""
    distances = []
    for instance in self.data:
      if instance != username:
        distance = self.fn(self.data[username], self.data[instance])
        distances.append((instance, distance))
    # sort based on distance -- closest first
    return sorted(distances, key=lambda artistTuple: artistTuple[1],
        reverse=True)


  def recommend(self, user):
    """Give list of recommendations"""
    recommendations = {}
    # first get list of users, ordered by nearness
    nearest = self.compute_nearest_neighbor(user)
    # now get the ratings for the user
    user_ratings = self.data[user]
    # determine the total distance
    total_distance = 0.0
    for i in range(self.k):
      total_distance += nearest[i][1]
    # now iterate through the k nearest neighbors
    # accumulating their ratings
    for i in  range(self.k):
      # compute slice of pie
      weight = nearest[i][1] / total_distance
      # get the name of the person
      name = nearest[i][0]
      # get the ratings for this person
      neighbor_ratings = self.data[name]
      # now find bands neighbor rated that user didn't
      for artist in neighbor_ratings:
        if not artist in user_ratings or not user_ratings[artist]:
          if not artist in recommendations:
            recommendations[artist] = neighbor_ratings[artist] * weight
          else:
            recommendations[artist] = recommendations[artist] + neighbor_ratings[artist] * weight
    # now make list from dictionary
    recommendations = [(self.convert_productid2name(k), v)
        for (k, v) in recommendations.items()]
    # finally sort and return
    recommendations = sorted(recommendations, key=lambda artistTuple: artistTuple[1], reverse=True)
    # return the first n items
    return recommendations[:self.n]


# test
r = recommender(users, 2, 'pearson')
print r.recommend('Hailey')
r = recommender(users, 2, 'manhattan')
print r.recommend('Hailey')
r = recommender(users, 2, 'euclidean')
print r.recommend('Hailey')
#r = recommender(users, 3)
#r.load_book_db('data/')
#print r.recommend('171118')
#r.user_ratings('171118', 5)
#r = recommender(users, 3, 'cosine')
#r.load_movie_db('data/')
#print r.recommend('Matt')
