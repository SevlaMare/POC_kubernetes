import io
from PIL import Image


def image_resize(image_data, width=100, height=100):
    """given a image, will generate a png thumb"""
    try:
        img = Image.open(io.BytesIO(image_data))

        # Resize the image using Nearest Neighbor algorithm
        img_resized = img.resize((width, height), resample=Image.NEAREST)

        buffer = io.BytesIO()
        img_resized.save(buffer, format='PNG', transparency=0)
        resized_image_data = buffer.getvalue()
        return resized_image_data
    except Exception as err:
        error_msg = f"Failed to resize image: {err}"
        raise RuntimeError(error_msg) from err
