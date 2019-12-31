
myjson = {
  "staticparameters": {
    "opponent_party_size": "4",
    "debug_ind": "1"
  },
  "seriesparameters": [
    {
      "party_name": "AllStars_3"
    },
    {
      "party_name": "AvgJoes_3"
    } ]
}

for party in myjson["seriesparameters"]:
  print (f"{myjson['staticparameters']}, {party} a whole lot of tea" )
