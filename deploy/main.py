#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能媒体重命名系统 - 精简部署版本
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
from pathlib import Path

app = FastAPI(title="智能媒体重命名系统", version="1.0.0")

# 创建静态文件目录
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    """首页"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>智能媒体重命名系统</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .upload-area {
                border: 2px dashed #ccc;
                padding: 40px;
                text-align: center;
                margin: 20px 0;
                border-radius: 5px;
                cursor: pointer;
            }
            .upload-area:hover {
                border-color: #007bff;
            }
            .btn {
                background: #007bff;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            .btn:hover {
                background: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 智能媒体重命名系统</h1>
            <p>欢迎使用智能媒体重命名系统！请上传您的媒体文件进行智能重命名。</p>
            
            <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                <h3>📁 点击选择文件或拖拽文件到这里</h3>
                <p>支持图片、视频、音频文件</p>
            </div>
            
            <input type="file" id="fileInput" style="display: none;" onchange="uploadFile()">
            
            <div id="result" style="margin-top: 20px;"></div>
        </div>

        <script>
            async function uploadFile() {
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                
                if (!file) return;
                
                const formData = new FormData();
                formData.append('file', file);
                
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<p>正在上传文件...</p>';
                
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 5px;">
                                <h4>✅ 上传成功！</h4>
                                <p><strong>文件名：</strong> ${data.filename}</p>
                                <p><strong>消息：</strong> ${data.message}</p>
                                <p><strong>文件路径：</strong> ${data.file_path}</p>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `
                            <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px;">
                                <h4>❌ 上传失败</h4>
                                <p>${data.detail}</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `
                        <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px;">
                            <h4>❌ 网络错误</h4>
                            <p>请检查网络连接</p>
                        </div>
                    `;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件"""
    try:
        # 保存上传的文件
        file_location = f"static/uploads/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        
        with open(file_location, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "filename": file.filename,
            "message": "文件上传成功",
            "file_path": file_location
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "智能媒体重命名系统"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090, log_level="info")