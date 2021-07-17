function Validate_Name(id){
window.alert("Hi");
    if ((document.getElementById(id).length() < 5) && (document.getElementById(id).value.length() > 30)){
        document.getElementById("Proc_Name_Error").innerHtml = "Name length should be 5-30 characters";
        window.alert("Hi");
    }
}