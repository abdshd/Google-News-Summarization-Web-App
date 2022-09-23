const express = require('express')
const axios = require('axios')
const path = require('path')
const cors = require('cors')
const fs = require('fs')

const { response } = require('express')
  
const app = express()
app.use(cors())
const port = process.env.PORT || 3000

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '/index.html'))
})

app.get('/data', (req, res) => {
    axios.get(
        `https://2mc8tmmpla.execute-api.us-east-1.amazonaws.com/Prod`)
        
            .then(response => {
                let test = response.data
                res.json(test) //sendFile(__dirname + "/index.html", {arr: test})
            })
})

app.listen(port)
