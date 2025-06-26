import openai
import pysrt
import os
import time
from typing import Optional

def translate_srt_openai(input_file: str, output_file: str, target_language: str = '繁體中文', 
                        api_key: Optional[str] = None, delay: float = 1.0):
    """
    使用 OpenAI API 翻譯 SRT 字幕檔案
    
    參數:
    - input_file: 輸入的 SRT 檔案路徑
    - output_file: 輸出的 SRT 檔案路徑  
    - target_language: 目標語言 (預設: 繁體中文)
    - api_key: OpenAI API 金鑰 (可選，也可透過環境變數設定)
    - delay: 每次 API 呼叫間的延遲秒數
    """
    
    # 設定 API 金鑰
    if api_key:
        openai.api_key = api_key
    elif os.getenv('OPENAI_API_KEY'):
        openai.api_key = os.getenv('OPENAI_API_KEY')
    else:
        raise ValueError("請提供 OpenAI API 金鑰，或設定 OPENAI_API_KEY 環境變數")
    
    # 檢查輸入檔案
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"找不到檔案: {input_file}")
    
    try:
        # 讀取 SRT 檔案
        print(f"正在讀取檔案: {input_file}")
        subs = pysrt.open(input_file, encoding='utf-8')
        print(f"總共有 {len(subs)} 條字幕")
        
        successful_translations = 0
        failed_translations = 0
        total_cost_estimate = 0
        
        for i, sub in enumerate(subs):
            try:
                # 跳過空白字幕
                if not sub.text.strip():
                    continue
                
                # 使用新版 OpenAI API 格式
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": f"你是一個專業的翻譯員。請將以下文字翻譯成{target_language}，保持原意、語氣和情感。如果是對話，請保持對話的自然感。"
                        },
                        {
                            "role": "user", 
                            "content": sub.text
                        }
                    ],
                    max_tokens=200,
                    temperature=0.3  # 降低隨機性，提高一致性
                )
                
                # 取得翻譯結果
                translated_text = response.choices[0].message.content.strip()
                sub.text = translated_text
                
                successful_translations += 1
                
                # 估算成本
                total_tokens = response.usage.total_tokens
                cost_estimate = total_tokens * 0.002 / 1000  # GPT-3.5-turbo 價格
                total_cost_estimate += cost_estimate
                
                # 顯示進度
                progress = (i + 1) / len(subs) * 100
                print(f"翻譯進度: {i+1}/{len(subs)} ({progress:.1f}%) | 成功: {successful_translations} | 預估成本: ${total_cost_estimate:.4f}")
                
                # 延遲避免超出 API 限制
                time.sleep(delay)
                
            except Exception as e:
                print(f"翻譯第 {i+1} 條字幕失敗: {e}")
                failed_translations += 1
                # 失敗時保留原文
                continue
        
        # 儲存結果
        print(f"正在儲存到: {output_file}")
        subs.save(output_file, encoding='utf-8')
        
        print(f"\n✅ 翻譯完成!")
        print(f"成功翻譯: {successful_translations} 條")
        print(f"翻譯失敗: {failed_translations} 條")
        print(f"預估總成本: ${total_cost_estimate:.4f} USD")
        print(f"檔案已儲存至: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 處理檔案時發生錯誤: {e}")
        return False

def translate_srt_openai_v1(input_file: str, output_file: str, target_language: str = '繁體中文', 
                           api_key: Optional[str] = None, delay: float = 1.0):
    """
    使用 OpenAI API v1.0+ 新版本格式翻譯 SRT 字幕檔案
    """
    from openai import OpenAI
    
    # 初始化客戶端
    if api_key:
        client = OpenAI(api_key=api_key)
    elif os.getenv('OPENAI_API_KEY'):
        client = OpenAI()
    else:
        raise ValueError("請提供 OpenAI API 金鑰，或設定 OPENAI_API_KEY 環境變數")
    
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"找不到檔案: {input_file}")
    
    try:
        subs = pysrt.open(input_file, encoding='utf-8')
        print(f"總共有 {len(subs)} 條字幕")
        
        successful_translations = 0
        failed_translations = 0
        total_cost_estimate = 0
        
        for i, sub in enumerate(subs):
            try:
                if not sub.text.strip():
                    continue
                
                # 使用新版 API 格式
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": f"你是一個專業的翻譯員。請將以下文字翻譯成{target_language}，保持原意、語氣和情感。"
                        },
                        {
                            "role": "user", 
                            "content": sub.text
                        }
                    ],
                    max_tokens=200,
                    temperature=0.3
                )
                
                translated_text = response.choices[0].message.content.strip()
                sub.text = translated_text
                
                successful_translations += 1
                
                # 估算成本
                total_tokens = response.usage.total_tokens
                cost_estimate = total_tokens * 0.002 / 1000
                total_cost_estimate += cost_estimate
                
                progress = (i + 1) / len(subs) * 100
                print(f"翻譯進度: {i+1}/{len(subs)} ({progress:.1f}%) | 預估成本: ${total_cost_estimate:.4f}")
                
                time.sleep(delay)
                
            except Exception as e:
                print(f"翻譯第 {i+1} 條字幕失敗: {e}")
                failed_translations += 1
                continue
        
        subs.save(output_file, encoding='utf-8')
        
        print(f"\n✅ 翻譯完成!")
        print(f"成功翻譯: {successful_translations} 條")
        print(f"翻譯失敗: {failed_translations} 條")
        print(f"預估總成本: ${total_cost_estimate:.4f} USD")
        
        return True
        
    except Exception as e:
        print(f"❌ 處理檔案時發生錯誤: {e}")
        return False

