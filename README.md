## CAI - 自然语言转PowerShell工具

### 使用方法：
1. 设置DeepSeek API key（可选，用于AI生成命令）：
   cai.exe --set "your_deepseek_api_key_here"

2. 执行命令：
   cai.exe "查看列表"
   cai.exe "查看当前目录的文件"
   cai.exe "显示网络配置"
   cai.exe "查看系统信息"

![](./doc/img/use.gif)

3. 只显示命令不执行：
   cai.exe "查看当前目录的文件" --dry-run

### 功能说明：
- 支持DeepSeek AI API生成PowerShell命令（需要API key）
- 如果API调用失败或SSL不可用，会自动回退到本地命令映射
- API key保存在.env文件中，只需设置一次
- 当前版本已优化SSL兼容性，在大多数Windows环境下都能正常工作

### 支持的本地指令：
- 查看列表 / 显示列表 / 列出文件
- 查看当前目录的文件
- 列出子目录
- 查看系统信息
- 显示网络配置
- 查看环境变量
- 查看运行进程
- 查看服务
- 以及其他通过AI生成的PowerShell命令

### 注意事项：
- 如果看到"SSL模块不可用"的警告，这是正常的，工具会自动使用本地命令映射
- 要使用AI功能，请设置DeepSeek API key
- 文件大小：约11MB
- 版本：2.1 (SSL优化版)
