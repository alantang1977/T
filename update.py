import requests  
import time  
import re
from collections import defaultdict

def fetch_and_replace(urls):
    # 读取demo.txt中的频道列表，用于过滤
    demo_channels = set()
    try:
        with open('demo.txt', 'r', encoding='UTF-8') as f:
            for line in f:
                line = line.strip()
                if line and ',' in line:
                    # 提取逗号前的频道名称（忽略空链接的情况）
                    channel_name = line.split(',')[0].strip()
                    if channel_name:
                        demo_channels.add(channel_name)
        print(f"成功加载demo.txt中的频道，共{len(demo_channels)}个")
    except FileNotFoundError:
        print("警告：未找到demo.txt文件，将记录所有频道")
    except Exception as e:
        print(f"读取demo.txt时出错：{e}，将记录所有频道")

    # 定义分类规则：(关键词列表, 目标分类)
    category_rules = [
        (['CCTV', '央视', '央视频道'], '央视频道'),
        (['卫视', '湖南卫视', '浙江卫视', '东方卫视', '北京卫视', '江苏卫视', 
          '安徽卫视', '重庆卫视', '四川卫视', '东南卫视', '深圳卫视'], '卫视频道'),
        (['广东', '广州', '珠江', '大湾区'], '广东频道'),
        (['香港', '凤凰', '翡翠', '明珠', 'TVB', 'ViuTV', 'HOYTV'], '香港频道'),
        (['台湾', '三立', '东森', '中天', '华视', '台视'], '台湾频道'),
        (['少儿', '卡通', '动漫', '幼幼', '金鹰', '卡酷', '嘉佳'], '少儿频道'),
        (['电影', '影视频道', 'CHC', '影院'], '影视频道'),
        (['体育', '五星体育', '纬来体育'], '体育频道'),
        (['新闻', '资讯'], '新闻频道'),
        (['动画', '动漫'], '动画频道'),
        (['教育', 'CETV'], '教育频道'),
        (['纪录片', '纪实'], '纪录频道')
    ]

    # 存储分类后的频道 {分类: {频道名: 链接}}
    categorized = defaultdict(dict)
    # 未匹配到规则的频道归入"其他频道"
    other_channels = {}

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
                    # 跳过包含特定关键词的行
                    if any(keyword in line for keyword in ['更新时间', time.strftime("%Y%m%d"), '关于', '解锁', '公众号', '软件库']):
                        continue
                    
                    # 处理特殊字符
                    processed_line = line.replace('_', '').replace('??', '')
                    
                    # 提取频道名称和链接
                    if ',' in processed_line:
                        parts = [p.strip() for p in processed_line.split(',', 1)]
                        channel_name, link = parts[0], parts[1] if len(parts) > 1 else ''
                        
                        # 过滤demo中的频道
                        if channel_name in demo_channels:
                            continue
                        
                        # 跳过空名称或空链接
                        if not channel_name or (not link.startswith(('http://', 'https://')) and link != ''):
                            continue
                    else:
                        continue  # 跳过不符合格式的行

                    # 归类频道
                    category = None
                    for keywords, cat in category_rules:
                        if any(keyword in channel_name for keyword in keywords):
                            category = cat
                            break
                    
                    # 存储频道（去重处理）
                    if category:
                        categorized[category][channel_name] = link
                    else:
                        other_channels[channel_name] = link  # 未匹配规则的归入其他频道

            else:
                print(f"Failed to retrieve {url} with status code {response.status_code}.")

        except requests.exceptions.Timeout:
            print(f"Request to {url} timed out.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while requesting {url}: {e}")

    # 将其他频道加入分类字典
    if other_channels:
        categorized['其他频道'] = other_channels

    # 合并分类并排序
    all_channels = {}
    # 按分类名称排序
    for cat in sorted(categorized.keys()):
        # 按频道名称自然排序（数字按数值，字母按字母表）
        sorted_channels = sorted(categorized[cat].items(), key=lambda x: (
            re.sub(r'(\d+)', lambda m: f'{int(m.group(1)):010d}', x[0].lower()),
            x[0].lower()
        ))
        all_channels[cat] = sorted_channels

    # 保存到文件
    timestamp = time.strftime("%Y%m%d%H%M%S") 
    notice = "注意事项,#genre#\n"+timestamp+"仅供测试自用如有侵权请通知,https://gh.tryxd.cn/https://raw.githubusercontent.com/alantang1977/X/main/Pictures/Robot.mp4\n" 
    
    with open('my.txt', 'w', encoding='UTF-8') as file:
        file.write(notice)
        for category, channels in all_channels.items():
            # 写入分类标题
            file.write(f"\n{category},#genre#\n")
            # 写入该分类下的所有频道
            for name, link in channels:
                file.write(f"{name},{link}\n")

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
