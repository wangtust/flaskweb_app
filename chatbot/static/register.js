document.addEventListener('DOMContentLoaded', function() {
    // 1. 元素获取（一次性获取所有需要的DOM元素）
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const verifyCodeInput = document.getElementById('verify_code');
    const sendCodeBtn = document.getElementById('send_code_btn');
    const passwordInput = document.getElementById('password');
    const confirmInput = document.getElementById('confirm_password');
    const togglePassword = document.getElementById('toggle-password');
    const toggleConfirmPassword = document.getElementById('toggle-confirm-password');
    const usernameError = document.getElementById('username-error');
    const emailError = document.getElementById('email-error');
    const passwordError = document.getElementById('password-error');
    const confirmError = document.getElementById('confirm-password-error');
    const form = document.querySelector('form');

    // 2. 密码可见性切换功能
    function setupPasswordToggle(toggleBtn, passwordInput) {
        if (!toggleBtn || !passwordInput) return;
        
        toggleBtn.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // 切换图标
            const icon = toggleBtn.querySelector('i');
            if (type === 'password') {
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }

    // 绑定密码可见性切换
    setupPasswordToggle(togglePassword, passwordInput);
    setupPasswordToggle(toggleConfirmPassword, confirmInput);

    // 3. 表单验证函数
    // 用户名验证（纯英文，3-16位）
    function validateUsername() {
        const username = usernameInput.value.trim();
        const regex = /^[A-Za-z]{3,16}$/;

        if (username === '') {
            usernameError.textContent = '';
            return false;
        }
        if (!regex.test(username)) {
            usernameError.textContent = '用户名必须为3-16位纯英文';
            return false;
        } else {
            usernameError.textContent = '';
            return true;
        }
    }

    // 密码验证（包含大小写字母、数字，8-20位）
    function validatePassword() {
        const password = passwordInput.value;
        const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,20}$/;

        if (password === '') {
            passwordError.textContent = '';
            return false;
        }
        if (!regex.test(password)) {
            passwordError.textContent = '密码需包含大小写字母和数字（8-20位）';
            return false;
        } else {
            passwordError.textContent = '';
            return true;
        }
    }

    // 确认密码验证
    function validateConfirmPassword() {
        const password = passwordInput.value;
        const confirmPwd = confirmInput.value;

        if (confirmPwd === '') {
            confirmError.textContent = '';
            return false;
        }
        if (confirmPwd !== password) {
            confirmError.textContent = '两次输入的密码不一致';
            return false;
        } else {
            confirmError.textContent = '';
            return true;
        }
    }

    // 4. 验证码发送逻辑
    let countdown = 0; // 倒计时控制

    function sendVerifyCode() {
        const email = emailInput.value.trim();
        // 邮箱格式验证
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            emailError.textContent = '请输入有效的邮箱地址';
            emailError.style.color = 'red';
            return;
        }

        // 防止倒计时中重复发送
        if (countdown > 0) return;

        // 发送请求到后端
        fetch('/send-verify-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP错误：${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                emailError.textContent = '验证码已发送，5分钟内有效';
                emailError.style.color = 'green';
                // 启动60秒倒计时
                countdown = 60;
                updateCountdown();
            } else {
                emailError.textContent = data.msg || '发送失败，请重试';
                emailError.style.color = 'red';
            }
        })
        .catch(error => {
            console.error('验证码发送失败：', error);
            emailError.textContent = '网络异常，发送失败';
            emailError.style.color = 'red';
        });
    }

    // 倒计时更新函数
    function updateCountdown() {
        if (countdown > 0) {
            sendCodeBtn.disabled = true;
            sendCodeBtn.textContent = `重新发送(${countdown}s)`;
            countdown--;
            setTimeout(updateCountdown, 1000);
        } else {
            sendCodeBtn.disabled = false;
            sendCodeBtn.textContent = '发送验证码';
        }
    }

    // 绑定发送验证码按钮点击事件
    sendCodeBtn.addEventListener('click', sendVerifyCode);

    // 5. 实时输入验证（提升用户体验）
    usernameInput.addEventListener('input', validateUsername);
    passwordInput.addEventListener('input', validatePassword);
    confirmInput.addEventListener('input', validateConfirmPassword);
    emailInput.addEventListener('input', function() {
        // 邮箱输入变化时清空错误提示
        if (emailInput.value.trim() !== '') {
            emailError.textContent = '';
        }
    });

    // 6. 表单提交验证
    form.addEventListener('submit', function(e) {
        const isUsernameValid = validateUsername();
        const isPasswordValid = validatePassword();
        const isConfirmValid = validateConfirmPassword();
        const isCodeValid = verifyCodeInput.value.trim() !== '';

        // 验证码非空验证
        if (!isCodeValid) {
            emailError.textContent = '请输入验证码';
            emailError.style.color = 'red';
        }

        // 任何一项验证失败则阻止提交
        if (!isUsernameValid || !isPasswordValid || !isConfirmValid || !isCodeValid) {
            e.preventDefault();
        }
    });
});