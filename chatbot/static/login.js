// login.js - 仅包含登录页面相关的JavaScript代码

document.addEventListener('DOMContentLoaded', function() {
    // 密码可见性切换功能
    const toggleBtn = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password');
    
    if (toggleBtn && passwordInput) {
        toggleBtn.addEventListener('click', function() {
            // 切换密码可见性
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // 切换图标样式
            toggleBtn.classList.toggle('show-password');
        });
    }
});