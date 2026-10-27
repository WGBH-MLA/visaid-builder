from typing import Any


def map_keys(catout_table:list) -> tuple[dict[Any, Any], set[Any], set[Any]]:
    facet_map = {}
    name_facets = set()
    catear_facets = set()
    for i in range(len(catout_table)):
        row = catout_table[i]['etd_data']
        if "chyron_data" in row and "name_normalized" in row["chyron_data"]:
            name = row["chyron_data"]["name_normalized"] + ',n'
            if name in facet_map:
                facet_map[name].append(i)
            else:
                name_facets.add(name)
                facet_map[name] = [i]
        if "catear_data" in row:
            for catear in row["catear_data"]:
                if catear != '_problems' and catear != '_alerts':
                    key = catear + ',' + row["catear_data"][catear] + ',c'
                    if key in facet_map:
                        facet_map[key].append(i)
                    else:
                        catear_facets.add(key)
                        facet_map[key] = [i]
    return facet_map, name_facets, catear_facets