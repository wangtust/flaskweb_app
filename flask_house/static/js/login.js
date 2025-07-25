$(document).ready(function () {
    // 注册
    $('#registe-btn').on('click', function () {
        $('#registeform').bootstrapValidator({
            message: 'This value is not valid',
            fields: {
                username: {
                    message: 'The username is not valid',
                    validators: {
                        notEmpty: {
                            message: '用户名不能为空'
                        },
                        stringLength: {
                            min: 6,
                            max: 15,
                            message: '用户名长度必须在6到15位之间'
                        },
                        regexp: {
                            regexp: /^[a-zA-Z0-9_\.]+$/,
                            message: '用户名只能包含大写、小写、数字和下画线'
                        },
                        different: {
                            field: 'password',
                            message: '用户名不能与密码相同'
                        }
                    }
                },
            email: {
                validators: {
                    notEmpty: {
                        message: '邮箱不能为空'
                    }
                }
            },
                password: {
                    validators: {
                        notEmpty: {
                            message: '密码不能为空'
                        },
                        identical: {
                            field: 'confirmPassword',
                            message: '与确认密码不一致'
                        },
                        different: {
                            field: 'username',
                            message: '密码不能与用户名相同'
                        }
                    }
                },
                confirmPassword: {
                    validators: {
                        notEmpty: {
                            message: '确认密码不能为空'
                        },
                        identical: {
                            field: 'password',
                            message: '与密码不一致'
                        },
                        different: {
                            field: 'username',
                            message: '确认密码不能与用户名相同'
                        }
                    }
                }
            }
        });
        var validator = $('#registeform').data("bootstrapValidator"); //获取validator对象
        validator.validate(); //手动触发验证
        if (validator.isValid()) { //通过验证
            $.ajax({
                type: 'post',
                url: '/register',
                data: $('#registeform').serialize(),
                dataType: 'json',
                success: function (result) {
                    if (result['valid'] == '0') {
                        alert(result['msg']);
                        var validatorObj = $("#registeform").data('bootstrapValidator');
                        if (validatorObj) {
                            validatorObj.destroy();
                            $('#registeform').data('bootstrapValidator', null);
                        }
                    } else {
                        // 注册成功，跳转到登录模态框
                        $('#register').modal('hide');
                        alert('注册成功，请登录');
                        $('#login').modal('show');
                        // 重置表单与验证器
                        $('#registeform')[0].reset();
                        var validatorObj = $("#registeform").data('bootstrapValidator');
                        if (validatorObj) {
                            validatorObj.destroy();
                            $('#registeform').data('bootstrapValidator', null);
                        }
                    }
                },

            })
        }
    });

    // 登录
    $('#login-btn').on('click', function (e) {
        e.preventDefault();
        $('#loginform').bootstrapValidator({
            message: 'This value is not valid',
            fields: {
                username: {
                    message: 'The username is not valid',
                    validators: {
                        notEmpty: {
                            message: '用户名不能为空'
                        },
                        stringLength: {
                            min: 6,
                            max: 15,
                            message: '用户名长度必须在6到15位之间'
                        },
                        regexp: {
                            regexp: /^[a-zA-Z0-9_\.]+$/,
                            message: '用户名只能包含大写、小写、数字和下划线'
                        }
                    }
                },
                password: {
                    validators: {
                        notEmpty: {
                            message: '密码不能为空'
                        },
                        different: {
                            field: 'username',
                            message: '密码不能与用户名相同'
                        }
                    }
                }
            }
        }); //验证配置
        var validator = $('#loginform').data("bootstrapValidator"); //获取validator对象
        validator.validate(); //手动触发验证
        if (validator.isValid()) { //通过验证
            $.ajax({
                type: 'post',
                url: '/login',
                data: $('#loginform').serialize(),
                dataType: 'json',
                success: function (result) {
                    if (result['valid'] == '0') {
                        alert(result['msg'])
                        var validatorObj = $("#loginform").data('bootstrapValidator');
                        if (validatorObj) {
                            $("#loginform").data('bootstrapValidator').destroy(); //或者 validatorObj.destroy(); 都可以，销毁验证
                            $('#loginform').data('bootstrapValidator', null);
                        }
                    } else {
                        href_str = "/user/" + result['msg'];

                        window.location.replace(href_str);
                    }
                },

            })
        }
    });
    // 发送注册邮箱验证码
    $('#send-reg-code-btn').on('click', function () {
        var email = $('#reg_email').val();
        if (!email) {
            return alert('请输入邮箱');
        }
        var $btn = $(this);
        $.post('/send_reg_code', {email: email}, function (resp) {
            alert(resp.msg);
            if (resp.valid == 1) {
                var countdown = 300;
                $btn.prop('disabled', true);
                var timer = setInterval(function() {
                    if (countdown <= 0) {
                        clearInterval(timer);
                        $btn.prop('disabled', false).text('发送验证码');
                    } else {
                        $btn.text('重新发送(' + countdown + 's)');
                        countdown--;
                    }
                }, 1000);
            }
        }, 'json').fail(function() {
            alert('发送失败');
        });
    });
// 退出
$("#logout").on('click', function () {
    $.ajax({
        url: '/logout',
        type: 'get',
        dataType: 'json',
        success: function (res) {
            if (res["valid"] == '1') {   // 退出成功
                window.location.href = '/';
            } else {                     // 退出失败
                alert(res["msg"]);
            }
        }
    })
});
});