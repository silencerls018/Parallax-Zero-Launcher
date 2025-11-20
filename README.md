🚀 Parallax Zero Launcher


Build your own AI Lab on Windows in 1 Click. 一键构建 Windows 本地 AI 实验室


📖 Introduction / 项目介绍

Parallax Zero is a GUI wrapper designed specifically for Windows users participating in the Gradient AI Cluster ecosystem. It solves the complexity of CLI commands, WSL network isolation issues, and environment configuration hurdles.

Parallax Zero 是专为 Windows 用户打造的 Parallax 可视化启动器。它完美解决了命令行操作复杂、WSL 网络隔离（NAT）、以及环境配置繁琐的痛点。让构建本地 AI 集群变得像玩游戏一样简单。

🏆 Built for GradientHQ "Build your own AI Lab" Competition

✨ Key Features / 核心功能

🛠️ Auto WSL Network Fix: Automatically detects WSL NAT isolation and switches to "Mirrored Mode" with one click, allowing LAN devices to connect seamlessly.

智能 WSL 网络修复：一键切换镜像模式，彻底解决局域网无法发现节点的问题。

⚡ Instant Launch: Asynchronous process management ensures the UI never freezes.

极速启动：全异步多线程架构，操作丝般顺滑。

📦 One-Click Dependency Setup: Automatically handles parallax install and environment checks.

全自动依赖管理：自动检测并安装所需的 AI 运行库。

📱 LAN Sharing: Easily share your local AI service to mobile devices on the same WiFi.

局域网共享：一键开启服务，手机平板即可连接使用。

📸 Screenshots / 界面预览

1. The Dashboard / 主控面板

(Manage your Master node, copy Peer IDs, and control services)
(管理主脑节点，一键复制 ID，控制聊天服务)

<img width="1459" height="1078" alt="下载" src="https://github.com/user-attachments/assets/377f6e96-e24b-4042-8e27-b0bec5158606" />


2. Role Selection / 角色选择

(Choose between Master Brain or GPU Worker)
(清晰的双语卡片，选择本机功能)

<img width="911" height="451" alt="image" src="https://github.com/user-attachments/assets/bb1c07ba-a908-481a-aeda-495aaccadad7" />


3. Intelligent Fixes / 智能修复

(Automatically detects missing WSL or Network configurations)
(自动检测环境缺失并引导修复)
<img width="1781" height="1133" alt="image" src="https://github.com/user-attachments/assets/fe7f3474-14d1-4316-8205-3c013e924a48" />



🚀 Getting Started / 如何使用

Prerequisites / 前置要求

Windows 10 or Windows 11

NVIDIA GPU (Recommended for Workers)

Installation / 安装步骤

Go to the Releases page.

Download ParallaxZero.exe.

Right-click and "Run as Administrator". (Required for WSL & Network config)

右键点击 EXE，选择“以管理员身份运行”。

Usage / 使用指南

🧠 As Master (主脑)

Select "MASTER NODE".

The app will auto-start the scheduler.

Copy your Peer ID or Local IP to other devices.

Click "Start Chat" to enable LAN access for your phone/tablet.
<img width="1470" height="1126" alt="image" src="https://github.com/user-attachments/assets/9dfc9a8b-ae61-4764-8c9e-268a1c2ecca3" />


💪 As Worker (算力节点)

Select "WORKER NODE".

Auto Join: If you are on the same WiFi, just click "Auto Join".

Remote Join: Paste the Peer ID from the Master node and click "Connect".

🛠️ Tech Stack / 技术栈

Language: Python 3.13

GUI Framework: CustomTkinter (Modern & High DPI)

Core Logic: subprocess management, winreg for environment paths, urllib for auto-updates.

Pixel Engine: Custom-built ASCII/Block font rendering engine.

👨‍💻 Credits

Built with ❤️ by [oxlyc./] for the Gradient Community.
