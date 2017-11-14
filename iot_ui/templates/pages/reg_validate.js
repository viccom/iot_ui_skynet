    function textFocus(el) {
        if (el.defaultValue == el.value) { el.value = ''; el.style.color = '#333'; }
    }
    function textBlur(el) {
        if (el.value == '') { el.value = el.defaultValue; el.style.color = '#999'; }
    }

    $(function(){
        //注册页面的提示文字
       (function register(){
           //邮箱栏失去焦点
            $(".block .email").blur(function(){
                var isEmail = /^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;

                if( $(this).val()==""|| $(this).val()=="请输入用户邮箱")
                {
                    $(this).next().html("请输入用户邮箱");
                }
                else if(!isEmail.test($(".block .email").val()))
                {
                    $(this).next().html("邮箱格式错误!");
                }
                else
                {
                    $(this).next().empty();
                }
            });

           //姓名栏失去焦点
            $(".block .FirstName").blur(function(){

                if( $(this).val()==""|| $(this).val()=="请输入用户的姓")
                {
                    $(this).next().html("请输入用户的姓");
                }
                else
                {

                    $(this).next().empty();
                }
            });

           //手机号栏失去焦点
            $(".block .phone").blur(function(){
                var reg=/^1[3|4|5|7|8][0-9]\d{4,8}$/i;//验证手机正则(输入前7位至11位)

                if( $(this).val()==""|| $(this).val()=="请输入您的手机号")
                {
                    $(this).next().html("请输入您的手机号");
                }
                else if($(this).val().length<11)
                {
                    $(this).next().html("手机号长度有误！");
                }
                else if(!reg.test($(".block .phone").val()))
                {
                    $(this).next().html("手机号不存在!");
                }
                else
                {
                    $(this).next().empty();
                }
            });

            //验证码栏失去焦点
            $(".reg-box .phonekey").blur(function(){
                reg=/^[A-Za-z0-9]{6}$/;
                if( $(this).val()=="" || $(this).val()=="请输入收到的验证码")
                {
                    $(this).addClass("errorC");
                    $(this).next().next().html("请填写验证码");
                    $(this).next().next().css("display","block");
                }
                else if(!reg.test($(".phonekey").val()))
                {
                    $(this).addClass("errorC");
                    $(this).next().next().html("验证码输入有误！");
                    $(this).next().next().css("display","block");
                }
                else
                {
                    $(this).removeClass("errorC");
                    $(this).next().next().empty();
                    $(this).addClass("checkedN");
              }
            });

            //密码栏失去焦点
            $(".block .password").blur(function(){
                var reg=/^[\@A-Za-z0-9\!\#\$\%\^\&\*\.\~]{6,22}$/;
                if(!reg.test($(".password").val()))
                {
                    $(this).next().html("格式有误，请输入6~12位的数字、字母或特殊字符！");
                }
                else
                {
                    $(this).next().html("");
                }
            });
            /*确认密码失去焦点*/
            $(".block .repassword").blur(function(){
                var pwd1=$('.block input.password').val();
                var pwd2=$(this).val();
                if(($(this).val() == '请再次输入密码' || $(this).val() == "") && (pwd1 == "请输入密码" || pwd1 == "") ){
                        return;
                }else if(pwd1!=pwd2)
                {
                    $(this).next().html("两次密码输入不一致！");
                }
                else
                {
                    $(this).next().empty();
                }
            });
       })();
        /*生成验证码*/
        (function create_code(){
            function shuffle(){
                var arr=['1','r','Q','4','S','6','w','u','D','I','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
                        'q','2','s','t','8','v','7','x','y','z','A','B','C','9','E','F','G','H','0','J','K','L','M','N','O','P','3','R',
                        '5','T','U','V','W','X','Y','Z'];
                return arr.sort(function(){
                    return (Math.random()-.5);
                });
            };
            shuffle();
            function show_code(){
                var ar1='';
                var code=shuffle();
                for(var i=0;i<6;i++){
                    ar1+=code[i];
                };
                //var ar=ar1.join('');
                $(".reg-box .phoKey").text(ar1);
            };
            show_code();
            $(".reg-box .phoKey").click(function(){
                show_code();
            });
        })();

        //登录页面的提示文字
        //账户输入框失去焦点
        (function login_validate(){
            $(".reg-box .account").blur(function(){
                reg=/^1[3|4|5|8][0-9]\d{4,8}$/i;//验证手机正则(输入前7位至11位)

                if( $(this).val()==""|| $(this).val()=="请输入您的账号")
                {
                    $(this).addClass("errorC");
                    $(this).next().html("账号不能为空！");
                    $(this).next().css("display","block");
                }
                else if($(".reg-box .account").val().length<11)
                {
                    $(this).addClass("errorC");
                    $(this).next().html("账号长度有误！");
                    $(this).next().css("display","block");
                }
                else if(!reg.test($(".reg-box .account").val()))
                {
                    $(this).addClass("errorC");
                    $(this).next().html("账号不存在!");
                    $(this).next().css("display","block");
                }
                else
                {
                    $(this).addClass("checkedN");
                    $(this).removeClass("errorC");
                    $(this).next().empty();
                }
            });
            /*密码输入框失去焦点*/
            $(".reg-box .admin_pwd").blur(function(){
                reg=/^[\@A-Za-z0-9\!\#\$\%\^\&\*\.\~]{6,22}$/;

                if($(this).val() == "请输入密码"){
                    $(this).addClass("errorC");
                    $(this).next().html("密码不能为空！");
                    $(this).next().css("display","block");

                }else if(!reg.test($(".admin_pwd").val()))
                {
                    $(this).addClass("errorC");
                    $(this).next().html("密码为6~12位的数字、字母或特殊字符！");
                    $(this).next().css("display","block");
                }else
                {
                    $(this).addClass("checkedN");
                    $(this).removeClass("errorC");
                    $(this).next().empty();
                }
            });

            /*验证码输入框失去焦点*/
            $(".reg-box .photokey").blur(function(){
                var code1=$('.reg-box input.photokey').val().toLowerCase();
                var code2=$(".reg-box .phoKey").text().toLowerCase();
                if(code1!=code2)
                {
                    $(this).addClass("errorC");
                    $(this).next().next().html("验证码输入错误！");
                    $(this).next().next().css("display","block");
                }
                else
                {
                    $(this).removeClass("errorC");
                    $(this).next().next().empty();
                    $(this).addClass("checkedN");
                }
            })
        })();
    });

    /*清除提示信息*/
    function emptyRegister(){
        console.log("clear");
        $(".block .email,.block .FirstName,.block .LastName,.block .phone,.block .password,.block .repassword").next().empty();
    }
    function emptyLogin(){
        $(".reg-box .account,.reg-box .admin_pwd,.reg-box .photokey").removeClass("errorC");
    }

    function NewUserRegister(){
        console.log("NewUserRegister");
        var email = $(".block .email").val();
        var FirstName = $(".block .FirstName").val();
        var LastName = $(".block .LastName").val();
        var phone = $(".block .phone").val();
        var password = $(".block .password").val();
        var cuser_id = $.cookie('user_id');

        console.log(email, FirstName, LastName, phone, password);
        var newuserdata = {
                "doc": '{"docstatus":0,"doctype":"User","name":"New+User+1","__islocal":1,"__unsaved":1,"owner":"'+cuser_id+'","enabled":1,"send_welcome_email":0,"language":"zh","thread_notify":1,"simultaneous_sessions":1,"user_type":"System+User","email":"'+email+'","first_name":"'+FirstName+'","last_name":"'+LastName+'","mobile_no":"'+phone+'","new_password":"'+password+'"}',
                "action": "Save",
                "userid":'"'+email+'"',
                "company": '"'+company+'"',

            };
        $.ajax({
                type: 'POST',
                url: "/api/method/iot_ui.ui_api.add_newuser2company",
                contentType: "application/x-www-form-urlencoded;charset=utf-8", //必须有
                data: newuserdata,
                dataType: "json",
                success: function(r) {
                    console.log(r);


                  },
                 error: function() {
                      console.log("异常!");
                  }
            });


    // var t=setTimeout("add_newuser2company('"+email+"')",2000);
    }

    function add_newuser2company(newuserid){
        var newuser =new Array(newuserid);
        var user2company = {
            "members": newuser,
            "company": company
        };
        $.ajax({
            type: 'POST',
            url: url,
            contentType: "application/json", //必须有
            data: JSON.stringify(user2company),
            dataType: "json",
            success: function(data) {
                console.log("加入公司成功!");
              },
             error: function() {
                  console.log("加入公司异常!");
              }
        });
    }
