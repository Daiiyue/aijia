function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(document).ready(function () {
    // 页面加载号
    $("#form-avatar").submit(function (event) {
        // 阻止表单的默认提交方式
        event.preventDefault();
        // 使用jquery.from的ajaxSubmit来给表单增加回调参数
        $(this).ajaxSubmit({
            url : "/api/v1_0/users/avatar",
            type: 'post',
            dataType:'json',
            headers:{
                'X-CSRFToken' : getCookie("csrf_token")
            },
            success:function (resp) {
                if (resp.errno == 0){
                    // 上传文件成功
                    $("#user-avatar").attr('src', resp.data.avatar_url)
                } else {
                    alert(resp.errmsg);
                }
            }
        });
    })
    $("#form-name").submit(function (event) {
        event.preventDefault();
        var name = $("#user-name").val();
        if (!name){
            alert("请填写用户名")
            return;
        }

        $.ajax({
            url:"/api/v1_0/user/name",
            type:"PUT",
            data:JSON.stringify({name:name}),
            contentType:"application/json",
            dataType:"json",
            headers:{
                'X-CSRFToken' : getCookie("csrf_token")
            },
            success:function (resp) {
                if (resp.errno ==0 ) {
                    $(".error-msg").hide();
                    showSuccessMsg();

                } else if (resp.errno == 4001){
                    $(".error-msg").show();
                    } else if (resp.data == 4101) {
                        location.href = "/"
                }
            }

        });
    })
})