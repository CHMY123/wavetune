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

# 初始化OpenAI客户端
api_key = os.environ.get('DEEPSEEK_API_KEY')
if not api_key:
    api_key = "sk-e8e03d5c814048ec82ec6b3827235936"  # 这里应该替换为实际的API密钥

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# 音乐库
MUSIC_LIBRARY = [
    "B站伊丽莎白鼠 - 如何用100秒让张杰感受UP主的爱.mp3",
    "小小阿布 - 悲伤剧情—-伴奏.mp3",
    "格格 - 生日祝福歌.mp3"
]

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 构建消息
        messages = [
            {"role": "system", "content": "你是一个专业的疲劳咨询助手，同时也是音乐推荐专家。你可以为用户提供疲劳咨询和建议，包括：\n1. 分析用户描述的疲劳症状\n2. 提供科学的缓解疲劳的方法\n3. 给出合理的休息和作息建议\n4. 根据用户的情绪和需求推荐合适的音乐\n5. 提供心理健康方面的指导\n请使用专业、友好的语言，给出具体、实用的建议。"},
            {"role": "user", "content": request.message}
        ]
        
        # 调用DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
        )
        
        ai_response = response.choices[0].message.content
        
        # 随机推荐一首音乐
        recommended_music = random.choice(MUSIC_LIBRARY)
        
        return ChatResponse(
            response=ai_response,
            recommended_music=recommended_music
        )
        
    except Exception as e:
        print(f"AI API调用失败: {e}")
        raise HTTPException(status_code=500, detail="AI API调用失败")
