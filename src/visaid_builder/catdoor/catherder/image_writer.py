import base64
import io

def write_image(image_fname, bs64_image):
    # just decodes the b64 string to bytes in order to write to file.
    # Has to use wb(write binary) for this
    buf = io.BytesIO()
    buf.write(base64.b64decode(bs64_image))
    with open(image_fname, "wb") as f:
        f.write(buf.getvalue())
        f.close()
        print(f"Wrote image to {image_fname}")