from PIL import Image, ImageDraw, ImageFont
from flask import Flask, render_template, send_from_directory, url_for, request
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
import math
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY_CODE']
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


# Image Upload Form
class ImageUploadForm(FlaskForm):
    photo = FileField('Upload an image',
                      validators=[
                          FileAllowed(photos, 'Only images are allowed'),
                          FileRequired('File field should not be empty')
                      ])
    submit = SubmitField('Generate')


@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)


@app.route('/', methods=['GET', 'POST'])
def upload():
    form = ImageUploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        base_img_url = url_for('get_file', filename=filename)[1:]
        print(base_img_url)
        user_input = str(request.form['watermark'])
        print(len(user_input))
        if len(user_input) == 0:
            watermark = 'static/images/name_logo.png'
            file_url = watermark_with_transparency(f'{base_img_url}', f'uploads/watermark_image.jpg',
                                                   watermark)

        else:
            watermark = user_input
            file_url = watermark_custom_text(f'{base_img_url}', f'uploads/watermark_image.jpg', watermark)
    else:
        file_url = None
    return render_template('index.html', form=form, file_url=file_url)


def watermark_with_transparency(input_image_path,
                                output_image_path,
                                watermark_image_path,
                                ):
    base_image = Image.open(input_image_path)
    wm = Image.open(watermark_image_path)
    wm_w, wm_h = wm.size
    base_w, base_h = base_image.size
    center_point = math.floor((base_w / 2) - (wm_w / 2))
    position = (center_point, math.floor(base_h / 2))
    transparent = Image.new('RGB', (base_w, base_h), (0, 0, 0, 0))
    transparent.paste(base_image, (0, 0))
    transparent.paste(wm, position, mask=wm)
    # transparent.show()
    transparent.save(output_image_path)
    return output_image_path


def watermark_custom_text(input_image_path,
                          output_image_path,
                          watermark_text,
                          ):
    base_image = Image.open(input_image_path)
    base_w, base_h = base_image.size

    draw = ImageDraw.Draw(base_image)
    font_size = 140
    font = ImageFont.truetype('static/fonts/Aboreto/Aboreto-Regular.ttf', font_size)

    _, _, wm_w, wm_h = draw.textbbox((0, 0), watermark_text, font=font)

    while draw.textlength(watermark_text, font) > base_w * .90:
        font_size -= 1
        font = ImageFont.truetype('static/fonts/Aboreto/Aboreto-Regular.ttf', font_size)
    if wm_w > base_w:
        wm_w = base_w * .9
    position = (((base_w / 2) - (wm_w/2)), ((base_h / 2) - (wm_h/2)))
    draw.text(position, watermark_text, font=font, fill=(255, 255, 255, 120))

    base_image.save(output_image_path)
    return output_image_path


if __name__ == '__main__':
    app.run(debug=True, port=8000)

