import json
from pathlib import Path

from .image_writer import write_image
from .html_constructor import html_file
from .key_collector import map_keys


def herd_cats(catout_table:list, output_path:str) -> None:
    data_json = []
    if output_path is None:
        output_path = 'catherder'
    directory = Path(output_path)
    directory.mkdir(parents=True, exist_ok=True)
    directory = Path(f'./{output_path}/catpics/')
    directory.mkdir(parents=True, exist_ok=True)
    html = html_file()
    for frame in catout_table:
        # 24 of the characters(in the image bs64) are always a data-heading,
        # and need to be stripped for the save to work correctly
        write_image(f'./{output_path}/catpics/'+frame['img_fname'], frame['img_data_uri'][23:])
        row = {'img_path': f'./catpics/' + frame['img_fname'], 'etd_data': frame['etd_data'], 'cataloger': frame['cataloger']}
        data_json.append(row)
    facet_map, facets = map_keys(catout_table)

    for facet in facets:
        for item in facets[facet]:
            html.addFacet(item, facet)
    # I can't import .json in raw html for 'reasons'. But if the files are 'scripts' that actually
    # just define a object that is what the .json encodes, that's fine. And json is perfectly valid (by definition)
    # object notation in javascript.
    with open(output_path+'/facet_map.js', 'w') as f:
        f.write('const facet_map = ')
        json.dump(facet_map, f)
        f.write(';')
        print(f"wrote facet_map to {output_path}/facet_map.js")
        f.close()
    with open(output_path+'/catout_table.js', 'w') as f:
        f.write('const data = ')
        json.dump(data_json, f)
        f.write(';')
        print(f"wrote catout_table to {output_path}/catout_table.js")
        f.close()
    html.write_html(f'{output_path}/herded_cats.html')

