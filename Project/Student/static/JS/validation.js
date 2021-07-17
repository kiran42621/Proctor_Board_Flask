function Validate_Name(id,span_name){
//window.alert("Hi");
    if ((document.getElementById(id).value.length < 5) || (document.getElementById(id).value.length > 30)){
        document.getElementById(span_name).innerHTML = "Name length should be 5-30 characters";
        document.getElementById("btn_Register").disabled = true;
    }
    else{
        document.getElementById(span_name).innerHTML = "";
        document.getElementById("btn_Register").disabled = false;
    }
}

function Validate_USN(id,span_name,user){
//window.alert("Hi");
    if ((document.getElementById(id).value.length < 5) || (document.getElementById(id).value.length > 15)){
        document.getElementById(span_name).innerHTML = user + " should be 5 - 15 characters";
        document.getElementById("btn_Register").disabled = true;
    }
    else{
        document.getElementById(span_name).innerHTML = "";
        document.getElementById("btn_Register").disabled = false;
    }
}

function Validate_Number(id,span_name){
//window.alert("Hi");
    if ((document.getElementById(id).value.length < 10) || (document.getElementById(id).value.length > 11)){
        document.getElementById(span_name).innerHTML = "Mobile number should be 10 characters";
        document.getElementById("btn_Register").disabled = true;
    }
    else{
        document.getElementById(span_name).innerHTML = "";
        document.getElementById("btn_Register").disabled = false;
    }
}

function Validate_Password(id1,id2,span_name){
    if (document.getElementById(id1).value.length < 8){
        document.getElementById(span_name).innerHTML = "Password should be 8-13 characters";
        document.getElementById("btn_Register").disabled = true;
    }
    else{
        if(document.getElementById(id1).value == document.getElementById(id2).value){
            document.getElementById(span_name).innerHTML = "";
            document.getElementById("btn_Register").disabled = false;
        }
        else{
            document.getElementById(span_name).innerHTML = "Both the passwords should be same";
            document.getElementById("btn_Register").disabled = true;
        }
    }
}

function validate_password_recover(id1,id2,span_name){
    if((document.getElementById(id1).selectedIndex == 0) || (document.getElementById(id2).selectedIndex == 0)){
        document.getElementById(span_name).innerHTML = "Choose any questions";
        document.getElementById("btn_Register").disabled = true;
    }
    else{
        if(document.getElementById(id1).selectedIndex == document.getElementById(id2).selectedIndex){
            document.getElementById(span_name).innerHTML = "Both questions cannot be same";
            document.getElementById("btn_Register").disabled = true;
        }
        else{
            document.getElementById(span_name).innerHTML = "";
            document.getElementById("btn_Register").disabled = false;
        }
    }
}