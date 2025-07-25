// 存储对话历史（上下文记忆）
let conversationHistory = [];
// 控制是否等待AI响应（防止重复发送）
let isWaiting = false;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function () {
  loadConfig();

  // 回车发送消息（不含Shift键）
  document.getElementById('user-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
});

// 加载配置信息（模型+API状态）
function loadConfig() {
  fetch('/config')
    .then(res => res.json())
    .then(config => {
      const configInfo = document.getElementById('config-info');
      configInfo.textContent = `模型：${config.model} | API：${config.api_configured ? '已配置' : '未配置'}`;
    })
    .catch(err => {
      console.error('获取配置失败：', err);
    });
}

// 发送消息函数
function sendMessage() {
  if (isWaiting) return; // 防止重复提交

  const input = document.getElementById('user-input');
  const msg = input.value.trim();

  if (!msg) { // 空消息校验
    input.focus();
    return;
  }

  // 添加用户消息到界面
  addMessage("你", msg, "user");

  // 记录到对话历史
  conversationHistory.push({
    role: "user",
    content: msg
  });

  // 清空输入框并设置等待状态
  input.value = "";
  setWaiting(true);

  // 显示加载中提示
  const loadingMsg = addMessage("AI助手", "<div class='loading'></div> 正在思考...", "bot");

  // 发送请求到后端
  fetch('/chat', {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: msg,
      history: conversationHistory.slice(-10) // 只传最近10轮对话
    })
  })
    .then(res => res.json())
    .then(data => {
      loadingMsg.remove(); // 移除加载提示

      if (data.error) {
        addMessage("系统", data.response, "bot error");
      } else {
        addMessage("AI助手", data.response, "bot");
        // 记录AI回复到历史
        conversationHistory.push({
          role: "assistant",
          content: data.response
        });
      }

      setWaiting(false);
    })
    .catch(err => {
      console.error('发送消息失败：', err);
      loadingMsg.remove();
      addMessage("系统", "抱歉，网络连接出现问题，请稍后再试。", "bot error");
      setWaiting(false);
    });
}

function addMessage(sender, text, cls) {
  // 创建外层容器
  const msgDiv = document.createElement("div");
  msgDiv.className = "msg " + cls.split(' ')[0];

  // 创建头像元素
  const avatar = document.createElement("img");
  avatar.className = "avatar";
  // 根据发送者类型设置头像路径（本地图片）
  if (cls.includes('bot')) {
    avatar.src = "/static/bot.jpg";  // AI头像
    avatar.alt = "AI助手";
  } else {
    avatar.src = "/static/user.jpg";  // 用户头像
    avatar.alt = "用户";
  }

  // 创建内容容器（原有代码）
  const contentDiv = document.createElement("div");
  contentDiv.className = "msg-content" + (cls.includes('error') ? ' error' : '');

  // 创建发送者标签和消息内容（原有代码）
  const senderDiv = document.createElement("div");
  senderDiv.className = "sender";
  senderDiv.textContent = sender;

  const textDiv = document.createElement("div");
  textDiv.innerHTML = text;

  // 组装内容容器
  contentDiv.appendChild(senderDiv);
  contentDiv.appendChild(textDiv);

  // 添加头像和内容到消息容器
  if (cls.includes('bot')) {
    // AI消息：头像在左，内容在右
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(contentDiv);
  } else {
    // 用户消息：内容在左，头像在右
    msgDiv.appendChild(contentDiv);
    msgDiv.appendChild(avatar);
  }

  // 添加到消息列表并滚动到底部（原有代码）
  const messagesContainer = document.getElementById('messages');
  messagesContainer.appendChild(msgDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  return msgDiv;
}

// 设置等待状态（禁用/启用按钮）
function setWaiting(waiting) {
  isWaiting = waiting;
  const sendBtn = document.getElementById('send-btn');
  const input = document.getElementById('user-input');

  sendBtn.disabled = waiting;
  input.disabled = waiting;

  sendBtn.textContent = waiting ? '发送中....' : '发送';
  if (!waiting) input.focus();
}

// 清空聊天记录
function clearChat() {
  if (confirm('确定要清空聊天记录吗？')) {
    // 调用API清空后端数据库
    fetch('/clear-chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // 清空成功，更新界面
        document.getElementById('messages').innerHTML = `
          <div class="msg bot">
            <div class="msg-content">
              <div class="sender">AI助手</div>
              你好！我是智能聊天机器人，有什么可以帮助你的吗？
            </div>
          </div>
        `;
        conversationHistory = []; // 清空内存中的历史
        document.getElementById('user-input').focus();
        console.log('聊天记录已清空');
      } else {
        console.error('清空失败:', data.error);
        alert('清空聊天记录失败: ' + data.error);
      }
    })
    .catch(error => {
      console.error('清空聊天记录失败:', error);
      alert('清空聊天记录失败，请稍后再试');
    });
  }
}
