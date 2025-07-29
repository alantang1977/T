import requests  
import time  
import re
from collections import defaultdict
from fuzzywuzzy import fuzz  # 需要安装fuzzywuzzy库：pip install fuzzywuzzy

def fetch_and_replace(urls):
    # 读取demo.txt中的频道列表，用于过滤和匹配
    demo_channels = []
    try:
        with open('demo.txt', 'r', encoding='UTF-8') as f:
            for line in f:
                line = line.strip()
                if line and ',' in line:
                    channel_name = line.split(',')[0].strip()
                    if channel_name:
                        demo_channels.append(channel_name)
        print(f"成功加载demo.txt中的频道，共{len(demo_channels)}个")
    except FileNotFoundError:
        print("错误：未找到demo.txt文件，无法继续执行")
        return
    except Exception as e:
        print(f"读取demo.txt时出错：{e}，无法继续执行")
        return

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

    # 存储匹配到的demo频道 {基准频道名: {分类: 链接}}
    matched_channels = defaultdict(lambda: defaultdict(str))

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
                        
                        # 跳过空名称或空链接
                        if not channel_name or (not link.startswith(('http://', 'https://')) and link != ''):
                            continue
                    else:
                        continue  # 跳过不符合格式的行

                    # 模糊匹配demo中的频道（相似度阈值设为70，可调整）
                    best_match = None
                    best_score = 0
                    for demo_name in demo_channels:
                        score = fuzz.partial_ratio(channel_name, demo_name)
                        if score > best_score and score >= 70:
                            best_score = score
                            best_match = demo_name

                    if best_match:
                        # 确定分类
                        category = None
                        for keywords, cat in category_rules:
                            if any(keyword in best_match for keyword in keywords):
                                category = cat
                                break
                        if not category:
                            category = '其他频道'

                        # 只保留第一个匹配的有效链接
                        if not matched_channels[best_match][category]:
                            matched_channels[best_match][category] = link

            else:
                print(f"Failed to retrieve {url} with status code {response.status_code}.")

        except requests.exceptions.Timeout:
            print(f"Request to {url} timed out.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while requesting {url}: {e}")

    # 整理输出格式
    all_channels = defaultdict(list)
    for base_name, cat_links in matched_channels.items():
        for category, link in cat_links.items():
            all_channels[category].append((base_name, link))

    # 排序处理
    sorted_channels = {}
    for cat in sorted(all_channels.keys()):
        # 按频道名称自然排序
        sorted_items = sorted(all_channels[cat], key=lambda x: (
            re.sub(r'(\d+)', lambda m: f'{int(m.group(1)):010d}', x[0].lower()),
            x[0].lower()
        ))
        sorted_channels[cat] = sorted_items

    # 保存到文件
    timestamp = time.strftime("%Y%m%d%H%M%S") 
    notice = "注意事项,#genre#\n"+timestamp+"仅供测试自用如有侵权请通知,https://gh.tryxd.cn/https://raw.githubusercontent.com/alantang1977/X/main/Pictures/Robot.mp4\n" 
    
    with open('my.txt', 'w', encoding='UTF-8') as file:
        file.write(notice)
        for category, channels in sorted_channels.items():
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
