import json
from pathlib import Path

from .image_writer import write_image
from .html_constructor import html_file
from .key_collector import map_keys


def herd_cats(catout_table:list, image_dir:str, output_path:str) -> None:
    data_json = []
    directory = Path(image_dir)
    directory.mkdir(parents=True, exist_ok=True)
    html = html_file(image_dir)
    for frame in catout_table:
        # 24 of the characters(in the image bs64) are always a data-heading,
        # and need to be stripped for the save to work correctly
        write_image(f'./{image_dir}/'+frame['img_fname'], frame['img_data_uri'][23:])
        row = {}
        row['img_path'] = f'./{image_dir}/'+frame['img_fname']
        row['etd_data'] = frame['etd_data']
        data_json.append(row)

    facet_map, name_facets, catear_facets = map_keys(catout_table)

    for facet in name_facets:
        html.addNameFacet(facet)
    for facet in catear_facets:
        html.addCatearsFacet(facet)
    with open(image_dir+'/facet_map.js', 'w') as f:
        f.write('const facet_map = ')
        json.dump(facet_map, f)
        f.write(';')
        print(f"wrote facet_map to {image_dir}/facet_map.js")
        f.close()
    with open(image_dir+'/catout_table.js', 'w') as f:
        f.write('const data = ')
        json.dump(data_json, f)
        f.write(';')
        print(f"wrote catout_table to {image_dir}/catout_table.js")
        f.close()
    html.write_html(output_path)

