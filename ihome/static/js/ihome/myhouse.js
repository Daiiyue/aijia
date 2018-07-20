$(document).ready(function(){
    $.get("/api/v1_0/user/auth",function (resp) {
        if (resp.errno == 0){
            $(".auth-warn").hide()
        } else {
            $(".auth-warn").show();
        }
    });

})
