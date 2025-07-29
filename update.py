import requests  
import time  
import re
from fuzzywuzzy import fuzz  # 需安装：pip install fuzzywuzzy python-Levenshtein
from collections import defaultdict

# 预设主要分类关键词（可根据实际频道类型扩展）
CATEGORY_KEYWORDS = {
    "央视": ["cctv", "央视", "中央"],
    "卫视": ["卫视", "省级台"],
    "地方台": ["省", "市", "县", "区", "地方"],
    "电影": ["电影", "影院", "mov", "film"],
    "电视剧": ["剧集", "电视剧", "连续剧", " drama"],
    "动漫": ["动漫", "动画", "卡通", "anime", "cartoon"],
    "体育": ["体育", "赛事", "球", "sport", "match"],
    "新闻": ["新闻", "资讯", "news"],
    "教育": ["教育", "教学", "学习", "edu"],
    "少儿": ["少儿", "儿童", "kid", "children"],
    "国际": ["国际", "foreign", "global", "overseas"]
}

def get_category(channel_name):
    """根据频道名判断分类（优先关键词匹配，再模糊匹配）"""
    name_lower = channel_name.lower()
    # 1. 关键词匹配
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in name_lower:
                return category
    # 2. 无关键词时返回"其他"
    return "其他"

def group_similar_channels(channels, threshold=70):
    """将相似名称的频道归为同一子分类（基于模糊匹配）"""
    groups = []
    ungrouped = channels.copy()
    
    while ungrouped:
        current = ungrouped.pop(0)
        group = [current]
        # 遍历剩余未分组频道，寻找相似名称
        to_remove = []
        for i, channel in enumerate(ungrouped):
            # 计算名称相似度
            similarity = fuzz.ratio(current["name"], channel["name"])
            if similarity >= threshold:
                group.append(channel)
                to_remove.append(i)
        # 从后往前删除已分组的频道
        for i in reversed(to_remove):
            ungrouped.pop(i)
        groups.append(group)
    return groups

def natural_sort_key(s):
    """自然排序键（支持数字和字母混合排序）"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]

def fetch_and_replace(urls):  
    # 按主分类存储频道 {主分类: {子分类: [频道列表]}}
    category_dict = defaultdict(lambda: defaultdict(list))
    seen_lines = set()  # 全局去重
    
    for url in urls:  
        try:  
            start_time = time.time()  
            response = requests.get(url, timeout=15)  
            elapsed_time = time.time() - start_time  
            print(f"Request to {url} took {elapsed_time:.2f} seconds.")  
  
            if response.status_code == 200:
                response.encoding = 'utf-8'
                content = response.text  

                for line in content.splitlines():  
                    line = line.strip()
                    # 过滤无效行和注释行
                    if not line or any(keyword in line for keyword in 
                                      ['更新时间', '关于', '解锁', '公众号', '软件库']):
                        continue
                    # 清理特殊字符
                    processed_line = line.replace('_', '').replace('??', '')
                    if not processed_line or processed_line in seen_lines:
                        continue
                    seen_lines.add(processed_line)

                    # 解析频道名和URL（假设格式为"名称, url"）
                    if ',' in processed_line:
                        name_part, url_part = processed_line.split(',', 1)
                        channel_name = name_part.strip()
                        channel_url = url_part.strip()
                        
                        # 获取主分类
                        main_category = get_category(channel_name)
                        # 暂存到主分类下（后续进行子分类）
                        category_dict[main_category].append({
                            "name": channel_name,
                            "url": channel_url
                        })
  
            else:  
                print(f"Failed to retrieve {url} with status code {response.status_code}.")  
  
        except requests.exceptions.Timeout:  
            print(f"Request to {url} timed out.")  
        except requests.exceptions.RequestException as e:  
            print(f"Error requesting {url}: {e}")  

    # 处理子分类（相似频道分组）并排序
    final_channels = defaultdict(list)
    for main_cat, channels in category_dict.items():
        # 按相似性分组（子分类）
        similar_groups = group_similar_channels(channels)
        # 对每个子组排序并添加到最终结果
        for group in similar_groups:
            # 用组内第一个频道名作为子分类名（可简化为"主分类-子组"）
            sub_cat = group[0]["name"] if group else "未命名"
            # 按自然排序对组内频道排序
            sorted_group = sorted(group, key=lambda x: natural_sort_key(x["name"]))
            final_channels[main_cat].extend([
                (f"{main_cat}-{sub_cat}", ch["name"], ch["url"]) 
                for ch in sorted_group
            ])

    # 保存结果
    timestamp = time.strftime("%Y%m%d%H%M%S") 
    notice = "注意事项,#genre#\n"+timestamp+"仅供测试自用如有侵权请通知,https://gh.tryxd.cn/https://raw.githubusercontent.com/alantang1977/X/main/Pictures/Robot.mp4\n" 
    
    with open(f'my.txt', 'w', encoding='UTF-8') as file:
        file.write(notice)
        # 按主分类排序输出
        for main_cat in sorted(final_channels.keys()):
            file.write(f"\n{main_cat},#genre#\n")  # 主分类标题
            # 输出该分类下的所有频道
            for sub_cat, name, url in final_channels[main_cat]:
                file.write(f"{name}, {url}\n")
  
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
