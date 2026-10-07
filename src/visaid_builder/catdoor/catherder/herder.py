from pathlib import Path

from .image_writer import write_image


def herd_cats(catout_table, image_dir, output_path):
    directory = Path(image_dir)
    directory.mkdir(parents=True, exist_ok=True)
    for frame in catout_table:
        # 24 of the characters are always a data-heading, and need to be stripped
        write_image(f'./{image_dir}/'+frame['img_fname'], frame['img_data_uri'][23:])


