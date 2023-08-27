import os

from PIL import Image, ImageOps



class CustomImage:
    def __init__(self, path, folder="reduced"):
        self.image = ImageOps.exif_transpose(Image.open(path))
        self.width, self.height = self.image.size

        self.path = path

        if folder[0] == "-":
            self.reduced_path = os.path.join(os.path.dirname(self.path) + folder,
                                            os.path.basename(self.path))
        else:
            self.reduced_path = os.path.join(os.path.dirname(self.path),
                                        folder,
                                        os.path.basename(self.path))

    def reduce_image(self, mode="target", ratio=0.5, quality=75, max_size=(1920, 1080), max_ratio=1):
        if max_ratio == 0:
            (W, H) = (self.width, self.height)

            (RW, RH) = (max_size[0]/W, max_size[1]/H)

            ratio = max(RW, RH)
            print(RW, RH, ratio)

            (wp, hp) = (round(ratio * W), round(ratio * H))
            print(wp, hp)

            self.image = self.image.resize((wp, hp))

            if ratio == RW:
                box = (0, (hp - max_size[1])/2, wp, (hp + max_size[1])/2)
            else:
                box = ((wp - max_size[0])/2, 0, (wp + max_size[0])/2, hp)   

            print("BOX: ", box)

            self.image = self.image.crop(box)

        elif mode == "target":
            if self.width > self.height:
                ratio_w = max_size[0] / self.width
                ratio_h = max_size[1] / self.height
            else:
                ratio_w = max_size[1] / self.width
                ratio_h = max_size[0] / self.height

            ratio = min(ratio_h, ratio_w, max_ratio)

            new_width = round(self.width * ratio)
            new_height = round(self.height * ratio)

            self.image = self.image.resize((new_width, new_height), Image.LANCZOS)
        
        parent_dir = os.path.dirname(self.reduced_path)

        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        self.image.save(self.reduced_path, 'JPEG', quality=quality)
        return os.path.exists(self.reduced_path)


if __name__ == '__main__':
    i = CustomImage("Sample.jpg")
    i.reduce_image(mode="target", ratio=1, quality=50, max_size=(400, 600), max_ratio=0)