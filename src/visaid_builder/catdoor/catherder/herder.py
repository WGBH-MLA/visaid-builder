import json
from pathlib import Path

from .image_writer import write_image
from .html_constructor import html_file
from .key_collector import map_keys


def herd_cats(catout_table:list, image_dir:str, output_path:str) -> None:

    directory = Path(image_dir)
    directory.mkdir(parents=True, exist_ok=True)
    html = html_file()
    html.writeFields()
    for frame in catout_table:
        # 24 of the characters(in the image bs64) are always a data-heading,
        # and need to be stripped for the save to work correctly
        write_image(f'./{image_dir}/'+frame['img_fname'], frame['img_data_uri'][23:])
        html.addRow(frame, f'./{image_dir}/'+frame['img_fname'])
        row = frame['etd_data']
        #TODO this needs to add cataloger and date and probably some other stuff too

    facet_map = map_keys(catout_table)
    with open(image_dir+'/facet_map.json', 'w') as f:
        json.dump(facet_map, f)
        print(f"wrote facet_map to {image_dir}/facet_map.json")
        f.close()
    with open(image_dir+'/catout_table.json', 'w') as f:
        json.dump(catout_table, f)
        print(f"wrote catout_table to {image_dir}/catout_table.json")
        f.close()
    html.write_html(output_path)

