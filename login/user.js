document.addEventListener('DOMContentLoaded', function () {
    fetch("http://127.0.0.1:5000/users/", {
        method: "GET"
    })
        .then(Response => Response.json())
        .then(Response => {
            const x = document.getElementById("userTable")
            const y = x.querySelector("tbody")
            y.innerHTML = ""
            Response.forEach(element => {
                const z = createHTMLRow({
                    user_id: element.user_id,
                    full_name: element.full_name,
                    user_name: element.user_name,
                    password: element.password,
                    email: element.email
                })
                y.appendChild(z)
            });
        })
});