from typing import Any


def map_keys(catout_table:list) -> tuple[dict[Any, Any], dict[Any, Any]]:
    facet_map = {}
    facets = {'catears': [], "name_normalized" : [], "cataloger": []}
    for i in range(len(catout_table)):
        row = catout_table[i]['etd_data']
        if "chyron_data" in row and "name_normalized" in row["chyron_data"]:
            name = row["chyron_data"]["name_normalized"] + ',n'
            if name in facet_map:
                facet_map[name].append(i)
            else:
                facets['name_normalized'].append(name)
                facet_map[name] = [i]
        if "cataloger" in catout_table[i]:
            name = catout_table[i]["cataloger"] + ',l'
            if name in facet_map:
                facet_map[name].append(i)
            else:
                facet_map[name] = [i]
                facets['cataloger'].append(name)
        if "catear_data" in row:
            for catear in row["catear_data"]:
                if catear != '_problems' and catear != '_alerts':
                    key = catear + ',' + row["catear_data"][catear] + ',c'
                    if key in facet_map:
                        facet_map[key].append(i)
                    else:
                        facets['catears'].append(key)
                        facet_map[key] = [i]
    return facet_map, facets