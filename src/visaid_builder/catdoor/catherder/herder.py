from pathlib import Path

from .image_writer import write_image
from .html_constructor import html_file
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
    html.write_html(output_path)

