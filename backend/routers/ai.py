from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from openai import OpenAI
import random

router = APIRouter(prefix="/api/ai", tags=["ai"])

# 定义请求和响应模型
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    recommended_music: str = None

# 音乐库
MUSIC_LIBRARY = [
    "放松钢琴曲 - 清晨的阳光",
    "自然白噪音 - 雨声",
    "冥想音乐 - 宁静心灵",
    "古典音乐 - 莫扎特小夜曲",
    "轻音乐 - 山间溪流"
]

# 初始化OpenAI客户端
client = None
# 直接设置API密钥
api_key = "sk-e8e03d5c814048ec82ec6b3827235936"
try:
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )
    print("OpenAI客户端初始化成功")
except Exception as e:
    print(f"初始化OpenAI客户端失败: {e}")
    client = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 构建消息
        messages = [
            {"role": "system", "content": "你是一个专业的疲劳咨询助手，同时也是音乐推荐专家。你可以为用户提供疲劳咨询和建议，包括：\n1. 分析用户描述的疲劳症状\n2. 提供科学的缓解疲劳的方法\n3. 给出合理的休息和作息建议\n4. 根据用户的情绪和需求推荐合适的音乐\n5. 提供心理健康方面的指导\n请使用专业、友好的语言，给出具体、实用的建议。"},
            {"role": "user", "content": request.message}
        ]
        
        ai_response = ""
        
        # 尝试调用DeepSeek API
        if client:
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    stream=False
                )
                ai_response = response.choices[0].message.content
            except Exception as e:
                print(f"AI API调用失败: {e}")
                # API调用失败时使用模拟响应
                ai_response = "感谢您的提问！我是您的AI助手，很高兴为您服务。\n\n针对您的问题，我建议您：\n\n1. 适当休息，保持良好的作息习惯\n2. 进行适量的运动，如散步、瑜伽等\n3. 保持充足的水分摄入\n4. 尝试听一些放松的音乐来缓解疲劳\n\n如果您有更具体的问题，欢迎随时向我咨询！"
        else:
            # 没有API密钥时使用模拟响应
            ai_response = "感谢您的提问！我是您的AI助手，很高兴为您服务。\n\n针对您的问题，我建议您：\n\n1. 适当休息，保持良好的作息习惯\n2. 进行适量的运动，如散步、瑜伽等\n3. 保持充足的水分摄入\n4. 尝试听一些放松的音乐来缓解疲劳\n\n如果您有更具体的问题，欢迎随时向我咨询！"
        
        # 随机推荐一首音乐
        recommended_music = random.choice(MUSIC_LIBRARY)
        
        return ChatResponse(
            response=ai_response,
            recommended_music=recommended_music
        )
        
    except Exception as e:
        print(f"处理聊天请求失败: {e}")
        # 即使发生异常，也返回模拟响应
        return ChatResponse(
            response="感谢您的提问！我是您的AI助手，很高兴为您服务。\n\n针对您的问题，我建议您：\n\n1. 适当休息，保持良好的作息习惯\n2. 进行适量的运动，如散步、瑜伽等\n3. 保持充足的水分摄入\n4. 尝试听一些放松的音乐来缓解疲劳\n\n如果您有更具体的问题，欢迎随时向我咨询！",
            recommended_music=random.choice(MUSIC_LIBRARY)
        )
