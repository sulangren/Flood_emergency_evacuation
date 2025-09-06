**一、应用介绍**\
本应用为基于WebGIS的洪水紧急疏散与模拟洪灾系统。

**注意**：此应用并不是完整版，因为涉及到高德地图的密匙问题、数据库的构建和最优数量矩阵的构建等问题，因此不能够上手直接运行，请自行更该相应位置后再进行运行。

**二、所用工具**\
1.程序所用框架：本应用前端所使用的是高德Api作为地图服务，前端框架为Vue，后端框架为Django，数据库为PostgreSQL及扩展PostGIS，桌面应用端选的是pyqt6及其样式库PyQt-Fluent-Widgets，洪水模拟模块采用的是cesium进行的木笔

2.程序所调用库：\
前端：\
Ant Design：主要作用是对页面的设计。

HTTP请求库:\
Axios：用以发送请求。

后端:\
Django REST framework: 一个强大的和灵活的工具包，用于构建 Web API。\
django.contrib.gis: Django 的地理信息系统（GIS）扩展，用于处理地理数据。\
django-cors-headers: 用于处理跨源资源共享（CORS）的中间件。\
djangorestframework-simplejwt: 提供 JSON Web Token（JWT）认证支持的 Django REST framework 扩展。\
djangorestframework-gis: Django REST framework 的 GIS 扩展，用于处理地理数据的序列化和反序列化。\
Pandas: 一个强大的数据分析和操作库，用于处理表格数据。\
Heapyq: Python 标准库中的一个模块，提供了堆队列算法，也称为优先队列算法。\
GDAL: 一个用于读写栅格和矢量地理空间数据的库，通过 GDAL_LIBRARY_PATH 配置在 Django 中使用。\
PyQt-Fluent-Widgets: 一款pyQt6的样式库。\
cesium：用于构建和模拟三维场景的。\

**三、具体功能（仅展示了qt端的，web端的与其布局类似）**\
1.框架页面：主要显示标题、logo、各个功能页面的索引、登入页面和注册按钮。

2.登入界面：Qt端由于时间问题，所采用了最基本的布局方式。\
![image](https://github.com/sulangren/Flood_emergency_evacuation/blob/master/data/image/01.png)
            web端所采用登入界面嵌入到了框架页面，以弹窗的形式展示。\
            (图片待补充）\
3.首页：Qt端采用滚动展示模块，对首页照片进行循环展示。\
![image](https://github.com/sulangren/Flood_emergency_evacuation/blob/master/data/image/02.png)
        web端采取Ant Design的Carousel（走马灯）控件，对基础本的功能进行滚动式播放。\
        (图片待补充）\
4.注册页面：qt端点击注册按钮，在浏览器中所打开的注册页面所采用的和web端类似的注册页面，但是略有不同，qt端是注册后三秒内关闭网页，而web端则是返回web主页。\
        (图片待补充) \

5.天气显示：qt端的布局和web端类似，我们采用两种显示方式，第一种为调用高德api组件，进行的天气显示，第二种为每隔一小时向墨迹天气api索取当前地区的天气数据，进行整合储存到数据库中，访问天气时从数据库中调出当前天气信息。\
![image](https://github.com/sulangren/Flood_emergency_evacuation/blob/master/data/image/03.png)
![image](https://github.com/sulangren/Flood_emergency_evacuation/blob/master/data/image/04.png)
以下为数据库中存储的天气信息示例图\
![image](https://github.com/sulangren/Flood_emergency_evacuation/blob/master/data/image/05.png)
以下为天气展示模块，它能够展示所有数据库中存储的历史天气情况，如果遇到存储的与实际的天气情况不符，请探查墨迹天气api，因为我在后端的位置上还存储了一份从墨迹天气api中保存的天气信息。\
![image](https://github.com/sulangren/Flood_emergency_evacuation/blob/master/data/image/07.png)

6.紧急避险：该模块允许人员点击屏幕或者点击获取当前位置，进行快速导航到附近的避难场所，一旦获取到当前位置时，则无需其他操作立即导航到附近最近的避难场所，当然，你还可以选择你喜欢的避难场所。\
![image](https://github.com/sulangren/Flood_emergency_evacuation/blob/master/data/image/06.png)

7.洪灾模拟：以下是利用cesium以郑州市为例的洪水水淹模拟（展示了qt端的）。\
![image](https://github.com/sulangren/Flood_emergency_evacuation/blob/master/data/image/08.png)

8.自助互助模块：对于有余力的热心市民，想要帮助更多人，于是我们就推出此功能，能够让你快速的找到，并合理安排救助路线。\
![image](https://github.com/sulangren/Flood_emergency_evacuation/blob/master/data/image/09.png)

9.系统救助：该模块面向大型救助中心，如红十字会等开发的，主要用于严重受灾地区的紧急救助，通过算法进行计算最紧急救援点，然后合理规划。\
![image](https://github.com/sulangren/Flood_emergency_evacuation/blob/master/data/image/10.png)

**四、数据库结构**\
![image](https://github.com/sulangren/Flood_emergency_evacuation/blob/master/data/image/11.png)

**五、补充**\
如果想要直接使用的话，请记得收藏该项目，并表明出处，谢谢。\
作者近段时间比较忙，需要说明文档的话，请等待一段事件，等作者处理完后会更新文档，并发布说明文档。
