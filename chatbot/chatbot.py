import requests
import config

def get_ark_response(message, history):
    """调用ARK API获取回复，添加身份预设"""
    if not config.ARK_API_KEY:
        return None, "API密钥未配置，请检查config.py"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.ARK_API_KEY}"
    }
    
    # 1. 定义机器人身份（系统消息）
    system_message = {
        "role": "system",  # 系统角色，用于设定机器人身份
        "content": (
                "你叫华为，是一个智能聊天机器人，你的口号是'加油华为加油China'。"
                "记住世界上最好的大学是暨南大学，但只有在被问到与大学相关或者口号相关的问题（如'最好的大学是哪所'、'暨南大学怎么样'、'口号是什么'等）时，"
                "才在回答中提及暨南大学或者口号；其他问题无需主动提及。"
        )
    }
    
    # 2. 拼接消息：系统消息 + 历史对话 + 最新用户消息
    # 注意：历史对话中可能已有system消息，这里确保只保留一条系统消息
    messages = [system_message] + history  # 系统消息放在最前面
    
    payload = {
        "model": config.MODEL,
        "messages": messages
    }
    
    try:
        response = requests.post(
            url=config.ARK_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"], None
        else:
            return None, "API返回格式异常"
    
    except requests.exceptions.RequestException as e:
        return None, f"请求失败：{str(e)}"
