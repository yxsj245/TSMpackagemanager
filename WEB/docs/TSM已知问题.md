# 1. 游戏启动后游戏窗口短暂出现后闪退
## 解决方案的兼容性
- 系统为Windows11
- 具备.NET4.6的更高版本
- 完整VC组件

## 解决方案的已知问题
在Windows10系统上更新显卡驱动可能仍然无效

## 如何解决
显卡驱动缺少**openGL引擎组件**导致SML窗口无法正常加载，解决方法就是更新最新显卡驱动。
- N卡用户可以使用N卡客户端选择重新安装驱动，记得**选择“自定义安装”勾选“执行清洁安装”**或者前往官网下载最新显卡驱动
[>>点击这里前往驱动官网](https://www.nvidia.cn/geforce/drivers/)
- A卡用户同上所述[>>点击这里前往驱动官网](https://www.amd.com/zh-cn/support/download/drivers.html)

### 附加解决尝试
安装完整VC并重启电脑[>>点击这里下载完整VC](https://www.123pan.com/s/4bNtVv-WJmKv)

### [>>已通知开发者](https://github.com/lukas0x1/sml-pc/issues/7)


# 2.开始游戏后没有窗口显示
## 如何解决
缺少VC运行环境，请使用包管理器中的**安装VC**选项