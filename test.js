
const fs = require("fs")

const ffmpeg = {
    fluent: require("fluent-ffmpeg"),
    static: require("ffmpeg-static")
}

ffmpeg.fluent.setFfmpegPath(ffmpeg.static)

_process = ffmpeg.fluent()
    .input("concat:" + fs.readdirSync("D:\\VIDEO_TS").filter((filename) => (filename.toLowerCase().endsWith(".vob"))).slice(1, 2).map((filename) => "D:\\VIDEO_TS\\" + filename).join("|"))
    .videoCodec('libx264')
    .audioCodec('aac')
    .outputOptions([
        '-crf 0', // Lossless quality
        '-preset ultrafast', // Fastest encoding
        '-vf zscale=w=1920:h=1080,unsharp=5:5:1.5:5:5:0.5,hqdn3d=1.5:1.5:6:6',
        '-ac 6', // 5.1 surround
        '-movflags +faststart',
    ])
    .format("mp4")
    .output("video.mp4")
    .on("end", () => console.log("done."))
    .on("progress", (data) => {
        console.log(data)
    })
    .on('stderr', (stderr) => console.log(stderr)) // Log FFmpeg output
    .run()