def batch_translate_srt_openai(input_file: str, output_file: str, target_language: str = '繁體中文',
                              batch_size: int = 5, api_key: Optional[str] = None):
    """
    批次翻譯版本 - 一次翻譯多條字幕，節省成本
    """
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key) if api_key else OpenAI()
    
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"找不到檔案: {input_file}")
    
    try:
        subs = pysrt.open(input_file, encoding='utf-8')
        print(f"總共有 {len(subs)} 條字幕，將以 {batch_size} 條為一批進行翻譯")
        
        total_cost_estimate = 0
        
        for i in range(0, len(subs), batch_size):
            batch_end = min(i + batch_size, len(subs))
            batch = subs[i:batch_end]
            
            # 準備批次文字
            texts_to_translate = []
            for j, sub in enumerate(batch):
                if sub.text.strip():
                    texts_to_translate.append(f"{j+1}. {sub.text}")
            
            if texts_to_translate:
                combined_text = "\n".join(texts_to_translate)
                
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": f"請將以下編號的字幕翻譯成{target_language}，保持編號格式，每行一條字幕："
                            },
                            {
                                "role": "user",
                                "content": combined_text
                            }
                        ],
                        max_tokens=1000,
                        temperature=0.3
                    )
                    
                    translated_lines = response.choices[0].message.content.strip().split('\n')
                    
                    # 分配翻譯結果
                    for j, line in enumerate(translated_lines):
                        if i + j < len(subs) and line.strip():
                            # 移除編號
                            clean_text = line.split('. ', 1)[-1] if '. ' in line else line
                            subs[i + j].text = clean_text.strip()
                    
                    # 估算成本
                    total_tokens = response.usage.total_tokens
                    cost_estimate = total_tokens * 0.002 / 1000
                    total_cost_estimate += cost_estimate
                    
                    print(f"批次 {i//batch_size + 1} 完成 ({i+1}-{batch_end}) | 預估成本: ${total_cost_estimate:.4f}")
                    
                except Exception as e:
                    print(f"批次 {i//batch_size + 1} 翻譯失敗: {e}")
            
            time.sleep(1)
        
        subs.save(output_file, encoding='utf-8')
        print(f"\n✅ 批次翻譯完成! 預估總成本: ${total_cost_estimate:.4f} USD")
        
        return True
        
    except Exception as e:
        print(f"❌ 批次翻譯時發生錯誤: {e}")
        return False

# 使用範例
def main():
    """
    使用範例
    """
    # 設定你的 API 金鑰
    api_key = "your-openai-api-key-here"  # 替換成你的 API 金鑰
    
    # 或者設定環境變數：
    # export OPENAI_API_KEY="your-api-key-here"
    
    input_file = "input.srt"
    output_file = "output_translated.srt"
    
    print("選擇翻譯模式:")
    print("1. 逐條翻譯 (準確度高，成本較高)")
    print("2. 批次翻譯 (速度快，成本較低)")
    
    choice = input("請選擇 (1 或 2): ").strip()
    
    if choice == "2":
        # 批次翻譯
        batch_translate_srt_openai(input_file, output_file, "繁體中文", batch_size=5, api_key=api_key)
    else:
        # 逐條翻譯 (使用新版 API)
        translate_srt_openai_v1(input_file, output_file, "繁體中文", api_key=api_key)

if __name__ == "__main__":
    # 安裝套件: pip install openai pysrt
    main()