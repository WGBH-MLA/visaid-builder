



def map_keys(catout_table:list) -> dict:
    facet_map = {}
    for i in range(len(catout_table)):
        row = catout_table[i]['etd_data']
        if "chyron_data" in row and "name_normalized" in row["chyron_data"]:
            name = row["chyron_data"]["name_normalized"]
            if name in facet_map:
                facet_map[name].append(i)
            else:
                facet_map[name] = [i]
        if "catear_data" in row:
            for catear in row["catear_data"]:
                if catear != '_problems' and catear != '_alerts':
                    key = catear + ',' + row["catear_data"][catear]
                    if key in facet_map:
                        facet_map[key].append(i)
                    else:
                        facet_map[key] = [i]
    return facet_map