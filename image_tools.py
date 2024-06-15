from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def get_image_from_bytes(b):
    """
    Gets the PIL.Image object from the bytes of photo
    :param b: Bytes of the photo
    :type b: bytes
    """
    stream = BytesIO(b)
    image = Image.open(stream).convert("RGBA")
    stream.close()
    return image


def crop_center(pil_img: Image, crop_width: int, crop_height: int) -> Image:
    """
    Функция для обрезки изображения по центру.
    """
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def format_to_3x4(pil_img: Image) -> Image:
    """
        Функция для преобразования картинки в формат 3x4
    """
    img_width, img_height = pil_img.size
    if img_width < img_height:
        return crop_center(pil_img, img_width, min(img_height, img_width * 4 // 3))
    else:
        return crop_center(pil_img, min(img_width, img_height * 3 // 4), img_height)


def resize_image(pil_img_1: Image, pil_img_2: Image) -> (Image, Image):
    img_width_1, img_height_1 = pil_img_1.size
    img_width_2, img_height_2 = pil_img_2.size
    img_width = min(img_width_1, img_width_2)
    pil_img_1 = pil_img_1.resize((img_width, img_height_1 * img_width // img_width_1))
    pil_img_2 = pil_img_2.resize((img_width, img_height_2 * img_width // img_width_2))
    return pil_img_1, pil_img_2


def get_bytes_from_image(image):
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


'''
def string_transformer(data, max_symbols):
    answer = ""
    for string in data.split('\n'):
        start = 0
        pos = -1
        while string.find(' ', pos + 1) != -1:
            if string.find(' ', pos + 1) - start + 1 > max_symbols:
                if not string[start:pos + 1]:
                    pos = string.find(' ', pos + 1)
                answer += string[start:pos + 1] + '\n'
                start = pos + 1
            pos = string.find(' ', pos + 1)
            if pos == -1:
                break
        answer += string[start:] + '\n'
    return answer
'''


def string_transformer(data, max_symbols):
    return data[:max_symbols]


def create_image(data):
    photo_before_ = get_image_from_bytes(data['photo_before'])
    photo_after_ = get_image_from_bytes(data['photo_after'])
    photo_before_ = format_to_3x4(photo_before_)
    photo_after_ = format_to_3x4(photo_after_)
    photo_before_, photo_after_ = resize_image(photo_before_, photo_after_)

    escape = 15  # между фотками
    size = 43  # Размер остального текста
    size2 = 53  # Размер заголовка
    st = 15  # Между краями и фотками
    max_symbols_a = 40  # Максимальное количество символов в заголовке
    max_symbols_b = 25  # Максимальное количество символов в подписи

    width = 2 * st + photo_before_.size[0] + photo_after_.size[0] + escape

    data['text_after'] = string_transformer(data['text_after'], max_symbols_b)
    data['text_before'] = string_transformer(data['text_before'], max_symbols_b)
    data['all_text'] = string_transformer(data['all_text'], max_symbols_a)

    cnt = (data['all_text'].count('\n') + 1)
    new_image = Image.new('RGB',
                          (width,
                           2 * st + max(photo_after_.size[1], photo_before_.size[1]) + cnt * size2 + st +
                           max(size * (data['text_before'].count('\n') + 1),
                               size * (data['text_after'].count('\n') + 1))),
                          (250, 250, 250))

    center = max(photo_after_.size[1], photo_before_.size[1]) // 2

    x_before_image = st
    y_before_image = st + cnt * size2 + st + center - photo_before_.size[1] // 2
    new_image.paste(photo_before_, (x_before_image, y_before_image))

    x_after_image = st + photo_before_.size[0] + escape
    y_after_image = st + cnt * size2 + st + center - photo_after_.size[1] // 2
    new_image.paste(photo_after_, (x_after_image, y_after_image))

    draw_text = ImageDraw.Draw(new_image)
    font = ImageFont.truetype('arial.ttf', size=size)
    font2 = ImageFont.truetype('arial.ttf', size=size2)

    bbefore = draw_text.multiline_textbbox((0, 0), data['text_before'], font=font)
    bafter = draw_text.multiline_textbbox((0, 0), data['text_after'], font=font)

    x_before = x_before_image + photo_before_.size[0] // 2 - bbefore[2] // 2
    x_after = x_after_image + photo_after_.size[0] // 2 - bafter[2] // 2

    y_before = photo_before_.size[1] + y_before_image + st
    y_after = y_after_image + photo_after_.size[1] + st
    y_after = y_before = max(y_before, y_after)
    # center = max(bbefore[3] // 2, bafter[3] // 2)
    # y_after += center - bafter[3] // 2
    # y_before += center - bbefore[3] // 2

    draw_text.rectangle(draw_text.textbbox((x_before, y_before), text=data['text_before'], font=font), 'white',
                        outline=(255, 255, 255))
    draw_text.text(
        (x_before, y_before-10),
        data['text_before'],
        align='center',
        fill=('#1C0606'),
        font=font
    )

    draw_text.rectangle(draw_text.textbbox((x_after, y_after), text=data['text_after'], font=font), 'white',
                        outline=(255, 255, 255))
    draw_text.text(
        (x_after, y_after-10),
        data['text_after'],
        align='center',
        fill=('#1C0606'),
        font=font
    )

    draw_text.text(
        (new_image.size[0] // 2 - draw_text.textbbox((0, 0), data['all_text'], font=font2)[2] // 2, 15),
        data['all_text'],
        align='center',
        fill=('#1C0606'),
        font=font2,
    )
    return new_image
