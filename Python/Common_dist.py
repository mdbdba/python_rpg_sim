from AbilityArray import AbilityArray
from collections import Counter

sum_dist = {}
eighteen_occur_dist = {}
most_popular_occur_dist = {}

for n in range(10000):
    pref_array = [0, 1, 2, 3, 4, 5]
    a1 = AbilityArray(pref_array=pref_array,
                      array_type='Common',
                      debug_ind=1)
    ability_list = a1.get_numerical_sorted_array()
    # print(f'round {n}: {ability_list}')
    list_total = sum(ability_list)
    if list_total in sum_dist:
        sum_dist.update({list_total: (sum_dist[list_total]+1)})
    else:
        sum_dist.update({list_total: 1})

    eighteen_occurs = ability_list.count(18)
    if eighteen_occurs in eighteen_occur_dist:
        eighteen_occur_dist.update({eighteen_occurs: (eighteen_occur_dist[eighteen_occurs]+1)})
    else:
        eighteen_occur_dist.update({eighteen_occurs: 1})

    occurence_count = Counter(ability_list)
    if occurence_count.most_common(1)[0][1] == 1:
        most_popular = -1
    else:
        most_popular = occurence_count.most_common(1)[0][0]

    if most_popular in most_popular_occur_dist:
        most_popular_occur_dist.update({most_popular: (most_popular_occur_dist[most_popular]+1)})
    else:
        most_popular_occur_dist.update({most_popular: 1})

sorted_sum_dist = {}
for key in sorted(sum_dist.keys()):
    sorted_sum_dist[key] = sum_dist[key]

sorted_eighteens = {}
for key in sorted(eighteen_occur_dist.keys()):
    sorted_eighteens[key] = eighteen_occur_dist[key]

sorted_popular = {}
for key in sorted(most_popular_occur_dist.keys()):
    sorted_popular[key] = most_popular_occur_dist[key]

print(f'sum_dist: {sorted_sum_dist}')
print(f'eighteen occur_dist: {sorted_eighteens}')
print(f'most_popular_occur_dist: {sorted_popular}')
# Used this test to peek at the distributions of the random ability stat generator.
# sum_dist: {46: 1, 49: 1, 50: 1, 51: 5, 52: 4, 53: 16, 54: 20, 55: 24, 56: 32, 57: 53, 58: 53, 59: 75, 60: 90, 61: 128,
#            62: 151, 63: 173, 64: 256, 65: 260, 66: 331, 67: 353, 68: 413, 69: 452, 70: 533, 71: 503, 72: 507, 73: 580,
#            74: 545, 75: 542, 76: 512, 77: 524, 78: 472, 79: 426, 80: 363, 81: 339, 82: 271, 83: 239, 84: 202, 85: 157,
#            86: 127, 87: 85, 88: 56, 89: 39, 90: 32, 91: 24, 92: 8, 93: 10, 94: 6, 95: 1, 96: 2, 97: 2, 98: 1}

# eighteen occurs dist: {0: 9078, 1: 892, 2: 29, 3: 1}

# most popular occur dist: {-1: 1819,  5: 8, 6: 27, 7: 67, 8: 168, 9: 312, 10: 636, 11: 948, 12: 1300, 13: 1472,
#                           14: 1377, 15: 1027, 16: 590, 17: 220, 18: 29}
