users = {"Angelica": {"Blues Traveler": 3.5, "Broken Bells": 2.0, "Norah Jones": 4.5, "Phonenix": 5.0, "Slightly Stoopid": 1.5, "The Strokes": 2.5, "Vampire Weekend": 2.0}, "Bill": {"Blues Traveler": 2.0, "Broken Bells": 3.5, "Deadmau5": 4.0, "Phonenix": 2.0, "Slightly Stoopid": 3.5, "Vampire Weekend": 3.0}, "Chan": {"Blues Traveler": 5.0, "Broken Bells": 1.0, "Deadmau5": 1.0, "Norah Jones": 3.0, "Phonenix": 5.0, "Slightly Stoopid": 1.0}, "Dan": {"Blues Traveler": 3.0,
"Broken Bells": 4.0, "Deadmau5": 4.5, "Phonenix": 3.0, "Slightly Stoopid": 4.5, "The Strokes": 4.0, "Vampire Weekend": 2.0}, "Hailey": {"Broken Bells": 4.0, "Deadmau5": 1.0, "Norah Jones": 4.0, "The Strokes": 4.0, "Vampire Weekend": 1.0}, "Jordyn": {"Broken Bells": 4.5, "Deadmau5": 4.0, "Norah Jones": 5.0, "Phonenix": 5.0, "Slightly Stoopid": 4.5, "The Strokes": 4.0, "Vampire Weekend": 4.0}, "Sam": {"Blues Traveler": 5.0, "Broken Bells": 2.0, "Norah Jones": 3.0, "Phonenix": 5.0,
"Slightly Stoopid": 4.0, "The Strokes": 5.0}, "Veronica": {"Blues Traveler": 3.0, "Norah Jones": 5.0, "Phonenix": 4.0,
"Slightly Stoopid": 2.5, "The Strokes": 3.0}}


def minkowski(rating1, rating2, r):
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
    return 0 # Indicates no ratings in common


def compute_nearest_neighbor(username, users):
  """creates a sorted list of users based on their distance to
  username"""
  distances = []
  for user in users:
    if user != username:
      # distance = minkowski(users[user], users[username], 1) -> Manhattan distance
      distance = minkowski(users[user], users[username], 2) # Euclidean distance
      distances.append((distance, user))
  # sort based on distance -- closest first
  return sorted(distances)


def recommend(username, users):
  """Give list of recommendations"""
  # first find nearest neighbor
  nearest = compute_nearest_neighbor(username, users)[0][1]
  recommendations = []
  # now find bands neighbor rated that user didn't
  neighbor_ratings = users[nearest]
  user_ratings = users[username]
  for artist in neighbor_ratings:
    if not artist in user_ratings:
      recommendations.append((artist, neighbor_ratings[artist]))
  # using the fn sorted for variety - sort is more efficient
  return sorted(recommendations, key=lambda artistTuple: artistTuple[1], reverse=True)


# test
print recommend('Chan', users)
