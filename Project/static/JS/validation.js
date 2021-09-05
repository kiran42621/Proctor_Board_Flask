var error = [];

function Validate_Name(id,span_name, btn_name){
//window.alert("Hi");
    if ((document.getElementById(id).value.length < 5) || (document.getElementById(id).value.length > 30)){
        document.getElementById(span_name).innerHTML = "Name length should be 5-30 characters";
        if(!error.includes("name")){
            error.push("name");
        }

    }
    else{
        document.getElementById(span_name).innerHTML = "";
        index = error.indexOf("name");
        if(error.includes("name")){
            error.splice(index, 1);
        }
    }
    checkBtn();
}

function Validate_USN(id,span_name,user,btn_name){
//window.alert("Hi");
    if ((document.getElementById(id).value.length < 5) || (document.getElementById(id).value.length > 15)){
        document.getElementById(span_name).innerHTML = user + " should be 5 - 15 characters";
        //document.getElementById(btn_name).disabled = true;
        if(!error.includes("USN")){
            error.push("USN");
        }
    }
    else{
        document.getElementById(span_name).innerHTML = "";
        index = error.indexOf("USN");
        if(error.includes("USN")){
            error.splice(index, 1);
        }
    }
    checkBtn();
}

function Validate_Number(id,span_name,btn_name){
//window.alert("Hi");
    if ((document.getElementById(id).value.length < 10) || (document.getElementById(id).value.length > 11)){
        document.getElementById(span_name).innerHTML = "Mobile number should be 10 characters";
        if(!error.includes("Number")){
            error.push("Number");
        }
    }
    else{
        document.getElementById(span_name).innerHTML = "";
        index = error.indexOf("Number");
        if(error.includes("Number")){
            error.splice(index, 1);
        }
    }
    checkBtn();
}

function Validate_Password(id1,id2,span_name,btn_name){
    if (document.getElementById(id1).value.length < 8){
        document.getElementById(span_name).innerHTML = "Password should be 8-13 characters";
        if(!error.includes("Password")){
            error.push("Password");
        }
    }
    else{
        if(document.getElementById(id1).value == document.getElementById(id2).value){
            document.getElementById(span_name).innerHTML = "";
            if(error.includes("Password")){
                index = error.indexOf("Password");
                error.splice(index, 1);
            }
        }
        else{
            document.getElementById(span_name).innerHTML = "Both the passwords should be same";
            if(!error.includes("Password")){
                error.push("Password");
            }
        }
    }
    checkBtn();
}

function validate_password_recover(id1,id2,span_name,btn_name){
    if((document.getElementById(id1).selectedIndex == 0) || (document.getElementById(id2).selectedIndex == 0)){
        document.getElementById(span_name).innerHTML = "Choose any questions";
        if(!error.includes("PassRecover2")){
            error.push("PassRecover2");
        }
    }
    else{
        if(document.getElementById(id1).selectedIndex == document.getElementById(id2).selectedIndex){
            document.getElementById(span_name).innerHTML = "Both questions cannot be same";
            if(!error.includes("PassRecover2")){
            error.push("PassRecover2");
        }
        }
        else{
            document.getElementById(span_name).innerHTML = "";
            index = error.indexOf("PassRecover2");
            if(error.includes("PassRecover2")){
                error.splice(index, 1);
            }
        }
    }
    checkBtn();
}