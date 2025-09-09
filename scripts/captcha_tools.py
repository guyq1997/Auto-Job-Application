#!/usr/bin/env python3
"""
CAPTCHA Recognition Tools Module
CAPTCHA识别工具模块 - 专门处理各种验证码识别
"""

import os
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

try:
    from browser_use import Tools
    from browser_use.agent.views import ActionResult
    from openai import OpenAI
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ 缺少依赖库: {e}")
    print("请运行: pip install -r requirements.txt")
    exit(1)

# 加载环境变量
load_dotenv()

class CaptchaRecognitionAction(BaseModel):
    """CAPTCHA识别工具参数模型"""
    captcha_type: str = Field(default="text", description="CAPTCHA类型: text(文字), math(数学), recaptcha(图像选择), slider(滑块)")
    filename: str = Field(default="captcha.png", description="保存截图的文件名")
    custom_prompt: str = Field(default="", description="自定义识别提示词")

class HCaptchaSliderAction(BaseModel):
    """hCaptcha滑块验证码专用识别工具参数模型"""
    filename: str = Field(default="hcaptcha_slider.png", description="保存截图的文件名")

class CaptchaTools:
    """CAPTCHA工具集合类"""
    
    def __init__(self, bot_instance=None):
        """
        初始化CAPTCHA工具
        
        Args:
            bot_instance: 浏览器自动化机器人实例，用于访问浏览器
        """
        self.bot_instance = bot_instance
        self.tools = self._create_tools()
    
    def get_tools(self):
        """获取工具集合"""
        return self.tools
    
    def _get_browser_page(self, browser_session):
        """获取浏览器页面实例"""
        page = None
        
        # 优先方式：通过bot_instance直接访问浏览器
        if self.bot_instance and self.bot_instance.browser and hasattr(self.bot_instance.browser, 'page'):
            page = self.bot_instance.browser.page
            print("🔍 使用bot_instance.browser.page进行截图")
        
        # 备用方式1: 通过browser_session.browser.page
        elif hasattr(browser_session, 'browser') and browser_session.browser:
            if hasattr(browser_session.browser, 'page'):
                page = browser_session.browser.page
                print("🔍 使用browser_session.browser.page进行截图")
            elif hasattr(browser_session.browser, 'pages') and browser_session.browser.pages:
                page = browser_session.browser.pages[0]
                print("🔍 使用browser_session.browser.pages[0]进行截图")
        
        # 备用方式2: 直接通过browser_session.page
        elif hasattr(browser_session, 'page'):
            page = browser_session.page
            print("🔍 使用browser_session.page进行截图")
        
        # 备用方式3: 通过agent的browser_session
        elif hasattr(browser_session, 'browser_session') and hasattr(browser_session.browser_session, 'browser'):
            if hasattr(browser_session.browser_session.browser, 'page'):
                page = browser_session.browser_session.browser.page
                print("🔍 使用browser_session.browser_session.browser.page进行截图")
        
        return page
    
    def _create_tools(self):
        """创建CAPTCHA工具集合"""
        tools = Tools()
        
        @tools.registry.action(
            "识别当前页面中的CAPTCHA验证码。自动截图并使用AI识别，返回验证码答案。支持文字、数学、图像选择、滑块等类型。",
            param_model=CaptchaRecognitionAction,
        )
        async def recognize_captcha(params: CaptchaRecognitionAction, browser_session) -> ActionResult:
            """
            CAPTCHA识别工具：自动截图并识别验证码
            一步完成截图 + AI识别，直接返回验证码答案
            """
            try:
                # 确保screenshots目录存在
                screenshots_dir = Path("screenshots")
                screenshots_dir.mkdir(exist_ok=True)
                
                # 生成带时间戳的文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = Path(params.filename).stem
                extension = Path(params.filename).suffix or ".png"
                screenshot_filename = f"{base_name}_{timestamp}{extension}"
                screenshot_path = screenshots_dir / screenshot_filename
                
                # 第一步：截图
                page = self._get_browser_page(browser_session)
                
                if page:
                    # 执行截图
                    await page.screenshot(path=str(screenshot_path), full_page=True)
                    print(f"📸 已截图保存: {screenshot_path}")
                else:
                    # 详细调试信息
                    print("🔍 调试信息:")
                    if self.bot_instance:
                        print(f"   bot_instance.browser: {self.bot_instance.browser}")
                    print(f"   browser_session类型: {type(browser_session)}")
                    if hasattr(browser_session, '__dict__'):
                        print(f"   browser_session属性: {list(browser_session.__dict__.keys())}")
                    return ActionResult(error="❌ 无法访问浏览器实例进行截图。请确保浏览器会话正常运行。")
                
                # 第二步：读取截图并转换为base64
                with open(screenshot_path, 'rb') as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                
                # 第三步：根据CAPTCHA类型构建识别提示词
                captcha_prompts = {
                    "text": "请识别这张图片中的验证码文字。只返回验证码的文字内容，不要包含其他解释。如果是字母和数字的组合，请准确识别每个字符。",
                    "math": "请计算这张图片中显示的数学算式，并返回计算结果。只返回最终的数字答案，不要包含计算过程。",
                    "recaptcha": "请分析这张reCAPTCHA图片，识别需要选择的图像内容。请详细描述你看到的内容和建议点击哪些图片。",
                    "slider": """请分析这张hCaptcha滑块验证码图片：
1. 仔细观察拼图缺口的位置和形状
2. 找到需要拖动的滑块元素
3. 分析滑块应该移动到缺口位置的距离
4. 返回具体的操作指导，格式为：'将滑块向右拖动约X像素到缺口位置'
请提供准确的拖动距离和方向。"""
                }
                
                # 使用自定义提示词或默认提示词
                analysis_prompt = params.custom_prompt or captcha_prompts.get(params.captcha_type, captcha_prompts["text"])
                
                # 第四步：调用OpenAI Vision API进行识别
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                response = client.chat.completions.create(
                    model="gpt-4o",  # 使用最新的视觉模型
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": analysis_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{image_data}",
                                        "detail": "high"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=300,
                    temperature=0.1  # 低温度确保结果一致性
                )
                
                # 提取识别结果
                captcha_result = response.choices[0].message.content.strip()
                
                success_msg = f"🤖 CAPTCHA识别成功 ({params.captcha_type}): {captcha_result}"
                print(success_msg)
                
                return ActionResult(
                    extracted_content=f"CAPTCHA答案: {captcha_result}",
                    include_in_memory=True,
                    long_term_memory=f"CAPTCHA识别: {captcha_result} (类型: {params.captcha_type}, 截图: {screenshot_filename})"
                )
                    
            except Exception as e:
                error_msg = f"❌ CAPTCHA识别失败: {str(e)}"
                print(error_msg)
                return ActionResult(error=error_msg)
        
        @tools.registry.action(
            "专门识别hCaptcha滑块验证码。自动截图并分析滑块拖动位置，返回详细的操作指导。",
            param_model=HCaptchaSliderAction,
        )
        async def solve_hcaptcha_slider(params: HCaptchaSliderAction, browser_session) -> ActionResult:
            """
            hCaptcha滑块验证码专用工具：专门处理hCaptcha滑块拖动验证
            """
            try:
                # 确保screenshots目录存在
                screenshots_dir = Path("screenshots")
                screenshots_dir.mkdir(exist_ok=True)
                
                # 生成带时间戳的文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = Path(params.filename).stem
                extension = Path(params.filename).suffix or ".png"
                screenshot_filename = f"{base_name}_{timestamp}{extension}"
                screenshot_path = screenshots_dir / screenshot_filename
                
                # 截图
                page = self._get_browser_page(browser_session)
                
                if page:
                    await page.screenshot(path=str(screenshot_path), full_page=True)
                    print(f"📸 hCaptcha截图保存: {screenshot_path}")
                else:
                    return ActionResult(error="❌ 无法访问浏览器进行hCaptcha截图")
                
                # 读取截图并转换为base64
                with open(screenshot_path, 'rb') as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                
                # hCaptcha专用分析提示词
                hcaptcha_prompt = """请分析这张hCaptcha滑块验证码截图：

1. **识别验证码类型**：确认这是hCaptcha滑块验证码
2. **定位拼图缺口**：找到背景图片中的拼图缺口位置
3. **定位滑块**：找到需要拖动的滑块元素位置
4. **计算拖动距离**：测量从滑块当前位置到缺口位置的像素距离
5. **提供操作指导**：返回具体的拖动操作

请返回如下格式的结果：
- 验证码类型：hCaptcha滑块验证码
- 缺口位置：距离左边缘约X像素
- 滑块当前位置：距离左边缘约Y像素  
- 需要拖动距离：向右拖动约Z像素
- 操作建议：将滑块向右拖动Z像素到缺口位置

请提供准确的数值和清晰的操作指导。"""
                
                # 调用OpenAI Vision API
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": hcaptcha_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{image_data}",
                                        "detail": "high"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=500,
                    temperature=0.1
                )
                
                # 提取识别结果
                hcaptcha_result = response.choices[0].message.content.strip()
                
                success_msg = f"🎯 hCaptcha滑块识别成功:\n{hcaptcha_result}"
                print(success_msg)
                
                return ActionResult(
                    extracted_content=f"hCaptcha滑块分析结果:\n{hcaptcha_result}",
                    include_in_memory=True,
                    long_term_memory=f"hCaptcha滑块已识别，截图: {screenshot_filename}"
                )
                
            except Exception as e:
                error_msg = f"❌ hCaptcha滑块识别失败: {str(e)}"
                print(error_msg)
                return ActionResult(error=error_msg)
        
        return tools

# 便利函数
def create_captcha_tools(bot_instance=None):
    """创建CAPTCHA工具实例"""
    return CaptchaTools(bot_instance=bot_instance)

if __name__ == "__main__":
    # 测试代码
    print("🧪 CAPTCHA工具模块加载成功")
    tools = create_captcha_tools()
    print(f"✅ 可用工具数量: {len(tools.get_tools().registry._actions)}")
