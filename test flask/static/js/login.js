$(function() {
    //点击“去注册”的链接
    $("#link_reg").on('click',function(){
        $('.login-box').hide()
        $('.reg-box').show()
    })

    //点击“登录”的链接
    $("#link_login").on('click',function(){
        $('.login-box').show()
        $('.reg-box').hide()
    })

   
    //从layui 中获取form 对象
    var form =layui.form 
    var layer = layui.layer
    //未捕获到数据内容
    //通过form.verify函数自定义校验规则
    // form.verity({        
    //     pwd:[/^[\S]{6,12}$/,'密码必须6到12位，且不能出现空格'],
    //     repwd:function(value){
    //         // 校验两次密码是否一致
    //         var pwd=$('#form-box [name=password]')
    //         if (pwd!=value){
    //             return '两次密码不一致'
    //         }
    //     }
    // })
    
    
    //监听注册表单的提交事件
    $('#form_reg').on('submit',function(e){
        //layer.msg('进行注册表单，准备提交注册数据')
        e.preventDefault();
        var patt = /[/^[\S]{6,12}$/;
        password = $('#form_reg [name=password]').val()
        if(!patt.test(password)) { 
          return layer.msg('密码必须6到12位，且不能出现空格')
        }
        if(password!=$('#form_reg [name=repassword]').val()) { 
            return layer.msg('两次密码输入不一致，请重新输入')
          }

        var data= {username:$('#form_reg [name=username]').val(),password:$('#form_reg [name=password]').val()}
        console.log('username is  ',$('#form_reg [name=username]').val())
        console.log('password is  ',$('#form_reg [name=password]').val())
        //$.post('http://ajax.frontend.itheima.net/api/reguser',data,function(res){
        $.ajax({
            url:"http://127.0.0.1/api/reguser",
            type:"POST",
            data:{username:$('#form_reg [name=username]').val(),password:$('#form_reg [name=password]').val()},
            success: function (data) {
                console.log('receive data is ',data)
                if (data=="msg:注册成功") {
                    layer.msg("注册成功,请登录")
                    $('#link_login').click()
                }
                else if (data=="msg:用户名被占用，请更换其他用户名！") {
                    layer.msg("该用户已注册,请更换用户名注册")
                }
                else {
                    console.log('receive data is ',data)
                }
            },
            error: function(res) {
                console.log(res)
                layer.msg('注册失败，出错了')
            },
        })
               
    })

    //监听登录事件
    $('#form_login').on('submit',function(e){
        layer.msg('进行登录操作，准备提交登录数据')
        e.preventDefault();
        //检查密码长度，'密码必须6到12位，且不能出现空格'
        var patt = /[/^[\S]{6,12}$/;
        password = $('#form_login [name=password]').val()
        if(!patt.test(password)) { 
          return layer.msg('密码必须6到12位，且不能出现空格')
        }

        var data= {username:$('#form_login [name=username]').val(),password:$('#form_login [name=password]').val()}
        console.log('username is  ',$('#form_login [name=username]').val())
        console.log('password is  ',$('#form_login [name=password]').val())
        $.ajax({
            url:'http://127.0.0.1/api/login',
            method: 'POST',
            data:{username:$('#form_login [name=username]').val(),password:$('#form_login [name=password]').val()},
            success: function (data) {
                console.log(data)
                if (data === "msg:未找到该用户,请注册！"){
                    console.log("未找到该用户,请注册！")
                    layer.msg("未找到该用户,请注册！")
                }
                // console.log('receive data is ',data)
                else if (data === "msg:查询到该用户名,登录成功！") {
                    // layer.msg("登录成功,进入首页")
                    localStorage.setItem('user',$('#form_login [name=username]').val())
                    layer.msg("登录成功,进入首页")
                    location.href= 'homepage.html'
                    //$('#link_login').click()
                }
                else if(data === "msg:用户名或密码错误，请重新输入！"){
                    console.log('receive data is ',data)
                    layer.msg("用户名或密码错误 请重试")
                }
            },
            error: function(res) {
                console.log(res)
                layer.msg('登录失败，出错了')
            },           
        })          
    })
})


