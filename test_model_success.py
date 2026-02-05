#!/usr/bin/env python3
"""
测试脚本：如何判断模型调用成功

演示如何通过不同方式判断 STT 和 TTS 模型调用是否成功
"""

import requests
import json
import base64
import sys
from pathlib import Path


class OpenTalkerTester:
    """OpenTalker API 测试工具"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def check_health(self) -> dict:
        """
        方法1: 检查服务健康状态

        返回值说明:
        - status: "healthy" 表示服务正常
        - model.status: "loaded" 表示模型已加载
        - model.model_type: "stt" 或 "tts" 表示当前加载的模型类型
        """
        print("\n" + "=" * 60)
        print("方法1: 检查服务健康状态")
        print("=" * 60)

        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)

            # 判断1: HTTP 状态码
            if response.status_code == 200:
                print("✅ HTTP 状态码: 200 (成功)")
            else:
                print(f"❌ HTTP 状态码: {response.status_code} (失败)")
                return None

            # 判断2: 解析响应内容
            data = response.json()
            print(f"\n响应内容:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            # 判断3: 检查服务状态
            if data.get("status") == "healthy":
                print("\n✅ 服务状态: healthy (健康)")
            else:
                print(f"\n❌ 服务状态: {data.get('status')} (不健康)")

            # 判断4: 检查模型状态
            model_info = data.get("model", {})
            if model_info.get("status") == "loaded":
                print(f"✅ 模型状态: loaded (已加载)")
                print(f"   模型类型: {model_info.get('model_type')}")
                print(f"   模型名称: {model_info.get('model_name')}")
            elif model_info.get("status") == "none":
                print(f"⚠️  模型状态: none (未加载，首次调用时会自动加载)")
            else:
                print(f"❌ 模型状态: {model_info.get('status')} (异常)")

            # 判断5: 检查 GPU 信息（可选）
            gpu_info = data.get("gpu")
            if gpu_info:
                print(f"\n📊 GPU 信息:")
                print(f"   设备: {gpu_info.get('device_name')}")
                print(
                    f"   显存使用: {gpu_info.get('used_memory_mb'):.1f}MB / {gpu_info.get('total_memory_mb'):.1f}MB"
                )
                print(f"   显存利用率: {gpu_info.get('utilization_percent'):.1f}%")
            else:
                print(f"\n⚠️  GPU 信息: 无 (CPU 模式)")

            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return None

    def test_stt(self, audio_file: str) -> dict:
        """
        方法2: 测试 STT (语音转文字) 调用

        成功判断标准:
        1. HTTP 状态码 = 200
        2. 响应包含 "text" 字段
        3. text 字段不为空
        """
        print("\n" + "=" * 60)
        print("方法2: 测试 STT (语音转文字)")
        print("=" * 60)

        if not Path(audio_file).exists():
            print(f"❌ 音频文件不存在: {audio_file}")
            return None

        try:
            # 准备请求
            with open(audio_file, "rb") as f:
                files = {"file": (Path(audio_file).name, f, "audio/wav")}
                data = {"model": "qwen3-asr", "response_format": "json"}

                print(f"📤 发送请求: {audio_file}")
                response = self.session.post(
                    f"{self.base_url}/v1/audio/transcriptions", files=files, data=data, timeout=60
                )

            # 判断1: HTTP 状态码
            print(f"\n📥 HTTP 状态码: {response.status_code}")

            if response.status_code == 200:
                print("✅ 请求成功")
            elif response.status_code == 400:
                print("❌ 请求参数错误")
                print(f"错误详情: {response.json()}")
                return None
            elif response.status_code == 503:
                print("❌ 模型未就绪")
                print(f"错误详情: {response.json()}")
                return None
            elif response.status_code == 500:
                print("❌ 服务器内部错误")
                print(f"错误详情: {response.json()}")
                return None
            else:
                print(f"❌ 未知错误: {response.status_code}")
                return None

            # 判断2: 解析响应
            result = response.json()
            print(f"\n响应内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            # 判断3: 检查 text 字段
            if "text" in result:
                text = result["text"]
                if text:
                    print(f"\n✅ 转录成功!")
                    print(f"   识别文本: {text}")
                    print(f"   文本长度: {len(text)} 字符")
                else:
                    print(f"\n⚠️  转录结果为空 (可能是静音或无法识别)")
            else:
                print(f"\n❌ 响应中没有 'text' 字段")
                return None

            return result

        except requests.exceptions.Timeout:
            print("❌ 请求超时 (可能是模型加载时间过长)")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return None
        except json.JSONDecodeError:
            print(f"❌ 响应不是有效的 JSON")
            print(f"原始响应: {response.text[:200]}")
            return None

    def test_tts(self, text: str, reference_audio: str, output_file: str = "output.wav") -> bool:
        """
        方法3: 测试 TTS (文字转语音) 调用

        成功判断标准:
        1. HTTP 状态码 = 200
        2. Content-Type 是音频格式
        3. 响应内容长度 > 0
        4. 能够保存为音频文件
        """
        print("\n" + "=" * 60)
        print("方法3: 测试 TTS (文字转语音)")
        print("=" * 60)

        if not Path(reference_audio).exists():
            print(f"❌ 参考音频不存在: {reference_audio}")
            return False

        try:
            # 读取参考音频并编码
            with open(reference_audio, "rb") as f:
                voice_data = base64.b64encode(f.read()).decode()

            # 准备请求
            request_data = {
                "model": "indextts-2",
                "input": text,
                "voice": voice_data,
                "response_format": "wav",
            }

            print(f"📤 发送请求:")
            print(f"   文本: {text}")
            print(f"   参考音频: {reference_audio}")
            print(f"   输出格式: wav")

            response = self.session.post(
                f"{self.base_url}/v1/audio/speech", json=request_data, timeout=120
            )

            # 判断1: HTTP 状态码
            print(f"\n📥 HTTP 状态码: {response.status_code}")

            if response.status_code == 200:
                print("✅ 请求成功")
            elif response.status_code == 400:
                print("❌ 请求参数错误")
                print(f"错误详情: {response.json()}")
                return False
            elif response.status_code == 503:
                print("❌ 模型未就绪")
                print(f"错误详情: {response.json()}")
                return False
            elif response.status_code == 500:
                print("❌ 服务器内部错误")
                print(f"错误详情: {response.json()}")
                return False
            else:
                print(f"❌ 未知错误: {response.status_code}")
                return False

            # 判断2: 检查 Content-Type
            content_type = response.headers.get("Content-Type", "")
            print(f"\nContent-Type: {content_type}")

            if "audio" in content_type:
                print("✅ 响应类型正确 (音频)")
            else:
                print(f"❌ 响应类型错误 (期望 audio/*, 实际 {content_type})")
                return False

            # 判断3: 检查内容长度
            audio_bytes = response.content
            audio_size = len(audio_bytes)
            print(f"\n音频大小: {audio_size} 字节 ({audio_size / 1024:.2f} KB)")

            if audio_size > 0:
                print("✅ 音频内容不为空")
            else:
                print("❌ 音频内容为空")
                return False

            # 判断4: 保存文件
            try:
                with open(output_file, "wb") as f:
                    f.write(audio_bytes)
                print(f"\n✅ 音频已保存: {output_file}")

                # 验证文件大小
                saved_size = Path(output_file).stat().st_size
                if saved_size == audio_size:
                    print(f"✅ 文件大小验证通过: {saved_size} 字节")
                else:
                    print(f"⚠️  文件大小不匹配: 期望 {audio_size}, 实际 {saved_size}")

                return True

            except Exception as e:
                print(f"❌ 保存文件失败: {e}")
                return False

        except requests.exceptions.Timeout:
            print("❌ 请求超时 (可能是模型加载时间过长)")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return False

    def test_error_handling(self):
        """
        方法4: 测试错误处理

        验证 API 能够正确返回错误信息
        """
        print("\n" + "=" * 60)
        print("方法4: 测试错误处理")
        print("=" * 60)

        # 测试1: 无效的模型名称
        print("\n测试1: 无效的模型名称")
        try:
            response = self.session.post(
                f"{self.base_url}/v1/audio/transcriptions",
                files={"file": ("test.wav", b"fake audio", "audio/wav")},
                data={"model": "invalid-model"},
                timeout=10,
            )

            if response.status_code == 400:
                print("✅ 正确返回 400 错误")
                error = response.json()
                print(f"   错误类型: {error.get('detail', {}).get('error', {}).get('type')}")
                print(f"   错误信息: {error.get('detail', {}).get('error', {}).get('message')}")
            else:
                print(f"❌ 期望 400, 实际 {response.status_code}")
        except Exception as e:
            print(f"❌ 测试失败: {e}")

        # 测试2: 文件过大
        print("\n测试2: 文件过大 (模拟)")
        print("⚠️  跳过 (需要创建大文件)")

        # 测试3: 无效的音频格式
        print("\n测试3: 无效的音频格式")
        try:
            response = self.session.post(
                f"{self.base_url}/v1/audio/transcriptions",
                files={"file": ("test.txt", b"not an audio file", "text/plain")},
                data={"model": "qwen3-asr"},
                timeout=10,
            )

            if response.status_code in [400, 500]:
                print(f"✅ 正确返回错误 ({response.status_code})")
                try:
                    error = response.json()
                    print(
                        f"   错误信息: {error.get('detail', {}).get('error', {}).get('message', 'N/A')}"
                    )
                except:
                    pass
            else:
                print(f"⚠️  返回状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ 测试失败: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("OpenTalker 模型调用成功判断测试")
    print("=" * 60)

    # 配置
    base_url = "http://localhost:8000"
    test_audio = "test_audio.wav"

    # 检查命令行参数
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"\n服务地址: {base_url}")
    print(f"测试音频: {test_audio}")

    # 创建测试器
    tester = OpenTalkerTester(base_url)

    # 运行测试
    tester.check_health()

    if Path(test_audio).exists():
        tester.test_stt(test_audio)
        tester.test_tts("你好世界", test_audio, "output_test.wav")
    else:
        print(f"\n⚠️  测试音频文件不存在: {test_audio}")
        print("   跳过 STT 和 TTS 测试")

    tester.test_error_handling()

    # 总结
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    print("\n判断模型调用成功的关键指标:")
    print("1. ✅ HTTP 状态码 = 200")
    print("2. ✅ 响应包含预期字段 (text 或音频数据)")
    print("3. ✅ 响应内容不为空")
    print("4. ✅ Content-Type 正确")
    print("5. ✅ 服务健康状态 = healthy")
    print("6. ✅ 模型状态 = loaded")
    print("\n错误情况:")
    print("- ❌ 400: 请求参数错误")
    print("- ❌ 503: 模型未就绪")
    print("- ❌ 500: 服务器内部错误")
    print("- ❌ 超时: 模型加载时间过长或网络问题")


if __name__ == "__main__":
    main()
