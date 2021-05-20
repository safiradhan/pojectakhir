function createHTMLRow(data) {  
    const row = document.createElement('tr');

    // view button
    const viewbutton = document.createElement('button');

    const insideButton = document.createTextNode("View");
    viewbutton.appendChild(insideButton)
    viewbutton.onclick = () => {
        // pindah ke view.html dengan querystring data.id
        window.location.href = "view.html?id=" + data.id   
    }
    
    
    for(prop in data) {
        const cell = document.createElement('td')
        cell.innerHTML = data[prop];
        row.appendChild(cell);
    }
        // add button to table
        row.appendChild(viewbutton)
        return row;
}