"""
API 接口测试脚本
用于测试后端服务的各个接口功能
"""

import requests
import json
from datetime import datetime

# API 基础URL
BASE_URL = "http://localhost:8000/api"

def test_api():
    """测试所有API接口"""
    print("开始测试 WaveTune API 接口...")
    
    # 测试用户注册接口
    print("\n1. 测试用户注册接口")
    try:
        register_data = {
            "username": "测试用户",
            "student_id": "2022001999",
            "password": "123456",
            "email": "test@example.com",
            "phone": "13800138999"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试用户登录接口
    print("\n2. 测试用户登录接口")
    session_token = None
    try:
        login_data = {
            "student_id": "2022001001",
            "password": "123456",
            "device_info": "Test Client"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        if result.get("code") == 200:
            session_token = result["data"]["session_token"]
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试系统统计接口
    print("\n3. 测试系统统计接口")
    try:
        response = requests.get(f"{BASE_URL}/system/stats")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试用户信息接口
    print("\n4. 测试用户信息接口")
    try:
        response = requests.get(f"{BASE_URL}/user/info?user_id=1")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试音乐推荐接口
    print("\n5. 测试音乐推荐接口")
    try:
        response = requests.get(f"{BASE_URL}/music/recommend?fatigue_level=medium")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试场景列表接口
    print("\n6. 测试场景列表接口")
    try:
        response = requests.get(f"{BASE_URL}/scene/list?user_id=1")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试反馈提交接口
    print("\n7. 测试反馈提交接口")
    try:
        feedback_data = {
            "user_id": 1,
            "feedback_type": "accuracy",
            "content": "测试反馈内容，系统运行正常",
            "score": 5
        }
        response = requests.post(
            f"{BASE_URL}/feedback/submit",
            json=feedback_data
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试反馈历史接口
    print("\n8. 测试反馈历史接口")
    try:
        response = requests.get(f"{BASE_URL}/feedback/history?user_id=1")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试需要认证的接口
    if session_token:
        headers = {"Authorization": f"Bearer {session_token}"}
        
        # 测试获取用户资料接口
        print("\n9. 测试获取用户资料接口")
        try:
            response = requests.get(f"{BASE_URL}/auth/profile?user_id=1", headers=headers)
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"错误: {e}")
        
        # 测试获取用户会话列表接口
        print("\n10. 测试获取用户会话列表接口")
        try:
            response = requests.get(f"{BASE_URL}/auth/sessions?user_id=1", headers=headers)
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"错误: {e}")
        
        # 测试用户登出接口
        print("\n11. 测试用户登出接口")
        try:
            logout_data = {"session_token": session_token}
            response = requests.post(f"{BASE_URL}/auth/logout", json=logout_data)
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"错误: {e}")
    
    print("\nAPI 接口测试完成！")

if __name__ == "__main__":
    test_api()


