import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import schedule
import time
import random

# Danh sách các mục (các section trên kenh14.vn)
sections = [
    {'name': 'Star', 'url': 'https://kenh14.vn/star.chn'},
    {'name': 'Cine', 'url': 'https://kenh14.vn/cine.chn'},
    {'name': 'Musik', 'url': 'https://kenh14.vn/musik.chn'},
    {'name': 'Beauty & Fashion', 'url': 'https://kenh14.vn/beauty-fashion.chn'},
    {'name': 'Đời sống', 'url': 'https://kenh14.vn/doi-song.chn'},
    {'name': 'Money-Z', 'url': 'https://kenh14.vn/money-z.chn'},
    {'name': 'Ăn - Quậy - Đi', 'url': 'https://kenh14.vn/an-quay-di.chn'},
    {'name': 'Sức khỏe', 'url': 'https://kenh14.vn/suc-khoe.chn'},
    {'name': 'Tek-life', 'url': 'https://kenh14.vn/tek-life.chn'},
    {'name': 'Học đường', 'url': 'https://kenh14.vn/hoc-duong.chn'},
    {'name': 'Xem Mua Lưu', 'url': 'https://kenh14.vn/xem-mua-luu.chn'},
    {'name': 'Video', 'url': 'https://kenh14.vn/video.chn'}
]

# Hàm lấy tin tức từ từng mục với retry và delay
def lay_tin_tuc():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://kenh14.vn/'
    }
    all_data = []

    for section in sections:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(section['url'], headers=headers, timeout=20)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                articles = soup.find_all('li', class_=lambda x: x and ('news' in x or 'item' in x or 'knswli' in x))
                if len(articles) < 5:
                    articles = soup.find_all('div', class_=lambda x: x and ('news' in x or 'story' in x))

                print(f"Tìm thấy {len(articles)} bài viết từ mục {section['name']}")

                for article in articles:
                    try:
                        title_tag = article.find('h3', class_=lambda x: x and 'title' in x)
                        if not title_tag:
                            title_tag = article.find('h2') or article.find('a', href=True)
                        title = title_tag.get_text(strip=True) if title_tag else 'Không có tiêu đề'

                        desc_tag = article.find(lambda tag: tag.name in ['div', 'p', 'span']
                                        and tag.get('class')
                                        and any('sapo' in c or 'desc' in c or 'summary' in c for c in tag.get('class')))
                        if not desc_tag or len(desc_tag.get_text(strip=True)) < 20:
                            link_tag = article.find('a', href=True, title=True)
                            desc = link_tag['title'].strip() if link_tag and link_tag.get('title') else 'Không có mô tả'
                        else:
                            desc = desc_tag.get_text(strip=True)

                        link_tag = article.find('a', href=True)
                        link = link_tag['href'] if link_tag else ''
                        if link and not link.startswith('http'):
                            link = 'https://kenh14.vn' + link

                        img_tag = article.find('img', attrs={'src': True})
                        img = img_tag['src'] if img_tag and 'src' in img_tag.attrs else 'Không có hình'

                        all_data.append({
                            'Mục': section['name'],
                            'Tiêu đề': title,
                            'Mô tả': desc,
                            'Hình ảnh': img,
                            'Link': link
                        })

                    except Exception as e:
                        print(f"Lỗi lấy bài từ {section['name']}: {e}")
                        continue

                break

            except requests.RequestException as e:
                print(f"Lỗi lấy trang web {section['name']} (lần {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    wait_time = random.uniform(5, 10)
                    print(f"Đợi {wait_time:.2f} giây trước khi thử lại...")
                    time.sleep(wait_time)
                continue
            except Exception as e:
                print(f"Lỗi khác từ {section['name']}: {e}")
                break

        time.sleep(random.uniform(2, 5))

    if all_data:
        df = pd.DataFrame(all_data)
        file_name = f"kenh14_all_sections_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        df.to_excel(file_name, index=False, engine='openpyxl')
        print(f"Đã lưu file: {file_name}")
    else:
        print("Không lấy được bài nào, kiểm tra lại!")

# Lấy tin tức ngay khi chạy code
#lay_tin_tuc()

# Lên lịch chạy hằng ngày lúc 6h sáng
schedule.every().day.at("23:25").do(lay_tin_tuc)

print("🔄 Đang chạy lịch hằng ngày. Nhấn Ctrl+C để dừng.")

while True:
    schedule.run_pending()
    time.sleep(60)