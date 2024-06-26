
const fs = require("fs")

const http = require("http")
const cors = require("cors")
const https = require("https")
const express = require("express")

const youtube = {
    music: require("node-youtube-music"),
    core: require("ytdl-core")
}

const ffmpeg = {
    static: require("ffmpeg-static"),
    fluent: require("fluent-ffmpeg")
}

let cached = []

const app = express()
const server = http.createServer(app)

app.use(cors())
app.use(express.json())

app.get("/", (request, response) => {
    response.sendFile(__dirname + "/index.html")
})
app.post("/search", async (request, response) => {
    if (request.body.query) {
        if (request.body.query.includes("+") && request.body.query.split("+").length > 2) request.body.query = request.body.query.split("+").join(" ")
        result = (await youtube.music.searchMusics(request.body.query)).filter((item) => (!item.isExplicit)).map((item) => ({
            id: item.youtubeId,
            title: item.title,
            artists: item.artists.map((artist) => (artist.name)),
            duration: [item.duration.label, item.duration.totalSeconds],
            thumbnail: item.thumbnailUrl.split("/").pop()
        }))
        /* Update Database */
        update = result.map((item) => ([item.id, item.title, item.artists, item.duration, item.thumbnail])).filter((item) => (!cached.includes(item)))
        if (update.length > 0) {
            cached = cached.concat(update)
            fs.writeFileSync("./cached", JSON.stringify(cached))
        }
        response.json(result.map((item) => ({
            id: ["A" + item.id, "I" + item.thumbnail.slice(0, 11)],
            title: item.title,
            artists: item.artists,
            duration: item.duration
        })))
    }
})
app.use("/media/:id", (request, response) => {
    if (request.method === "POST") {

    } else if (request.method === "GET") {
        if (request.params.id.startsWith("A")) {
            youtube.core("https://www.youtube.com/watch?v=" + request.params.id.slice(1, 12), {
                quality: "highestaudio", filter: "audioonly"
            }).pipe(response)
            /*
            ffmpeg.fluent()
                .inputFormat("webm")
                .format("flac")
                .audioCodec("flac")
                .audioFrequency(41000)
                .audioBitrate("1411k")
                .audioChannels(2)
                .on("error", (err) => {
                    console.log(err)
                })
                .pipe(response)
            */
        } else if (request.params.id.startsWith("I") && request.query.size) {
            size = request.query.size.split("x")
            result = cached.filter((item) => (item[4].slice(0, 11) === request.params.id.slice(1, 12))).pop()
            https.get("https://lh3.googleusercontent.com/" + result[4].split("=")[0] + `=w${size[0]}-h${size[1]}-l90-rj`, (object) => {
                object.on("response", (data) => {
                    response.set(data.headers)
                })
                object.pipe(response)
            })
        }
    }
})

server.listen(5000, () => {
    if (!fs.existsSync("./cached")) {
        fs.writeFileSync("./cached", JSON.stringify([]))
    }
    cached = JSON.parse(fs.readFileSync("./cached"))
    ffmpeg.fluent.setFfmpegPath(ffmpeg.static)
    console.log("Server Online.")
})