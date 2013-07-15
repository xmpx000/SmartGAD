使用说明:

在使用之前，需要安装“google-api-python-client”

功能:
1.跨多profile查询；
2.支持逐天查询或按时间段查询
3.支持代理shadowsocks代理
4.支持多种查询模式：csv输入、调度任务、失败恢复
5.输出为csv格式
6.输出结果在date文件夹中

支持跨多个profile批量查询数据，可以按照一段日期进行查询，某些情况下我们可能需要

1.授权
1.1.访问：https://code.google.com/apis/console。在Services中，打开Analytics API 权限
1.2.在API Access中，创建一个Client ID，Application type==Installed Applications，Installed application type==Other
1.3.下载client_secrets.json文件
1.4.在当前目录运行：python sample_utils.py --noauth_local_webserver，系统会自动下载“analytics.dat”，完成授权


2.查询数据：
2.1.本程序有2个控制文件，一个为input.csv,主要负责查询的输入数据（GA账号、纬度、过滤器等），具体见相关文件。另外一个文件为conf.ini。它负责是否使用代理，查询配置等，相关信息参考config.ini
2.2.运行tool_query_ga_date.py即可获取数据
