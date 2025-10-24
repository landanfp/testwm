import ffmpeg

def add_animated_watermark(input_video, logo_path, output_video):
    # متن متحرک SeriesPlus1 که از راست ظاهر میشه و بعد از 5 ثانیه به چپ برمی‌گرده
    text_filter = (
        "drawtext=text='SeriesPlus1':"
        "fontcolor=white:fontsize=36:x=w-tw-10*t:y=h-60:"
        "enable='between(mod(t,10),0,5)',"
        "drawtext=text='SeriesPlus1':"
        "fontcolor=white:fontsize=36:x=-tw+10*t:y=h-60:"
        "enable='between(mod(t,10),5,10)'"
    )

    (
        ffmpeg
        .input(input_video)
        .filter("movie", logo_path)
        .filter("scale", 100, -1)
        .overlay(10, 10)  # لوگو در بالا سمت چپ
        .output(output_video, vf=text_filter, vcodec="libx264", acodec="aac", movflags="+faststart")
        .overwrite_output()
        .run(quiet=True)
    )
