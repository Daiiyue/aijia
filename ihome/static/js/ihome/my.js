function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function logout() {
    $.ajax({
        url:"/api/v1_0/session",
        type:'delete',
        headers:{
            "X-CSRFToken":getCookie("csrf_token")
        },
        dataType:'json',
        success:function (data) {
            if (data.errno == 0 ) {
                location.href='/';
            }
        }
    });
}

$(document).ready(function(){
    $.get("/api/v1_0/user",function (resp) {
        if (resp.errno == 4101){
            login_href = "/";
        } else if (resp.errno == 0){
            $("#user-name").html(resp.data.name);
            $("#user-mobile").html(resp.data.mobile);
            if (resp.data.avatar){
                $("#user-avatar").attr("src",resp.data.avatar)
            }
        }
    },"json"); // 此处的json指datatype,即前段要接受来自后端的参数类型



})