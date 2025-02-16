"""
    Very inspired by zivezab's django-autograph
    https://github.com/zivezab/django-autograph/blob/master/autograph/utils.py
"""
import json
from itertools import chain
from PIL import Image, ImageDraw, ImageOps, __version__ as PIL_VERSION

AA = 5  # super sampling gor antialiasing


def draw_signature(data, as_file=False):
    """ Draw signature based on lines stored in json_string.
        `data` can be a json object (list in fact) or a json string
        if `as_file` is True, a temp file is returned instead of Image instance
    """

    def _remove_empty_pts(pt):
        return {
            'x': list(filter(lambda n: n is not None, pt['x'])),
            'y': list(filter(lambda n: n is not None, pt['y']))
        }

    if type(data) is str:
        drawing = json.loads(data, object_hook=_remove_empty_pts)
    elif type(data) is list:
        drawing = data
    else:
        raise ValueError

    # Compute box
    min_width = int(round(min(chain(*[d['x'] for d in drawing])))) - 10
    max_width = int(round(max(chain(*[d['x'] for d in drawing])))) + 10
    width = max_width - min_width
    min_height = int(round(min(chain(*[d['y'] for d in drawing])))) - 10
    max_height = int(round(max(chain(*[d['y'] for d in drawing])))) + 10
    height = max_height - min_height

    # Draw image
    im = Image.new("RGBA", (width * AA, height * AA))
    draw = ImageDraw.Draw(im)
    for line in drawing:
        len_line = len(line['x'])
        points = [
            (
                (line['x'][i] - min_width) * AA,
                (line['y'][i] - min_height) * AA
            )
            for i in range(0, len_line)
        ]
        draw.line(points, fill="#000", width=2 * AA)
    im = ImageOps.expand(im)
    # Smart crop
    bbox = im.getbbox()
    if bbox:
        im.crop(bbox)

    old_pil_version = int(PIL_VERSION.split('.')[0]) < 10
    im.thumbnail(
        (width, height),
        Image.ANTIALIAS if old_pil_version  else Image.LANCZOS
    )

    if as_file:
        ret = im._dump(format='PNG')
    else:
        ret = im

    return ret
