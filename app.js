const path = require('path')
const cors = require('cors')
const express = require('express')
const compression = require('compression')

const routers = {}

const app = express()
const PORT = process.env.PORT || 12315

app.use((req, res, next) => {
    console.log(`${req.method} ${req.url}`)
    next()
})

app.use(cors())
app.use(compression())
app.use(express.json())

Object.entries(routers).forEach(([path, router]) => {
    app.use(`/${path}`, router)
})

app.all('/', (req, res) => {
    res.send('GirlsCreationR Translation')
})

Array.from(['dicts', 'names', 'novels', 'words']).forEach(cls => {
    app.get(`/${cls}/*`, (req, res) => {
        const filePath = path.join(__dirname, `${cls}/${req.params[0]}`)
        res.sendFile(filePath, err => err && res.sendStatus(404))
    })
})

const server = app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`)
})
