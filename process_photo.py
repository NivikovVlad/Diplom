import os
from pprint import pprint
from PIL import Image, ImageFont, ImageDraw, ImageOps
from PIL.Image import Resampling


types_text = {
    'friend_is': ['Friendship is ...', 'Дружба это ...', 'icons/friendship.png'],
    'love_is': ['Love is ...', 'Любовь это ...', 'icons/love.png']
}


def set_new_image(photo_id, img_description, img_type):

    img_path = f'UserFiles/Photos/{photo_id}.jpg'
    with Image.open(img_path) as im:
        if im.width > im.height:
            im = im.rotate(90, expand=True)
        plus_width = im.width // 100 * 3
        plus_height = im.height // 100 * 20
        im = ImageOps.fit(im, (987, 1520), method=Resampling.BICUBIC, bleed=0.0, centering=(0.5, 0.5))

        new_image = Image.new(mode="RGB", size=[im.width+plus_width, im.height+plus_height], color=(235, 215, 205))

        new_image.paste(im, (plus_width//2, plus_height//2))

        icon_img = Image.open(types_text[img_type][2])
        icon_img = icon_img.resize((plus_height // 2, plus_height // 2))
        new_image.paste(icon_img, (new_image.width - icon_img.width - plus_width // 2, 0))

        text_size = plus_height // 4
        font1 = ImageFont.truetype("./Fonts/ArkanaScriptRough.ttf", text_size)
        font2 = ImageFont.truetype("./Fonts/Angeme-Regular.ttf", text_size * 0.8)

        drawer = ImageDraw.Draw(new_image)
        drawer.text((plus_width // 2, plus_height // 15),
                    f"{types_text[img_type][0]} ...", font=font1, fill='black')
        drawer.text((plus_width // 2, plus_height // 15 + text_size),
                    f"{types_text[img_type][1]} ...", font=font2, fill='black')

        caption_size = font1.getlength(img_description)
        if caption_size > im.width // 2:
            s = img_description.split()
            cap1 = ''
            cap2 = ''
            s1 = s[0:len(s) // 2 + 1]
            s2 = s[len(s) // 2 + 1:]
            for word in s1:
                cap1 += str(word + ' ')
            for word in s2:
                cap2 += str(word + ' ')

            tab = ''
            font2 = ImageFont.truetype("./Fonts/Angeme-Regular.ttf", text_size // 1.5)
        else:
            cap1 = img_description
            cap2 = ''
            tab = ''
        drawer.text((plus_width // 2, new_image.height - text_size * 1.5),
                    text=cap1 + tab + cap2, font=font2, fill='black')

        new_image.save(f'UserFiles/ResultPhotos/{photo_id}.jpg')
        print(f'Сохраняю: {new_image}')
        # result_images.append(new_image)
        # return result_images


# if __name__ == '__main__':
#     # print(len(captions_for_pictures))
#     # Images = MyImage(images_dir, new_images_dir)
#     # Images.set_new_image()
#     images_list = []
#     test_images_dir = './test_dir/'
#     files = (file for file in os.listdir(new_images_dir) if file.endswith(('.png', '.jpg', '.jpeg', '.JPG')))
#     for file in files:
#         images_list.append(os.path.join(new_images_dir, file))
#     i = 0
#     for img in images_list:
#         with Image.open(img) as imgs:
#             imgs = imgs.rotate(90, expand=True)
#             imgs.save(str(test_images_dir) + str(i) + '.png')
#             i += 1