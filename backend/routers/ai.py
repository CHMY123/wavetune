from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from openai import OpenAI
import random

router = APIRouter(prefix="/api/ai", tags=["ai"])

# 定义请求和响应模型
class ChatRequest(BaseModel):
    message: str
    history: list = []

class ChatResponse(BaseModel):
    response: str
    recommended_music: str = None

# 音乐库
MUSIC_LIBRARY = [
    "安妮的仙境",
    "森林狂想曲",
    "菊次郎的夏天",
    "Tassel",
    "卡农",
    "梦中的婚礼(钢琴版) - jaycd",
    "Ballade Pour Adeline (水边的阿狄丽娜)",
    "夜曲",
    "夜的钢琴曲",
    "大鱼",
    "千与千寻",
    "《夜色钢琴曲》欢乐颂",
    "罗密欧与朱丽叶",
    "圆舞曲",
    "克罗地亚狂想曲",
    "致爱丽丝",
    "土耳其进行曲",
    "Mystery of love",
    "Lullaby",
    "鸟之诗 (钢琴纯音乐)"
]

# 网站功能
WEBSITE_FEATURES = "WaveTune是一个智能脑疲劳检测系统，主要功能包括：\n1. 脑疲劳检测：通过穿戴设备获取或上传EEG、fNIRS信号数据（csv文件格式）进行疲劳状态检测\n2. 音乐推荐：根据疲劳状态推荐适合的音乐\n3. 2-back实验：通过认知训练游戏评估用户的认知能力\n4. 信号监测：实时监测和分析脑信号\n5. 联邦学习：用户可以贡献数据参与模型训练，保护隐私的同时改进系统\n6. 反馈系统：用户可以提交反馈和建议"

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
            {"role": "system", "content": f"你是WaveTune智能脑疲劳检测系统的专业助手，同时也是音乐推荐专家。\n\n系统信息：\n{WEBSITE_FEATURES}\n\n项目现有音乐库：\n{', '.join(MUSIC_LIBRARY)}\n\n你的职责：\n1. 分析用户描述的疲劳症状\n2. 提供科学的缓解疲劳的方法\n3. 给出合理的休息和作息建议\n4. 根据用户的情绪和需求推荐合适的音乐\n5. 提供系统功能使用指导\n6. 回答用户关于系统的问题\n7. 保持对话的连贯性，记住之前的对话内容\n\n请使用专业、友好的语言，给出具体、实用的建议。"},
        ]
        
        # 添加历史消息
        for msg in request.history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # 添加当前消息
        messages.append({"role": "user", "content": request.message})
        
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
                ai_response = "感谢您的提问！我是WaveTune智能脑疲劳检测系统的AI助手，很高兴为您服务。\n\n针对您的问题，我建议您：\n\n1. 适当休息，保持良好的作息习惯\n2. 进行适量的运动，如散步、瑜伽等\n3. 保持充足的水分摄入\n4. 尝试听一些放松的音乐来缓解疲劳\n\n如果您有更具体的问题，欢迎随时向我咨询！"
        else:
            # 没有API密钥时使用模拟响应
            ai_response = "感谢您的提问！我是WaveTune智能脑疲劳检测系统的AI助手，很高兴为您服务。\n\n针对您的问题，我建议您：\n\n1. 适当休息，保持良好的作息习惯\n2. 进行适量的运动，如散步、瑜伽等\n3. 保持充足的水分摄入\n4. 尝试听一些放松的音乐来缓解疲劳\n\n如果您有更具体的问题，欢迎随时向我咨询！"
        
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
            response="感谢您的提问！我是WaveTune智能脑疲劳检测系统的AI助手，很高兴为您服务。\n\n针对您的问题，我建议您：\n\n1. 适当休息，保持良好的作息习惯\n2. 进行适量的运动，如散步、瑜伽等\n3. 保持充足的水分摄入\n4. 尝试听一些放松的音乐来缓解疲劳\n\n如果您有更具体的问题，欢迎随时向我咨询！",
            recommended_music=random.choice(MUSIC_LIBRARY)
        )
