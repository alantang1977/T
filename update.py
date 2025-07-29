import requests  
import time  
import re
from collections import defaultdict  # 用于按分类存储频道

def fetch_and_replace(urls):  
    # 1. 定义分类规则：{分类名称: [关键词列表]}，优化相似名称归类
    CATEGORY_RULES = {
        "央视频道": ["CCTV", "中央", "央视", "cctv"],
        "卫视频道": ["卫视", "江苏台", "浙江台", "北京台", "东方台", "湖南卫视", "安徽卫视", 
                   "广东卫视", "山东卫视", "湖北卫视", "江西卫视", "四川卫视"],
        "地方频道": ["绵阳", "宜宾", "广元", "绍兴", "温州", "舟山", "深圳", "广州", "上海", 
                   "重庆", "天津", "南京", "杭州", "成都", "武汉", "西安"],
        "体育频道": ["体育", "足球", "篮球", "垂钓", "围棋", "五星体育", "高尔夫", "网球", 
                   "羽毛球", "乒乓球", "搏击", "赛车"],
        "影视动画": ["电影", "电视剧", "卡通", "动画", "金鹰卡通", "卡酷动画", "动漫", 
                   "影院", "剧场", "剧集", "少儿", "儿童"],
        "新闻资讯": ["新闻", "资讯", "新华", "国际", "纪实", "CGTN", "财经", "法治", 
                   "时事", "评论"],
        "香港地区": ["香港", "凤凰", "TVB", "翡翠台", "明珠台", "本港台", "国际台", 
                   "亚视", "香港台", "now tv", "viu", "美亚", "耀才财经", "星光"],
        "台湾地区": ["台湾", "大爱", "TVBS", "中天", "纬来", "龍華", "三立", "民视", 
                   "华视", "中视", "公视", "东森", "年代", "非凡", "番薯", "唯心", 
                   "人间卫视", "生命电视", "PTS"]
    }
    DEFAULT_CATEGORY = "其他频道"  # 未匹配到的频道归入此类

    # 2. 存储分类后的频道（去重）
    categorized_channels = defaultdict(set)  # {分类: {频道行1, 频道行2, ...}}
    seen_lines = set()  # 全局去重（避免不同分类重复）

    # 3. 编译正则表达式模式以提高匹配效率
    category_patterns = {}
    for cat, keywords in CATEGORY_RULES.items():
        # 创建不区分大小写的正则表达式模式
        pattern = re.compile(r'|'.join(re.escape(keyword) for keyword in keywords), re.IGNORECASE)
        category_patterns[cat] = pattern

    for url in urls:  
        try:  
            start_time = time.time()  
            response = requests.get(url, timeout=15)  
            end_time = time.time()  
            elapsed_time = end_time - start_time
            print(f"Request to {url} took {elapsed_time:.2f} seconds.")  

            if response.status_code == 200:
                response.encoding = 'utf-8'
                content = response.text  

                for line in content.splitlines():  
                    # 过滤无效行
                    if '更新时间' in line or time.strftime("%Y%m%d") in line or '关于' in line or '解锁' in line or '公众号' in line or '软件库' in line:
                        continue
                    # 处理特殊字符
                    processed_line = line.replace('_', '').replace('??', '')
                    if not processed_line.strip():  # 跳过空行
                        continue
                    # 全局去重
                    if processed_line in seen_lines:
                        continue
                    seen_lines.add(processed_line)

                    # 提取频道名（通常在逗号前）
                    channel_name = processed_line.split(',')[0].strip() if ',' in processed_line else processed_line
                    category = DEFAULT_CATEGORY

                    # 优先匹配地区分类（香港、台湾）以确保正确归类
                    for cat in ["香港地区", "台湾地区"]:
                        if category_patterns[cat].search(channel_name):
                            category = cat
                            break
                    
                    # 若未匹配地区分类，则匹配其他分类
                    if category == DEFAULT_CATEGORY:
                        for cat in CATEGORY_RULES:
                            if cat in ["香港地区", "台湾地区"]:
                                continue  # 已单独处理，跳过
                            if category_patterns[cat].search(channel_name):
                                category = cat
                                break

                    categorized_channels[category].add(processed_line)

            else:  
                print(f"Failed to retrieve {url} with status code {response.status_code}.")  

        except requests.exceptions.Timeout:  
            print(f"Request to {url} timed out.")  
        except requests.exceptions.RequestException as e:  
            print(f"An error occurred while requesting {url}: {e}")  

    # 4. 按分类输出到文件
    timestamp = time.strftime("%Y%m%d%H%M%S") 
    notice = "注意事项,#genre#\n"+timestamp+"仅供测试自用如有侵权请通知,http://rihou.cc:555/mp4?id=lndjll.mp4\n" 
    
    with open('my.txt', 'w', encoding='UTF-8') as file:
        file.write(notice)
        # 按预设顺序输出分类（地区分类优先展示）
        output_order = [
            "央视频道", "卫视频道", "地方频道", 
            "香港地区", "台湾地区",  # 地区分类位置
            "体育频道", "影视动画", "新闻资讯", 
            DEFAULT_CATEGORY
        ]
        for category in output_order:
            if category in categorized_channels and categorized_channels[category]:
                # 写入分类标识和频道数量
                channel_count = len(categorized_channels[category])
                file.write(f"{category},#genre#（共{channel_count}个频道）\n")
                # 写入该分类下的所有频道（按名称排序）
                for line in sorted(categorized_channels[category], 
                                  key=lambda x: x.split(',')[0].strip()):
                    file.write(line + '\n')
                file.write('\n')  # 分类间空行分隔

if __name__ == "__main__":  
    urls = [
        'https://smart.pendy.dpdns.org/m3u/Smart.m3u',  
        'http://rihou.cc:555/gggg.nzk',
        'http://ox.my.to/8/3199728.txt',
        'https://raw.githubusercontent.com/jack2713/my/refs/heads/main/TMP/TMP1.txt',
        'https://raw.githubusercontent.com/kimwang1978/collect-tv-txt/main/merged_output.txt',
        'https://raw.githubusercontent.com/jack2713/my/refs/heads/main/my03.txt',
        'https://qu.ax/MWZsS.txt',
        'http://gg.7749.org/z/i/gdss.txt',
    ]  
    fetch_and_replace(urls)
