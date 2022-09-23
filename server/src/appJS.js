const feedDisplay = document.querySelector('#feed')

fetch('http://localhost:3000/data')
    .then(response => {return response.json()})
    .then(data => {
        data.forEach(summary => {
            const Item = `<div><h2>` + summary.headline + `</h2><h3>` + summary.date + '</h3><p>' + summary.summary + '</p></div>'
            feedDisplay.insertAdjacentHTML("beforeend", Item)
        })
    })
    .catch(err => console.log(err))
