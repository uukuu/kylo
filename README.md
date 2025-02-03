# Docly

1. 将本项目克隆到本地
2. 修改 blog-gen.py 中的 CONFIG 配置
3. 执行 docly.bat 即可
4. 有可选参数 '-g' 生成博客 '-d' 上传到 github (需要先配置 github_url, 在 public 目录下新建 github.io 仓库, 默认上传 public 目录下的所有内容) '-s' 启动本地服务器 (默认地址为 http://127.0.0.1:8080, 如需修改请同步修改 docly.bat 中的 SERVER 变量和 blog-gen.py 中的 local_url 变量)
   
   以上参数可以同时使用, 例如:
   ```
   docly -g -d -s
   ```

