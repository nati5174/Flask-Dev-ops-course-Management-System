function registar_data(){

    let username1 = document.getElementById("username_reg").value
    let email1 = document.getElementById("email_reg").value
    let password1 = document.getElementById("pswd_reg").value
    let type1 = document.getElementById("stdnt").value


    let reg_data = JSON.stringify({'username': username1, 'email': email1, 'password':password1, 'type': type1})



    let req = new XMLHttpRequest()
    req.open('POST', 'http://127.0.0.1:5000/register')

    req.setRequestHeader('Content-Type', 'application/json')
    console.log(JSON.stringify(reg_data))

    req.send(reg_data);


    return;


}

function login_data(){

    let username1 = document.getElementById("username_log").value
    let password1 = document.getElementById("pswd_log").value

    let login_data = JSON.stringify({'username': username1, 'password':password1})


    let req = new XMLHttpRequest()
    req.open('POST', 'http://127.0.0.1:5000/login')

    req.setRequestHeader('Content-Type', 'application/json')
    console.log(JSON.stringify(login_data))

    req.send(login_data);

    location.replace("https://www.w3schools.com")


    return;


}

